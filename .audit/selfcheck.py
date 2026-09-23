"""Self-verification receipt, discharging CRUCIBLE contract Phase 1 item 11.

Item 11 makes `crucible selfcheck` the one command that runs every Phase 2
deterministic self-verification check, the formatter, the linter, the type
checker, the tests, the negative controls, the positive-fire fixtures of
verifier principle 7, the self-fuzz, the scope approval refusal proof, and the
fingerprint drift proof, and emits .audit/selfcheck.yaml with one row per check
carrying its argv, exit code, elapsed seconds, and both-halves outcome as
exactly clean, fired, inert, or unrun.

The both-halves discipline is the whole point. Verifier principle 7 holds that a
required deterministic check proving only that it stays clean is itself a
coverage gap, and that a required check which cannot fire at all is not a gap
but a broken instrument capping the gate at BLOCK. So every row here records two
independent observations: the check stays clean on material that carries no
defect, and the same check produces its finding on material that carries a
planted one. A row that can only demonstrate the clean half is recorded as inert
rather than as a pass, and core.SelfcheckRow derives that verdict rather than
this module asserting it.

Rows whose fixtures do not yet exist are recorded as unrun. That is deliberate
and it is not a softening: an unrun required check caps at BLOCK exactly as an
inert one does, so the receipt states the truth that the check has not been
demonstrated rather than omitting the row and leaving the reader to assume
coverage that was never established.

The negative-control roster is data-driven. When
.audit/fixtures/negative/manifest.yaml is authored under contract item 12 each
declared control resolves through it; until then each control identifier still
emits its own row so the receipt names precisely which demonstrations are owed.
"""

from __future__ import annotations

import datetime
import tempfile
import time
from pathlib import Path
from typing import Any

import yaml

import core
import negcontrol
import normalize
import recon
import rewardfixtures
from core import Disposition, Outcome, SelfcheckRow

SELFCHECK_SCHEMA = "crucible.selfcheck/v1"

NEGATIVE_MANIFEST_SUBPATH = "fixtures/negative/manifest.yaml"
REWARD_MANIFEST_SUBPATH = "fixtures/reward/v1/manifest.yaml"

RUFF_SPEC = "ruff"
TYPE_CHECKER_SPEC = "mypy==1.14.1"

NEGATIVE_CONTROLS: tuple[tuple[str, str], ...] = (
    (
        "NC-OMITTED-ISSUE",
        "A report omitting an issue the scanner recorded must be refused.",
    ),
    (
        "NC-FABRICATED-SPAN",
        "A finding citing a span absent from the cited artifact must be refused.",
    ),
    (
        "NC-BLOCKED-RUN-CITED",
        "A blocked tool run cited as evidence must be refused.",
    ),
    (
        "NC-EMPTY-ALL-CLEAR",
        "An empty all-clear report over a surface carrying issues must be refused.",
    ),
    (
        "NC-WRONG-CVSS",
        "A severity that does not recompute from its declared vector must be refused.",
    ),
    (
        "NC-DIRTY-TREE",
        "A dirty tree presented as clean must be refused.",
    ),
    (
        "NC-UNPINNED-DATABASE",
        "An unpinned scanner database cited as evidence must be refused.",
    ),
    (
        "NC-VERIFIER-FUZZ",
        "Malformed findings input must fail closed rather than parse into a pass.",
    ),
    (
        "NC-EXCLUDED-ANCESTOR",
        "An excluded ancestor behind a clean direct parent must still be found.",
    ),
    (
        "NC-WHITEOUTED-OBJECT-DB",
        "A Git object database surviving only in a whiteouted lower layer must be found.",
    ),
    (
        "NC-FREEZE-PARTIAL",
        "An event timestamp preceding one freeze row while clearing the others must fire.",
    ),
    (
        "NC-NEARDUP-CROSS-REPOSITORY",
        "A near duplicate expressed through a different repository and issue must fire.",
    ),
    (
        "NC-EMPTY-SUBMISSION-RESOLVES",
        "An empty submission that resolves a fail-to-pass target must fire.",
    ),
    (
        "NC-CARRIER-UNRECONCILED",
        "A provenance carrier that parses but does not reconcile must fire.",
    ),
    (
        "NC-CARRIER-UNKNOWN-KEY",
        "A provenance carrier carrying an unknown key must fire.",
    ),
    (
        "NC-BINDING-DIVERGENT",
        "A committed binding block diverging from the recomputed block must fire.",
    ),
    (
        "NC-NEARDUP-REVIEW-BAND",
        "A bound borderline fixture must enter the near duplicate review band.",
    ),
    (
        "NC-NEARDUP-CLEAN",
        "A measured non neighbour must stay clean under the near duplicate screen.",
    ),
    (
        "NC-ATTESTATION-VALID",
        "A valid source attestation must be accepted by exclusion and freeze.",
    ),
    (
        "NC-ATTESTATION-MISMATCH",
        "An attested value contradicting its declaration must be retained at BLOCK.",
    ),
    (
        "NC-ATTESTATION-UNAVAILABLE",
        "An unresolved attestation must emit a coverage gap at HOLD.",
    ),
    (
        "NC-BUDGET-PLANTED",
        "Each budget instrument must fire on its planted positive fixture.",
    ),
    (
        "NC-BUDGET-CLEAN",
        "Each budget instrument must stay clean on its clean fixture.",
    ),
    (
        "NC-ROOT-DRIFT-PLANTED",
        "A bundle passing under the shipped root and failing under the effective root must fire.",
    ),
    (
        "NC-ROOT-DRIFT-CLEAN",
        "A bundle passing under the effective root must stay clean.",
    ),
    (
        "NC-ROOT-DRIFT-UNRESOLVED",
        "An unresolved shipped-under root must emit a coverage gap at bare HOLD.",
    ),
)

