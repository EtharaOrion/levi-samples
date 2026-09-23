"""Pinned scanner family, discharging the CRUCIBLE contract step 8a scanner sweep.

Phase 1 item 5 of the contract forbids an unpinned scanner database and forbids
``semgrep --config auto`` outright, and Phase 1 item 4 requires every tool to be
declared in the registry before it is invoked. This module is where both rules
become executable: it reads the six configs already authored under
.audit/scanner-configs/, registers one instrument per config, and runs only the
configs that declare ``runs: true``.

Five of the six configs declare ``runs: false`` because their vulnerability feeds
cannot be pinned offline or their binaries are absent from this host. A scanner
that does not run is not a clean scanner, so each of those emits exactly one
D-COVERAGE-GAP carrying the identifier the config itself declares. The contract's
rule that a clean grounding result is never evidence of correctness is encoded
here as the standing rule: DEMONSTRATED_COVERAGE is reachable only when the
scanner actually executed, produced parseable output, and had a nonempty target
set to execute over.

A nonzero exit is tool-specific evidence and never an automatic failure. semgrep
exits 1 when it has findings and also exits 1 when its own interpreter fails to
import, so this module distinguishes the two by whether stdout parses as a JSON
object carrying a ``results`` key, not by the exit code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

import core
import recon
from core import (
    Bucket,
    CoverageGap,
    Disposition,
    Finding,
    InstrumentResult,
    Standing,
)
from normalize import Anchor, NormalizedIssue
from registry import REGISTRY, Category, EvidenceClass, Instrument

SCANNER_CONFIG_DIRNAME = "scanner-configs"
SCANNER_CONFIG_SCHEMA = "crucible.scanner-config/v1"

SCANNER_NAMES = ("gitleaks", "grype", "hadolint", "osv-scanner", "semgrep", "trivy")

TARGET_PATTERNS = (
    "solution/*.py",
    "solution/*.sh",
    "tests/*.py",
    "tests/graded/*.sh",
    "environment/*.sh",
)

EXCLUDED_ROOT_PARTS = ("trinity", ".audit")
EXCLUDED_FIXTURE_PART = "fixtures"

SEMGREP_NAME = "semgrep"
SEMGREP_BLOCKED_GAP_ID = "D-SCANNER-SEMGREP-BLOCKED"
SEMGREP_NO_TARGETS_GAP_ID = "D-SCANNER-SEMGREP-NO-TARGETS"
SEMGREP_FORBIDDEN_FINDING_ID = "D-SCANNER-SEMGREP-FORBIDDEN-ARGV"
CONFIG_ABSENT_GAP_ID = "D-SCANNER-CONFIG-ABSENT"
CONFIG_SCHEMA_GAP_ID = "D-SCANNER-CONFIG-SCHEMA"
INTERNAL_ERROR_GAP_ID = "D-SCANNER-INTERNAL-ERROR"

SCANNER_SURFACE = "bundle_scripts"
SCANNER_CRITICAL_CLASS = "scanner-static-analysis"

_REGISTRY_DECLARATIONS: tuple[dict[str, Any], ...] = (
    {
        "name": "gitleaks",
        "binary": "gitleaks",
        "ecosystems": ("*",),
        "timeout_seconds": 900.0,
        "required_conditions": ("binary-present", "rule-file-pinned"),
        "critical_capability": "committed-secret-detection",
        "database_pin": ".audit/scanner-configs/rules/gitleaks.toml",
        "notes": "Go binary, unresolvable through the uv toolchain this harness is confined to.",
    },
    {
        "name": "grype",
        "binary": "grype",
        "ecosystems": ("*",),
        "timeout_seconds": 1200.0,
        "required_conditions": ("binary-present", "vulnerability-feed-pinned"),
        "critical_capability": "container-vulnerability-enumeration",
        "database_pin": "",
        "notes": "Remote vulnerability feed, unpinnable offline, so the instrument declines to run.",
    },
    {
        "name": "hadolint",
        "binary": "hadolint",
        "ecosystems": ("docker",),
        "timeout_seconds": 300.0,
        "required_conditions": ("binary-present", "rule-selection-pinned"),
        "critical_capability": "dockerfile-configuration-lint",
        "database_pin": ".audit/scanner-configs/rules/hadolint.yaml",
        "notes": "Haskell binary, absent from this host, though the rule selection is pinned.",
    },
    {
        "name": "osv-scanner",
        "binary": "osv-scanner",
        "ecosystems": ("python", "rust"),
        "timeout_seconds": 900.0,
        "required_conditions": ("binary-present", "vulnerability-feed-pinned"),
        "critical_capability": "dependency-vulnerability-enumeration",
        "database_pin": "",
        "notes": "Remote OSV feed, unpinnable offline, so no dependency claim is made at all.",
    },
    {
        "name": "semgrep",
        "binary": "uvx",
        "ecosystems": ("python", "shell"),
        "timeout_seconds": 900.0,
        "required_conditions": ("runner-resolvable", "rule-files-pinned", "nonempty-target-set"),
        "critical_capability": "static-pattern-detection-over-committed-scripts",
        "database_pin": ".audit/scanner-configs/rules/crucible-python.yaml"
        "+.audit/scanner-configs/rules/crucible-shell.yaml",
        "notes": "The only config declaring runs true. Rule files are committed and digested.",
    },
    {
        "name": "trivy",
        "binary": "trivy",
        "ecosystems": ("*",),
        "timeout_seconds": 1200.0,
        "required_conditions": ("binary-present", "vulnerability-feed-pinned"),
        "critical_capability": "filesystem-vulnerability-and-misconfiguration-enumeration",
        "database_pin": "",
        "notes": "OCI-delivered feed, unpinnable offline, so the instrument declines to run.",
    },
)


def instrument_name(scanner: str) -> str:
    """Return the registry name this family uses for one scanner config."""
    return f"D-SCANNER-{scanner.upper()}"


def _register_declarations() -> None:
    """Register every scanner instrument with the twelve required declaration fields.

    Registration is idempotent because the orchestrator imports family modules by
    name and a test harness may import this module a second time; a duplicate
    registration would raise and turn a re-import into a broken instrument.
    """
    for declaration in _REGISTRY_DECLARATIONS:
        name = instrument_name(declaration["name"])
        if name in REGISTRY:
            continue
        REGISTRY.register(
            Instrument(
                name=name,
                category=Category.SCANNER,
                binary=declaration["binary"],
                ecosystems=declaration["ecosystems"],
                timeout_seconds=declaration["timeout_seconds"],
                required_conditions=declaration["required_conditions"],
                critical_capability=declaration["critical_capability"],
                evidence_class=EvidenceClass.RAW_TOOL_OUTPUT,
                requires_parser=True,
                requires_raw_artifact=True,
                disposition_cap_on_absence=Disposition.HOLD,
                bucket=Bucket.D,
                database_pin=declaration["database_pin"],
                notes=declaration["notes"],
            )
        )


_register_declarations()


def _ascii_text(raw: str) -> str:
    """Force a declaration string into the ASCII the emitted YAML is restricted to."""
    return raw.encode("ascii", "backslashreplace").decode("ascii")


def _collapse(raw: Any) -> str:
    """Collapse a folded YAML scalar into one ASCII line."""
    if not isinstance(raw, str):
        return ""
    return _ascii_text(" ".join(raw.split()))


def _first_sentence(raw: str) -> str:
    collapsed = _collapse(raw)
    head, separator, _ = collapsed.partition(". ")
    return (head + separator).strip() if separator else collapsed


def config_dir(base: Path) -> Path:
    return base / core.AUDIT_DIRNAME / SCANNER_CONFIG_DIRNAME


def load_config(path: Path) -> dict[str, Any]:
    """Parse one scanner config, failing closed to an empty declaration.

    An unreadable or non-mapping config is returned as empty rather than raised,
    because the caller turns an empty declaration into a coverage gap and a raise
    would abort the whole family.
    """
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _is_excluded(path: Path, base: Path) -> bool:
    """Reject any candidate under trinity/ or under the audit fixture tree."""
    try:
        relative = path.resolve().relative_to(base.resolve())
    except ValueError:
        return True
    parts = relative.parts
    if not parts:
        return True
    if parts[0] in EXCLUDED_ROOT_PARTS:
        return True
    return core.AUDIT_DIRNAME in parts and EXCLUDED_FIXTURE_PART in parts


def scan_targets(base: Path) -> list[Path]:
    """Every committed script the pinned rule set is allowed to read.

    The target set is the bundles' own Python and shell files. trinity/ holds the
    contract tooling rather than audited bundle bytes, and .audit/fixtures/ holds
    planted positives whose hits would be selfcheck evidence rather than findings
    about a bundle, so both are excluded by path rather than by rule.
    """
    targets: list[Path] = []
    for bundle in core.bundle_roots(base):
        for pattern in TARGET_PATTERNS:
            for candidate in sorted(bundle.glob(pattern)):
                if candidate.is_file() and not _is_excluded(candidate, base):
                    targets.append(candidate)
    return targets


def _relative(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve_argv(template: list[Any], base: Path, targets: list[Path]) -> list[str]:
    """Build the final argv, substituting committed rule-file paths with absolute ones.

    Any template element that names an existing file under the project root is a
    rule-file placeholder and is replaced by its absolute path, so the invocation
    does not depend on the working directory the harness happens to run from.
    """
    argv: list[str] = []
    for element in template:
        token = str(element)
        candidate = base / token
        if token.startswith(core.AUDIT_DIRNAME) and candidate.is_file():
            argv.append(str(candidate.resolve()))
            continue
        argv.append(token)
    argv.extend(str(target.resolve()) for target in targets)
    return argv


def forbidden_argv_hits(argv: list[str], forbidden: list[Any]) -> list[str]:
    """Report every way the final argv reaches a form the contract forbids.

    The declared forbidden list mixes two shapes. An entry carrying an equals sign
    is a single forbidden token such as ``--config=auto``. The remaining entries
    are the separated form of the same invocation and are forbidden only as an
    adjacent window, because ``--config`` on its own is exactly what the pinned
    local rule files are passed with and matching it alone would refuse the legal
    invocation while proving nothing about the registry form.
    """
    tokens = [str(item) for item in forbidden if "=" in str(item)]
    window = [str(item) for item in forbidden if "=" not in str(item)]
    hits: list[str] = []
    for token in tokens:
        if token in argv:
            hits.append(f"forbidden token present in argv: {token}")
    if window:
        width = len(window)
        for index in range(len(argv) - width + 1):
            if argv[index : index + width] == window:
                hits.append("forbidden adjacent argv window present: " + " ".join(window))
    return hits


def parse_semgrep(stdout: str) -> tuple[dict[str, Any] | None, str]:
    """Separate a semgrep findings document from a semgrep tool failure.

    semgrep exits 1 both when it has findings and when its own interpreter fails
    to start, so the exit code cannot tell those apart. A JSON object carrying a
    ``results`` key is a findings document; anything else is a tool failure and
    must never be read as a clean scan.
    """
    text = stdout.strip()
    if not text:
        return None, "stdout was empty, so no findings document was produced"
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        return None, f"stdout did not parse as JSON: {error}"
    if not isinstance(payload, dict):
        return None, "stdout parsed as JSON but was not an object"
    if "results" not in payload:
        return None, "stdout parsed as a JSON object carrying no results key"
    return payload, ""


def semgrep_issues(payload: dict[str, Any], base: Path) -> list[NormalizedIssue]:
    """Convert a semgrep findings document into verifier-owned normalized issues.

    semgrep's own ``check_id`` is retained as ``tool_ref`` only. Identity is
    recomputed by normalize.NormalizedIssue from the rule and the content anchor,
    so a rule renumbering upstream cannot silently change what this harness
    counts as one issue.
    """
    issues: list[NormalizedIssue] = []
    for entry in payload.get("results") or []:
        if not isinstance(entry, dict):
            continue
        extra = entry.get("extra") if isinstance(entry.get("extra"), dict) else {}
        start = entry.get("start") if isinstance(entry.get("start"), dict) else {}
        raw_path = str(entry.get("path") or "")
        anchor = Anchor(
            path=_relative(Path(raw_path), base) if raw_path else "",
            symbol=str(extra.get("metavars", {}).get("$FUNC", {}).get("abstract_content", ""))
            if isinstance(extra.get("metavars"), dict)
            else "",
            excerpt=str(extra.get("lines") or ""),
        )
        issues.append(
            NormalizedIssue(
                rule=str(entry.get("check_id") or "unnamed-rule"),
                anchor=anchor,
                severity=core.normalize_severity(extra.get("severity")),
                message=_collapse(str(extra.get("message") or "")),
                tool=SEMGREP_NAME,
                tool_ref=f"{entry.get('check_id')}@{raw_path}:{start.get('line')}",
                extra={"engine": str(extra.get("engine_kind") or "")},
            )
        )
    return issues


def _issue_finding(issue: NormalizedIssue, instrument: str) -> Finding:
    return Finding(
        finding_id=f"{instrument}-{issue.issue_id[:16]}",
        instrument=instrument,
        critical_class=SCANNER_CRITICAL_CLASS,
        severity=issue.severity,
        caps=Disposition.HOLD,
        bucket=Bucket.D,
        subject=issue.anchor.path or "project",
        statement=_ascii_text(
            f"Pinned rule {issue.rule} matched at {issue.anchor.path}. {issue.message}"
        ),
        evidence=issue.to_row(),
    )


def _missing_config_result(name: str, path: Path) -> InstrumentResult:
    instrument = instrument_name(name)
    return InstrumentResult(
        instrument=instrument,
        ran=False,
        gaps=[
            CoverageGap(
                gap_id=CONFIG_ABSENT_GAP_ID,
                instrument=instrument,
                surface=SCANNER_SURFACE,
                subject=name,
                reason="scanner-config-absent-or-unparseable",
                caps=Disposition.HOLD,
                statement=(
                    f"The config the {name} instrument is declared by did not parse as a mapping "
                    f"at {path.name}, so the instrument has no pinned invocation to run and its "
                    "silence is recorded as a gap rather than as a clean scan."
                ),
            )
        ],
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes={"config_path": path.name},
    )


def _declined_result(name: str, config: dict[str, Any], path: Path) -> InstrumentResult:
    """Build the result for a config that declares runs false.

    The gap identifier is taken from the config rather than reconstructed here,
    so the identifier a reviewer reads in evidence.yaml is the same string the
    pinned config declares and the two cannot drift apart.
    """
    instrument = instrument_name(name)
    gap_id = str(config.get("coverage_gap_id") or "").strip()
    basis = _collapse(config.get("runs_basis"))
    if not gap_id:
        return InstrumentResult(
            instrument=instrument,
            ran=False,
            gaps=[
                CoverageGap(
                    gap_id=CONFIG_SCHEMA_GAP_ID,
                    instrument=instrument,
                    surface=SCANNER_SURFACE,
                    subject=name,
                    reason="declined-scanner-declares-no-coverage-gap-id",
                    caps=Disposition.HOLD,
                    statement=(
                        f"The {name} config declares runs false but names no coverage_gap_id, so "
                        "the gap its absence creates cannot be cited under a stable identifier."
                    ),
                )
            ],
            standing=Standing.INSUFFICIENT_EVIDENCE,
            notes={"config_path": path.name},
        )
    database = config.get("database") if isinstance(config.get("database"), dict) else {}
    return InstrumentResult(
        instrument=instrument,
        ran=False,
        gaps=[
            CoverageGap(
                gap_id=gap_id,
                instrument=instrument,
                surface=SCANNER_SURFACE,
                subject=name,
                reason=_first_sentence(config.get("runs_basis")) or "scanner-declines-to-run",
                caps=Disposition.HOLD,
                statement=basis
                or (
                    f"The {name} instrument declares runs false and gives no basis, which is "
                    "itself a gap in the pinned scanner surface."
                ),
            )
        ],
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes={
            "config_path": path.name,
            "runs": False,
            "pin_state": str(database.get("pin_state") or "unresolved"),
            "evidence_note": _collapse(config.get("evidence_note")),
        },
    )


def _semgrep_result(base: Path, config: dict[str, Any], path: Path) -> InstrumentResult:
    """Run the one scanner config that declares runs true, under its pinned rule files."""
    instrument = instrument_name(SEMGREP_NAME)
    targets = scan_targets(base)
    template = config.get("argv_template")
    if not isinstance(template, list) or not template:
        return _missing_config_result(SEMGREP_NAME, path)

    argv = resolve_argv(template, base, targets)
    forbidden = config.get("forbidden_argv")
    hits = forbidden_argv_hits(argv, forbidden if isinstance(forbidden, list) else [])
    if hits:
        return InstrumentResult(
            instrument=instrument,
            ran=False,
            findings=[
                Finding(
                    finding_id=SEMGREP_FORBIDDEN_FINDING_ID,
                    instrument=instrument,
                    critical_class="scanner-configuration-integrity",
                    severity=core.Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject="project",
                    statement=_ascii_text(
                        "The resolved semgrep argv reached a form the contract forbids outright, "
                        "so the scan was refused rather than executed: " + "; ".join(hits)
                    ),
                    evidence={"argv": argv, "hits": hits},
                )
            ],
            gaps=[
                CoverageGap(
                    gap_id=SEMGREP_BLOCKED_GAP_ID,
                    instrument=instrument,
                    surface=SCANNER_SURFACE,
                    reason="forbidden-argv-refused-before-execution",
                    caps=Disposition.HOLD,
                    statement=(
                        "semgrep did not execute because its resolved argv was refused, so the "
                        "static surface it would have covered carries no result."
                    ),
                )
            ],
            standing=Standing.OBSERVED_VIOLATION,
            notes={"argv": argv, "target_count": len(targets)},
        )

    if not targets:
        return InstrumentResult(
            instrument=instrument,
            ran=False,
            gaps=[
                CoverageGap(
                    gap_id=SEMGREP_NO_TARGETS_GAP_ID,
                    instrument=instrument,
                    surface=SCANNER_SURFACE,
                    reason="empty-target-set",
                    caps=Disposition.HOLD,
                    statement=(
                        "The declared target patterns resolved to no committed file, so a clean "
                        "semgrep result would have been clean over nothing."
                    ),
                )
            ],
            standing=Standing.INSUFFICIENT_EVIDENCE,
            notes={"argv": argv, "target_count": 0},
        )

    timeout = config.get("timeout_seconds")
    artifact = core.run_capture(
        argv,
        artifact_id="scanner-semgrep",
        cwd=base,
        timeout=float(timeout) if isinstance(timeout, int | float) else 900.0,
    )
    payload, parse_error = parse_semgrep(artifact.stdout)
    target_rows = [_relative(target, base) for target in targets]

    if payload is None:
        reason = artifact.blocked_reason or "tool-error-unparseable-output"
        return InstrumentResult(
            instrument=instrument,
            ran=False,
            artifacts=[artifact],
            gaps=[
                CoverageGap(
                    gap_id=SEMGREP_BLOCKED_GAP_ID,
                    instrument=instrument,
                    surface=SCANNER_SURFACE,
                    reason=reason,
                    caps=Disposition.HOLD,
                    statement=_ascii_text(
                        "semgrep produced no parseable findings document over "
                        f"{len(targets)} committed target files, so the static surface carries no "
                        f"result at all. Exit code {artifact.exit_code}, blocked reason {reason}, "
                        f"parse outcome: {parse_error or 'not reached'}. A tool that failed to "
                        "produce a document is never read as a tool that found nothing."
                    ),
                )
            ],
            standing=Standing.INSUFFICIENT_EVIDENCE,
            notes={
                "argv": argv,
                "target_count": len(targets),
                "targets": target_rows,
                "stderr_head": _collapse(artifact.stderr)[:400],
            },
        )

    issues = semgrep_issues(payload, base)
    findings = [_issue_finding(issue, instrument) for issue in issues]
    errors = payload.get("errors") if isinstance(payload.get("errors"), list) else []
    standing = Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE
    gaps: list[CoverageGap] = []
    if errors:
        gaps.append(
            CoverageGap(
                gap_id=SEMGREP_BLOCKED_GAP_ID,
                instrument=instrument,
                surface=SCANNER_SURFACE,
                reason="partial-scan-tool-reported-errors",
                caps=Disposition.HOLD,
                statement=_ascii_text(
                    f"semgrep produced a findings document but reported {len(errors)} scan "
                    "errors, so its coverage over the declared target set is partial and a "
                    "negative result over the affected files is not demonstrated."
                ),
            )
        )
        standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=instrument,
        ran=True,
        findings=findings,
        gaps=gaps,
        artifacts=[artifact],
        standing=standing,
        notes={
            "argv": argv,
            "target_count": len(targets),
            "targets": target_rows,
            "issue_count": len(issues),
            "scan_error_count": len(errors),
            "normalized_issues": [issue.to_row() for issue in issues],
            "evidence_note": _collapse(config.get("evidence_note")),
        },
    )


def _internal_error_result(name: str, error: Exception) -> InstrumentResult:
    instrument = instrument_name(name)
    return InstrumentResult(
        instrument=instrument,
        ran=False,
        gaps=[
            CoverageGap(
                gap_id=INTERNAL_ERROR_GAP_ID,
                instrument=instrument,
                surface=SCANNER_SURFACE,
                subject=name,
                reason="instrument-raised-internally",
                caps=Disposition.HOLD,
                statement=_ascii_text(
                    f"The {name} instrument raised {type(error).__name__} before producing a "
                    f"determination, so it covered nothing: {error}"
                ),
            )
        ],
        standing=Standing.INSUFFICIENT_EVIDENCE,
    )


def run_family(base: Path, reconnaissance: recon.Recon) -> list[InstrumentResult]:
    """Run the step 8a scanner family over every resident bundle.

    Returns one InstrumentResult per declared scanner config, in a fixed order so
    two runs over the same bytes emit the same evidence rows. Nothing here raises:
    a scanner that cannot be reached, a config that cannot be parsed, and an
    instrument that fails internally each become a coverage gap, because an
    instrument that returns silently would read downstream as a pass.
    """
    del reconnaissance
    results: list[InstrumentResult] = []
    directory = config_dir(base)
    for name in SCANNER_NAMES:
        path = directory / f"{name}.yaml"
        try:
            config = load_config(path)
            if not config or config.get("schema") != SCANNER_CONFIG_SCHEMA:
                results.append(_missing_config_result(name, path))
                continue
            if not bool(config.get("runs", False)):
                results.append(_declined_result(name, config, path))
                continue
            if name == SEMGREP_NAME:
                results.append(_semgrep_result(base, config, path))
                continue
            results.append(_declined_result(name, config, path))
        except Exception as error:
            results.append(_internal_error_result(name, error))
    return results


__all__ = [
    "SCANNER_NAMES",
    "TARGET_PATTERNS",
    "forbidden_argv_hits",
    "instrument_name",
    "load_config",
    "parse_semgrep",
    "resolve_argv",
    "run_family",
    "scan_targets",
    "semgrep_issues",
]