_LINT_POSITIVE_SOURCE = "import os\n"

_FORMAT_POSITIVE_SOURCE = "x   =    1\ndef  f( a ,b ):\n  return  a+b\n"


def _now() -> str:
    """Emit the receipt instant as RFC 3339 UTC, matching the freshness domain."""
    return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")


def _ascii_text(raw: str) -> str:
    """Keep every emitted byte ASCII, per the house rules."""
    return raw.encode("ascii", "backslashreplace").decode("ascii")


def _internal_argv(name: str) -> list[str]:
    """Record the invocation that reproduces an in-process check."""
    return ["python3", "-c", f"import selfcheck; selfcheck.{name}()"]


def _unrun_row(
    check_id: str,
    instrument: str,
    argv: list[str],
    detail: str,
    *,
    required: bool = True,
) -> SelfcheckRow:
    """Record a check that was not demonstrated, never a silent omission."""
    return SelfcheckRow(
        check_id=check_id,
        instrument=instrument,
        argv=argv,
        exit_code=None,
        elapsed_seconds=0.0,
        clean_half=Outcome.UNRUN,
        positive_half=Outcome.UNRUN,
        required=required,
        detail=_ascii_text(detail),
    )


def _audit_dir(base: Path) -> Path:
    return base / core.AUDIT_DIRNAME


def check_linter(base: Path) -> SelfcheckRow:
    """Prove the linter stays clean on the harness and fires on a planted defect."""
    audit = _audit_dir(base)
    started = time.monotonic()
    clean = core.run_capture(
        [RUFF_SPEC, "check", "."],
        artifact_id="selfcheck-linter-clean",
        cwd=audit,
        timeout=300.0,
    )
    clean_half = Outcome.UNRUN
    detail_parts: list[str] = []
    if clean.blocked_reason is not None:
        detail_parts.append(f"clean half blocked: {clean.blocked_reason}")
    elif clean.exit_code == 0:
        clean_half = Outcome.CLEAN
    else:
        clean_half = Outcome.FIRED
        detail_parts.append("linter reported findings against the harness itself")

    positive_half = Outcome.UNRUN
    with tempfile.TemporaryDirectory() as scratch:
        planted = Path(scratch) / "planted.py"
        planted.write_text(_LINT_POSITIVE_SOURCE, encoding="ascii")
        fired = core.run_capture(
            [RUFF_SPEC, "check", "--select", "F401", "--no-cache", str(planted)],
            artifact_id="selfcheck-linter-positive",
            cwd=audit,
            timeout=300.0,
        )
    if fired.blocked_reason is not None:
        detail_parts.append(f"positive half blocked: {fired.blocked_reason}")
    elif fired.exit_code not in (None, 0) and "F401" in fired.stdout:
        positive_half = Outcome.FIRED
    else:
        positive_half = Outcome.CLEAN
        detail_parts.append("planted unused import did not produce a linter finding")

    elapsed = time.monotonic() - started
    return SelfcheckRow(
        check_id="SC-LINTER",
        instrument="ruff-check",
        argv=[RUFF_SPEC, "check", "."],
        exit_code=clean.exit_code,
        elapsed_seconds=elapsed,
        clean_half=clean_half,
        positive_half=positive_half,
        required=True,
        detail=_ascii_text("; ".join(detail_parts)),
    )


def check_formatter(base: Path) -> SelfcheckRow:
    """Prove the formatter accepts the harness and rejects unformatted bytes."""
    audit = _audit_dir(base)
    started = time.monotonic()
    clean = core.run_capture(
        [RUFF_SPEC, "format", "--check", "."],
        artifact_id="selfcheck-formatter-clean",
        cwd=audit,
        timeout=300.0,
    )
    clean_half = Outcome.UNRUN
    detail_parts: list[str] = []
    if clean.blocked_reason is not None:
        detail_parts.append(f"clean half blocked: {clean.blocked_reason}")
    elif clean.exit_code == 0:
        clean_half = Outcome.CLEAN
    else:
        clean_half = Outcome.FIRED
        detail_parts.append("formatter reported drift against the harness itself")

    positive_half = Outcome.UNRUN
    with tempfile.TemporaryDirectory() as scratch:
        planted = Path(scratch) / "planted.py"
        planted.write_text(_FORMAT_POSITIVE_SOURCE, encoding="ascii")
        fired = core.run_capture(
            [RUFF_SPEC, "format", "--check", "--no-cache", str(planted)],
            artifact_id="selfcheck-formatter-positive",
            cwd=audit,
            timeout=300.0,
        )
    if fired.blocked_reason is not None:
        detail_parts.append(f"positive half blocked: {fired.blocked_reason}")
    elif fired.exit_code not in (None, 0):
        positive_half = Outcome.FIRED
    else:
        positive_half = Outcome.CLEAN
        detail_parts.append("planted unformatted source did not produce formatter drift")

    elapsed = time.monotonic() - started
    return SelfcheckRow(
        check_id="SC-FORMATTER",
        instrument="ruff-format",
        argv=[RUFF_SPEC, "format", "--check", "."],
        exit_code=clean.exit_code,
        elapsed_seconds=elapsed,
        clean_half=clean_half,
        positive_half=positive_half,
        required=True,
        detail=_ascii_text("; ".join(detail_parts)),
    )


def check_type_checker(base: Path) -> SelfcheckRow:
    """Record whether a pinned type checker resolves and demonstrates both halves."""
    audit = _audit_dir(base)
    argv = ["uvx", "--from", TYPE_CHECKER_SPEC, "mypy", "--ignore-missing-imports", "."]
    started = time.monotonic()
    clean = core.run_capture(
        argv,
        artifact_id="selfcheck-typecheck-clean",
        cwd=audit,
        timeout=600.0,
    )
    elapsed = time.monotonic() - started
    if clean.blocked_reason is not None:
        return _unrun_row(
            "SC-TYPE-CHECKER",
            "mypy",
            argv,
            f"type checker did not resolve: {clean.blocked_reason}",
        )
    detail = (
        "type checker clean over the harness"
        if clean.exit_code == 0
        else "type checker reported findings over the harness, recorded and not suppressed"
    )

    clean_half = Outcome.UNRUN
    positive_half = Outcome.UNRUN
    positive_detail = "planted type-error fixture did not run"
    with tempfile.TemporaryDirectory() as raw:
        fixtures = Path(raw)
        (fixtures / "clean_fixture.py").write_text(
            "def widen(value: int) -> str:\n    return str(value)\n", encoding="utf-8"
        )
        (fixtures / "planted.py").write_text(
            "def widen(value: int) -> str:\n    return value\n", encoding="utf-8"
        )
        quiet = core.run_capture(
            [
                "uvx",
                "--from",
                TYPE_CHECKER_SPEC,
                "mypy",
                "--ignore-missing-imports",
                "clean_fixture.py",
            ],
            artifact_id="selfcheck-typecheck-clean-fixture",
            cwd=fixtures,
            timeout=600.0,
        )
        probe = core.run_capture(
            ["uvx", "--from", TYPE_CHECKER_SPEC, "mypy", "--ignore-missing-imports", "planted.py"],
            artifact_id="selfcheck-typecheck-planted",
            cwd=fixtures,
            timeout=600.0,
        )
    if quiet.blocked_reason is None:
        clean_half = Outcome.CLEAN if quiet.exit_code == 0 else Outcome.FIRED
    if probe.blocked_reason is not None:
        positive_detail = f"planted type fixture blocked: {probe.blocked_reason}"
    elif probe.exit_code == 0:
        positive_half = Outcome.CLEAN
        positive_detail = "a return type violating its annotation was not reported"
    else:
        positive_half = Outcome.FIRED
        positive_detail = "a return type violating its annotation was reported as planted"

    return SelfcheckRow(
        check_id="SC-TYPE-CHECKER",
        instrument="mypy",
        argv=argv,
        exit_code=clean.exit_code,
        elapsed_seconds=elapsed,
        clean_half=clean_half,
        positive_half=positive_half,
        required=True,
        detail=_ascii_text("; ".join(part for part in (detail, positive_detail) if part)),
    )


def check_tests(base: Path) -> SelfcheckRow:
    """Run the harness test suite, recording an absent suite as unrun."""
    audit = _audit_dir(base)
    suite = audit / "tests"
    argv = ["python3", "-m", "pytest", "-q", "tests"]
    if not suite.is_dir():
        return _unrun_row(
            "SC-TESTS",
            "pytest",
            argv,
            "no test suite authored at .audit/tests, contract item 12 still owed",
        )
    started = time.monotonic()
    result = core.run_capture(
        argv,
        artifact_id="selfcheck-tests",
        cwd=audit,
        timeout=900.0,
    )
    elapsed = time.monotonic() - started
    if result.blocked_reason is not None:
        return _unrun_row(
            "SC-TESTS",
            "pytest",
            argv,
            f"test runner blocked: {result.blocked_reason}",
        )
    clean_half = Outcome.CLEAN if result.exit_code == 0 else Outcome.FIRED

    planted = core.run_capture(
        ["python3", "-m", "pytest", "-q", "--version"],
        artifact_id="selfcheck-tests-planted-probe",
        cwd=audit,
        timeout=120.0,
    )
    positive_half = Outcome.UNRUN
    positive_detail = "planted-failure probe did not run"
    if planted.blocked_reason is None:
        with tempfile.TemporaryDirectory() as raw:
            planted_dir = Path(raw) / "tests"
            planted_dir.mkdir(parents=True)
            (planted_dir / "test_planted.py").write_text(
                "def test_planted_failure():\n    assert 1 == 2\n", encoding="utf-8"
            )
            outcome = core.run_capture(
                ["python3", "-m", "pytest", "-q", "tests"],
                artifact_id="selfcheck-tests-planted",
                cwd=Path(raw),
                timeout=300.0,
            )
        if outcome.blocked_reason is not None:
            positive_detail = f"planted-failure probe blocked: {outcome.blocked_reason}"
        elif outcome.exit_code == 0:
            positive_detail = "a planted failing test did not fail the runner"
            positive_half = Outcome.CLEAN
        else:
            positive_half = Outcome.FIRED
            positive_detail = "a planted failing test failed the runner as expected"

    return SelfcheckRow(
        check_id="SC-TESTS",
        instrument="pytest",
        argv=argv,
        exit_code=result.exit_code,
        elapsed_seconds=elapsed,
        clean_half=clean_half,
        positive_half=positive_half,
        required=True,
        detail=_ascii_text(positive_detail),
    )


def _scope_approval_refusal(base: Path) -> tuple[Outcome, Outcome, str]:
    """Demonstrate both halves of the Phase 2 item 2 approval enforcement proof."""
    live = recon.scope_binding(base)
    detail_parts: list[str] = []
    clean_half = Outcome.UNRUN
    if not live.get("scope_present") or not live.get("approved_present"):
        detail_parts.append("clean half unavailable: scope or approval absent in the live tree")
    elif live.get("matches"):
        clean_half = Outcome.CLEAN
    else:
        clean_half = Outcome.FIRED
        detail_parts.append("live tree does not satisfy its own approval binding")

    positive_half = Outcome.UNRUN
    scope_path = _audit_dir(base) / core.SCOPE_FILENAME
    approved_path = _audit_dir(base) / core.SCOPE_APPROVED_FILENAME
    if scope_path.is_file() and approved_path.is_file():
        with tempfile.TemporaryDirectory() as scratch:
            planted_root = Path(scratch)
            planted_audit = planted_root / core.AUDIT_DIRNAME
            planted_audit.mkdir(parents=True)
            mutated = scope_path.read_bytes() + b"\nselfcheck_planted_mutation: true\n"
            (planted_audit / core.SCOPE_FILENAME).write_bytes(mutated)
            (planted_audit / core.SCOPE_APPROVED_FILENAME).write_bytes(approved_path.read_bytes())
            mismatched = recon.scope_binding(planted_root)
            missing_root = Path(scratch) / "missing"
            missing_audit = missing_root / core.AUDIT_DIRNAME
            missing_audit.mkdir(parents=True)
            (missing_audit / core.SCOPE_FILENAME).write_bytes(scope_path.read_bytes())
            absent = recon.scope_binding(missing_root)
        refused_mismatch = mismatched.get("matches") is False
        refused_absent = absent.get("approved_present") is False and not absent.get("matches")
        if refused_mismatch and refused_absent:
            positive_half = Outcome.FIRED
        else:
            positive_half = Outcome.CLEAN
            detail_parts.append(
                "planted mismatch or missing approval was not refused by the binding check"
            )
    else:
        detail_parts.append("positive half unavailable: scope bytes absent")
    return clean_half, positive_half, "; ".join(detail_parts)


def check_scope_approval(base: Path) -> SelfcheckRow:
    """Prove scope approval enforcement refuses a missing or mismatched approval."""
    started = time.monotonic()
    clean_half, positive_half, detail = _scope_approval_refusal(base)
    elapsed = time.monotonic() - started
    return SelfcheckRow(
        check_id="SC-SCOPE-APPROVAL-REFUSAL",
        instrument="recon.scope_binding",
        argv=_internal_argv("_scope_approval_refusal"),
        exit_code=0,
        elapsed_seconds=elapsed,
        clean_half=clean_half,
        positive_half=positive_half,
        required=True,
        detail=_ascii_text(detail),
    )


def _fingerprint_drift() -> tuple[Outcome, Outcome, str]:
    """Demonstrate both halves of the Phase 2 item 4 fingerprint drift proof.

    The drift this proves survivable is the drift the contract intends: the
    source line moving, so the gutter carries different numbers, and the
    surrounding formatting changing through indentation, trailing whitespace,
    and blank lines. It is not a claim that any edit whatever preserves the
    fingerprint, and the positive half exists to prove the fingerprint does move
    when the anchored artifact genuinely differs.
    """
    original_excerpt = "def handler(request):\n    return compute(request)\n"
    reformatted_excerpt = (
        "  312|         def handler(request):   \n"
        "  313| \n"
        "  314|                 return compute(request)\t\n"
    )
    original = normalize.NormalizedIssue(
        rule="crucible-python-eval-exec",
        anchor=normalize.Anchor(
            path="solution/recompute.py",
            symbol="handler",
            excerpt=original_excerpt,
        ),
        severity=core.Severity.HIGH,
        message="planted",
        tool="selfcheck",
    )
    drifted = normalize.NormalizedIssue(
        rule="crucible-python-eval-exec",
        anchor=normalize.Anchor(
            path="solution/recompute.py",
            symbol="handler",
            excerpt=reformatted_excerpt,
        ),
        severity=core.Severity.HIGH,
        message="planted",
        tool="selfcheck",
    )
    moved = normalize.NormalizedIssue(
        rule="crucible-python-eval-exec",
        anchor=normalize.Anchor(
            path="solution/other.py",
            symbol="handler",
            excerpt=original_excerpt,
        ),
        severity=core.Severity.HIGH,
        message="planted",
        tool="selfcheck",
    )
    detail_parts: list[str] = []
    survived, survived_detail = normalize.survives_drift([original], [drifted])
    clean_half = Outcome.CLEAN if survived else Outcome.FIRED
    if not survived:
        detail_parts.append(f"reformatting lost the fingerprint: {survived_detail}")
    changed, changed_detail = normalize.survives_drift([original], [moved])
    if changed:
        positive_half = Outcome.CLEAN
        detail_parts.append("a genuinely different anchor did not move the fingerprint")
    else:
        positive_half = Outcome.FIRED
        del changed_detail
    return clean_half, positive_half, "; ".join(detail_parts)


def check_fingerprint_drift(base: Path) -> SelfcheckRow:
    """Prove normalized fingerprints survive formatting drift and only that."""
    del base
    started = time.monotonic()
    clean_half, positive_half, detail = _fingerprint_drift()
    elapsed = time.monotonic() - started
    return SelfcheckRow(
        check_id="SC-FINGERPRINT-DRIFT",
        instrument="normalize.survives_drift",
        argv=_internal_argv("_fingerprint_drift"),
        exit_code=0,
        elapsed_seconds=elapsed,
        clean_half=clean_half,
        positive_half=positive_half,
        required=True,
        detail=_ascii_text(detail),
    )


def _self_fuzz() -> tuple[Outcome, Outcome, str]:
    """Feed malformed values to the closed constructors and require refusal."""
    import evidence
    from registry import Category, EvidenceClass, Instrument

    detail_parts: list[str] = []
    accepted = True
    try:
        evidence.LedgerRow(
            threat=evidence.REWARD_THREATS[0],
            channel=evidence.CAPABILITY_CHANNELS[0],
            boundary=evidence.REWARD_BOUNDARIES[0],
            resolution="gap",
            statement="well formed",
        )
        core.CoverageGap(
            gap_id="SELFCHECK-WELL-FORMED",
            instrument="selfcheck",
            surface="harness_code",
            reason="well-formed",
            caps=Disposition.HOLD,
            statement="well formed",
        )
        Instrument(
            name="SELFCHECK-WELL-FORMED",
            category=Category.RECON,
            binary="",
            ecosystems=("*",),
            timeout_seconds=1,
            required_conditions=(),
            critical_capability="none",
            evidence_class=EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
        )
    except Exception as error:
        accepted = False
        detail_parts.append(f"well-formed value refused: {error}")
    clean_half = Outcome.CLEAN if accepted else Outcome.FIRED

    refusals = 0
    expected = 5
    try:
        evidence.LedgerRow(
            threat="not-a-declared-threat",
            channel=evidence.CAPABILITY_CHANNELS[0],
            boundary=evidence.REWARD_BOUNDARIES[0],
            resolution="gap",
        )
    except Exception:
        refusals += 1
    try:
        evidence.LedgerRow(
            threat=evidence.REWARD_THREATS[0],
            channel=evidence.CAPABILITY_CHANNELS[0],
            boundary=evidence.REWARD_BOUNDARIES[0],
            resolution="not_applicable",
        )
    except Exception:
        refusals += 1
    try:
        core.CoverageGap(
            gap_id="SELFCHECK-MALFORMED",
            instrument="selfcheck",
            surface="harness_code",
            reason="malformed",
            caps=Disposition.SHIP,
            statement="a gap may never cap at SHIP",
        )
    except Exception:
        refusals += 1
    try:
        Instrument(
            name="SELFCHECK-MALFORMED-CAP",
            category=Category.RECON,
            binary="",
            ecosystems=("*",),
            timeout_seconds=1,
            required_conditions=(),
            critical_capability="none",
            evidence_class=EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.SHIP,
        )
    except Exception:
        refusals += 1
    try:
        Instrument(
            name="SELFCHECK-MALFORMED-PARSER",
            category=Category.RECON,
            binary="",
            ecosystems=("*",),
            timeout_seconds=1,
            required_conditions=(),
            critical_capability="none",
            evidence_class=EvidenceClass.SET_RELATION,
            requires_parser=True,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
        )
    except Exception:
        refusals += 1

    severity_failed = core.normalize_severity("not-a-severity") is not core.Severity.MEDIUM
    if severity_failed:
        detail_parts.append("unknown severity did not fail closed to MEDIUM")

    if refusals == expected and not severity_failed:
        positive_half = Outcome.FIRED
    else:
        positive_half = Outcome.CLEAN
        detail_parts.append(f"{refusals} of {expected} malformed values refused")
    return clean_half, positive_half, "; ".join(detail_parts)


def check_self_fuzz(base: Path) -> SelfcheckRow:
    """Prove the closed constructors accept valid values and refuse malformed ones."""
    del base
    started = time.monotonic()
    clean_half, positive_half, detail = _self_fuzz()
    elapsed = time.monotonic() - started
    return SelfcheckRow(
        check_id="SC-SELF-FUZZ",
        instrument="core.and.evidence.constructors",
        argv=_internal_argv("_self_fuzz"),
        exit_code=0,
        elapsed_seconds=elapsed,
        clean_half=clean_half,
        positive_half=positive_half,
        required=True,
        detail=_ascii_text(detail),
    )


def _load_manifest(path: Path) -> dict[str, Any]:
    """Read a fixture manifest, failing closed to an empty mapping."""
    if not path.is_file():
        return {}
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, yaml.YAMLError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _drive_control(base: Path, entry: dict[str, Any]) -> dict[str, Any]:
    """Dispatch one declared control to the runner its kind names."""
    control_id = str(entry.get("id"))
    kind = str(entry.get("kind") or "")
    expect = str(entry.get("expect") or "")
    if kind == "verify":
        return negcontrol.run_verify_control(base, control_id, expect)
    if kind == "source-integrity":
        return negcontrol.run_source_integrity_control(base)
    if kind == "attestation":
        return negcontrol.run_attestation_control(base, control_id, expect)
    if kind == "budget":
        return negcontrol.run_budget_control(base, control_id)
    if kind.startswith("contamination:"):
        return negcontrol.run_contamination_control(base, control_id, kind.split(":", 1)[1], expect)
    return {
        "clean": Outcome.UNRUN,
        "positive": Outcome.UNRUN,
        "detail": f"no runner is registered for control kind {kind!r}",
    }


def check_negative_controls(base: Path) -> list[SelfcheckRow]:
    """Drive every declared negative control over both halves of its fixture.

    A control the manifest marks unrun is emitted with its recorded reason
    rather than silently dropped. An unrun required control caps the gate
    exactly as an inert one does, so recording the reason is what lets a reader
    distinguish a check that has not been built from one that has been built and
    does not work.
    """
    manifest_path = _audit_dir(base) / NEGATIVE_MANIFEST_SUBPATH
    manifest = _load_manifest(manifest_path)
    declared = manifest.get("controls")
    by_id: dict[str, Any] = {}
    if isinstance(declared, list):
        for entry in declared:
            if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                by_id[entry["id"]] = entry

    statements = dict(NEGATIVE_CONTROLS)
    identifiers = list(statements)
    identifiers.extend(key for key in by_id if key not in statements)

    rows: list[SelfcheckRow] = []
    for control_id in identifiers:
        argv = _internal_argv(f"_negative_control:{control_id}")
        statement = statements.get(control_id, "")
        entry = by_id.get(control_id)
        if entry is None:
            rows.append(
                _unrun_row(
                    f"SC-{control_id}",
                    "negative-control",
                    argv,
                    f"{statement} No fixture declared at {NEGATIVE_MANIFEST_SUBPATH}.",
                )
            )
            continue
        if str(entry.get("status")) == "unrun":
            rows.append(
                _unrun_row(
                    f"SC-{control_id}",
                    "negative-control",
                    argv,
                    f"{statement} {entry.get('unrun_reason') or 'recorded as unrun'}".strip(),
                )
            )
            continue
        started = time.monotonic()
        outcome = _drive_control(base, entry)
        elapsed = time.monotonic() - started
        rows.append(
            SelfcheckRow(
                check_id=f"SC-{control_id}",
                instrument="negative-control",
                argv=argv,
                exit_code=0,
                elapsed_seconds=round(elapsed, 3),
                clean_half=outcome["clean"],
                positive_half=outcome["positive"],
                required=True,
                detail=f"{statement} {outcome['detail']}".strip(),
            )
        )
    return rows


def check_reward_fixtures(base: Path) -> list[SelfcheckRow]:
    """Drive every contract item 12d reward subject over both halves of its fixture.

    One row per subject rather than one row for the suite, because a suite-level
    row would let a subject that cannot fire hide behind subjects that can, and
    the receipt exists precisely to name which demonstrations stand.
    """
    manifest_path = _audit_dir(base) / REWARD_MANIFEST_SUBPATH
    if not manifest_path.is_file():
        return [
            _unrun_row(
                "SC-REWARD-FIXTURES",
                "reward-fixtures",
                _internal_argv("_reward_fixtures"),
                f"no reward fixture manifest at {REWARD_MANIFEST_SUBPATH}, contract item 12d owed",
            )
        ]
    rows: list[SelfcheckRow] = []
    for outcome in rewardfixtures.run_all(base):
        subject = str(outcome["subject"])
        started = time.monotonic()
        rows.append(
            SelfcheckRow(
                check_id=f"SC-{subject}",
                instrument=f"reward-{outcome['kind']}",
                argv=_internal_argv(f"_reward_fixture:{subject}"),
                exit_code=0,
                elapsed_seconds=round(time.monotonic() - started, 3),
                clean_half=outcome["clean"],
                positive_half=outcome["positive"],
                required=True,
                detail=str(outcome["detail"]),
            )
        )
    return rows


def check_principle_seven_fixtures(base: Path) -> SelfcheckRow:
    """Aggregate the standing of every required Bucket-D both-halves demonstration.

    This row reports coverage of the roster rather than running a check of its
    own. It resolves fired only when every subject the two fixture manifests
    declare has demonstrated both halves, because principle 7 makes the gate
    turn on the weakest required check rather than on how many checks passed.
    A subject declared unrun keeps this row unrun, which caps at BLOCK exactly
    as the unrun subject itself does and refuses to let breadth of coverage
    stand in for completeness of it.
    """
    fixtures = _audit_dir(base) / "fixtures"
    argv = _internal_argv("_principle_seven_fixtures")
    if not fixtures.is_dir():
        return _unrun_row(
            "SC-PRINCIPLE-SEVEN-FIXTURES",
            "principle-seven",
            argv,
            "no .audit/fixtures tree, so no required Bucket-D atom has demonstrated both halves",
        )

    negative = _load_manifest(_audit_dir(base) / NEGATIVE_MANIFEST_SUBPATH)
    reward_manifest = _load_manifest(_audit_dir(base) / REWARD_MANIFEST_SUBPATH)
    declared = [
        entry
        for entry in (negative.get("controls") or [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    ]
    unrun = sorted(str(entry["id"]) for entry in declared if str(entry.get("status")) == "unrun")
    demonstrated = len(declared) - len(unrun)
    reward_subjects = len(reward_manifest.get("atoms") or []) + len(
        reward_manifest.get("derivations") or []
    )

    detail = (
        f"{demonstrated} of {len(declared)} negative controls and {reward_subjects} reward "
        f"subjects demonstrate both halves; unrun: {', '.join(unrun) or 'none'}"
    )
    if unrun or not reward_subjects:
        return _unrun_row("SC-PRINCIPLE-SEVEN-FIXTURES", "principle-seven", argv, detail)
    return SelfcheckRow(
        check_id="SC-PRINCIPLE-SEVEN-FIXTURES",
        instrument="principle-seven",
        argv=argv,
        exit_code=0,
        elapsed_seconds=0.0,
        clean_half=Outcome.CLEAN,
        positive_half=Outcome.FIRED,
        required=True,
        detail=detail,
    )


def run_all(base: Path | None = None) -> list[SelfcheckRow]:
    """Run every self-verification check and return one row each, per item 11."""
    root = base or core.project_root()
    rows: list[SelfcheckRow] = [
        check_linter(root),
        check_formatter(root),
        check_type_checker(root),
        check_tests(root),
        check_scope_approval(root),
        check_fingerprint_drift(root),
        check_self_fuzz(root),
        check_principle_seven_fixtures(root),
    ]
    rows.extend(check_reward_fixtures(root))
    rows.extend(check_negative_controls(root))
    rows.sort(key=lambda row: row.check_id)
    return rows


def write(rows: list[SelfcheckRow], base: Path | None = None) -> Path:
    """Emit .audit/selfcheck.yaml, one row per check, emoji-free and ASCII."""
    root = base or core.project_root()
    path = _audit_dir(root) / core.SELFCHECK_FILENAME
    disposition = core.cap_all(row.caps for row in rows)
    broken = sorted(row.check_id for row in rows if row.outcome in core.BROKEN_OUTCOMES)
    document = {
        "schema": SELFCHECK_SCHEMA,
        "generated_at": _now(),
        "row_count": len(rows),
        "disposition": disposition.token,
        "broken_required_checks": broken,
        "rows": [row.to_row() for row in rows],
    }
    payload = yaml.safe_dump(
        document,
        sort_keys=True,
        default_flow_style=False,
        allow_unicode=False,
        width=100,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="ascii")
    return path


__all__ = [
    "NEGATIVE_CONTROLS",
    "NEGATIVE_MANIFEST_SUBPATH",
    "REWARD_MANIFEST_SUBPATH",
    "SELFCHECK_SCHEMA",
    "check_fingerprint_drift",
    "check_formatter",
    "check_linter",
    "check_negative_controls",
    "check_principle_seven_fixtures",
    "check_reward_fixtures",
    "check_scope_approval",
    "check_self_fuzz",
    "check_tests",
    "check_type_checker",
    "run_all",
    "write",
]
