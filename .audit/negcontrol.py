"""Negative-control demonstrations, discharging CRUCIBLE contract items 12, 12a and 12c.

Verifier principle 7 makes a required deterministic check live rather than
merely fail-closed. A check that has only been shown to stay quiet on clean
material has not been shown to work at all, because a check that never fires is
indistinguishable from one that is quiet for the wrong reason. So every control
here drives the real instrument twice, once over material carrying no defect and
once over material carrying a planted one, and requires the instrument to stay
clean on the first and to produce its finding on the second.

The instruments are invoked directly rather than reimplemented. A control that
asserted its own copy of the logic would prove only that the copy works, which
is precisely the inert-check defect this harness exists to catch elsewhere.

Fixture bytes are committed under .audit/fixtures/negative/ as compact seed
documents and are staged into a temporary directory carrying the directory shape
each instrument resolves against. Staging rather than committing whole bundle
trees keeps the fixture surface small enough to review by eye, and the seed
document is the reviewable artifact because every byte the instrument reads is
derived from it.

One control is recorded as unrun rather than demonstrated. The empty-submission
control requires replaying a submission inside a pinned image, no image resolves
at this root, and inventing a score would be a fabricated demonstration. An
unrun required control caps the gate exactly as an inert one does, which is the
honest reading.
"""

from __future__ import annotations

import datetime
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

import attestation
import contamination
import core
import verify
from core import Disposition, Outcome

FIXTURE_SUBPATH = "fixtures/negative"
SEED_FILENAME = "seed.yaml"

CLEAN = "clean"
POSITIVE = "positive"


def fixture_root(base: Path) -> Path:
    """Resolve the committed negative-control fixture tree."""
    return base / core.AUDIT_DIRNAME / FIXTURE_SUBPATH


def load_seed(base: Path, control_id: str, half: str) -> dict[str, Any]:
    """Read one committed fixture seed, failing closed to an empty mapping."""
    path = fixture_root(base) / control_id / half / SEED_FILENAME
    if not path.is_file():
        return {}
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return document if isinstance(document, dict) else {}


def seed_path(control_id: str, half: str) -> str:
    """Return the repository-relative path of one fixture seed."""
    return f"{core.AUDIT_DIRNAME}/{FIXTURE_SUBPATH}/{control_id}/{half}/{SEED_FILENAME}"


def stage(seed: dict[str, Any], destination: Path) -> Path:
    """Materialise a seed into the directory shape the instruments resolve against.

    The returned path is the project base an instrument is given. Screening
    roots are written one level above it because the contamination instruments
    resolve ENGRAM roots through the parent, which is the same relation that
    holds in the real tree.
    """
    base = destination / "root"
    base.mkdir(parents=True, exist_ok=True)
    (destination / ".memory" / "roots").mkdir(parents=True, exist_ok=True)

    for name, payload in (seed.get("roots") or {}).items():
        target = destination / ".memory" / "roots" / name
        target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    view = seed.get("crucible_view")
    if view is not None:
        (destination / ".memory" / "crucible_view.yaml").write_text(
            yaml.safe_dump(view, sort_keys=True, allow_unicode=False), encoding="utf-8"
        )

    for relative, payload in (seed.get("files") or {}).items():
        target = base / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, str):
            target.write_text(payload, encoding="utf-8")
        elif relative.endswith(".json"):
            target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        else:
            target.write_text(
                yaml.safe_dump(payload, sort_keys=True, allow_unicode=False), encoding="utf-8"
            )
    return base


def staged_bundles(seed: dict[str, Any], base: Path) -> list[Path]:
    """Resolve the bundle roots a staged fixture declares."""
    names = seed.get("bundles") or []
    return [base / str(name) for name in names]


def _now() -> datetime.datetime:
    """Return the instant the controls compare freshness against."""
    return datetime.datetime.now(datetime.UTC)


def _fired(result: Any, expect: str) -> bool:
    """Decide whether an instrument result carries the expected planted signal."""
    if expect.startswith("finding:"):
        token = expect.split(":", 1)[1]
        return any(token in item.finding_id for item in result.findings)
    if expect.startswith("gap:"):
        token = expect.split(":", 1)[1]
        return any(token in item.gap_id for item in result.gaps)
    if expect == "any-finding":
        return bool(result.findings)
    return False


def _clean(result: Any, forbid: str) -> bool:
    """Decide whether an instrument stayed clean of the signal a control plants."""
    return not _fired(result, forbid)


_CONTAMINATION_RUNNERS = {
    "exclusion": "_run_exclusion",
    "freeze": "_run_freeze",
    "neardup": "_run_neardup",
    "strip": "_run_strip",
    "record": "_run_record",
}


def run_contamination_control(
    base: Path, control_id: str, atom: str, expect: str
) -> dict[str, Any]:
    """Drive one contamination atom over its clean and planted fixture halves."""
    runner = getattr(contamination, _CONTAMINATION_RUNNERS[atom], None)
    if runner is None:
        return {
            "clean": Outcome.UNRUN,
            "positive": Outcome.UNRUN,
            "detail": f"contamination atom {atom} is not callable",
        }
    outcomes: dict[str, Any] = {}
    for half in (CLEAN, POSITIVE):
        seed = load_seed(base, control_id, half)
        if not seed:
            outcomes[half] = None
            continue
        with tempfile.TemporaryDirectory() as raw:
            staged = stage(seed, Path(raw))
            try:
                result = runner(staged, staged_bundles(seed, staged), _now())
            except Exception as error:  # noqa: BLE001
                outcomes[half] = f"error: {type(error).__name__}: {error}"
                continue
            outcomes[half] = result
    return _resolve(outcomes, expect, control_id)


def _resolve(outcomes: dict[str, Any], expect: str, control_id: str) -> dict[str, Any]:
    """Reduce a pair of instrument results into a both-halves verdict."""
    clean_result = outcomes.get(CLEAN)
    positive_result = outcomes.get(POSITIVE)

    if clean_result is None or positive_result is None:
        missing = [half for half in (CLEAN, POSITIVE) if outcomes.get(half) is None]
        return {
            "clean": Outcome.UNRUN,
            "positive": Outcome.UNRUN,
            "detail": f"{control_id} has no committed seed for: {', '.join(missing)}",
        }
    if isinstance(clean_result, str) or isinstance(positive_result, str):
        detail = " ".join(
            str(value) for value in (clean_result, positive_result) if isinstance(value, str)
        )
        return {"clean": Outcome.UNRUN, "positive": Outcome.UNRUN, "detail": detail}

    clean_ok = _clean(clean_result, expect)
    positive_ok = _fired(positive_result, expect)
    return {
        "clean": Outcome.CLEAN if clean_ok else Outcome.FIRED,
        "positive": Outcome.FIRED if positive_ok else Outcome.CLEAN,
        "detail": (
            f"expected {expect}; clean half "
            f"{'stayed quiet' if clean_ok else 'fired unexpectedly'}, positive half "
            f"{'fired as planted' if positive_ok else 'failed to fire'}"
        ),
    }


def run_verify_control(base: Path, control_id: str, rule: str) -> dict[str, Any]:
    """Drive one verifier rule over its clean and planted fixture halves."""
    outcomes: dict[str, Any] = {}
    for half in (CLEAN, POSITIVE):
        seed = load_seed(base, control_id, half)
        if not seed:
            outcomes[half] = None
            continue
        with tempfile.TemporaryDirectory() as raw:
            staged = stage(seed, Path(raw))
            context = staged / "evidence.yaml"
            findings = staged / "findings.yaml"
            context.write_text(
                yaml.safe_dump(seed.get("evidence") or {}, sort_keys=True, allow_unicode=False),
                encoding="utf-8",
            )
            findings.write_text(
                yaml.safe_dump(seed.get("findings") or {}, sort_keys=True, allow_unicode=False),
                encoding="utf-8",
            )
            try:
                report = verify.verify_findings(findings, context, staged)
            except Exception as error:  # noqa: BLE001
                outcomes[half] = f"error: {type(error).__name__}: {error}"
                continue
            outcomes[half] = {row["rule"] for row in report["violations"]}

    clean_rules = outcomes.get(CLEAN)
    positive_rules = outcomes.get(POSITIVE)
    if clean_rules is None or positive_rules is None:
        return {
            "clean": Outcome.UNRUN,
            "positive": Outcome.UNRUN,
            "detail": f"{control_id} has no committed seed for both halves",
        }
    if isinstance(clean_rules, str) or isinstance(positive_rules, str):
        detail = " ".join(
            str(value) for value in (clean_rules, positive_rules) if isinstance(value, str)
        )
        return {"clean": Outcome.UNRUN, "positive": Outcome.UNRUN, "detail": detail}

    clean_ok = rule not in clean_rules
    positive_ok = rule in positive_rules
    return {
        "clean": Outcome.CLEAN if clean_ok else Outcome.FIRED,
        "positive": Outcome.FIRED if positive_ok else Outcome.CLEAN,
        "detail": (
            f"rule {rule}; clean half {'did not raise it' if clean_ok else 'raised it'}, "
            f"positive half {'raised it as planted' if positive_ok else 'did not raise it'}"
        ),
    }


def run_source_integrity_control(base: Path) -> dict[str, Any]:
    """Demonstrate that a dirty tree presented as clean is refused.

    Both halves are real git repositories rather than recorded claims, because
    the rule re-derives live state instead of trusting the record, and a fixture
    that only supplied a record would exercise the trusting path this rule
    exists to avoid.
    """
    git = shutil.which("git")
    if git is None:
        return {
            "clean": Outcome.UNRUN,
            "positive": Outcome.UNRUN,
            "detail": "git is not available on this host so no live tree can be constructed",
        }

    def build(dirty: bool) -> tuple[Path, str]:
        raw = Path(tempfile.mkdtemp())
        subprocess.run([git, "init", "-q", str(raw)], check=True, capture_output=True)
        (raw / "seed.txt").write_text("committed\n", encoding="utf-8")
        env = {
            "GIT_AUTHOR_NAME": "fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        }
        subprocess.run([git, "-C", str(raw), "add", "seed.txt"], check=True, capture_output=True)
        subprocess.run(
            [git, "-C", str(raw), "commit", "-q", "-m", "seed"],
            check=True,
            capture_output=True,
            env={**env, "PATH": "/usr/bin:/bin:/usr/local/bin"},
        )
        sha = subprocess.run(
            [git, "-C", str(raw), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.strip()
        if dirty:
            (raw / "uncommitted.txt").write_text("dirty\n", encoding="utf-8")
        return raw, sha

    results: dict[str, set[str]] = {}
    for half, dirty in ((CLEAN, False), (POSITIVE, True)):
        root, sha = build(dirty)
        try:
            document = {
                "schema": "crucible.evidence/v1",
                "disposition": "HOLD",
                "scope_digest": "",
                "recon": {"git_sha": sha, "dirty_bit": False, "dirty_entries": []},
                "instruments": [],
                "findings": [],
                "coverage_gaps": [],
            }
            rows = verify.check_source_integrity(document, root)
            results[half] = {
                str(row["statement"]) for row in rows if row["caps"] == Disposition.BLOCK.token
            }
        finally:
            shutil.rmtree(root, ignore_errors=True)

    token = "clean tree while the live tree is dirty"
    clean_ok = not any(token in text for text in results.get(CLEAN, set()))
    positive_ok = any(token in text for text in results.get(POSITIVE, set()))
    return {
        "clean": Outcome.CLEAN if clean_ok else Outcome.FIRED,
        "positive": Outcome.FIRED if positive_ok else Outcome.CLEAN,
        "detail": (
            "a real repository recorded as clean was accepted while a real repository with an "
            "uncommitted file recorded as clean was refused"
            if clean_ok and positive_ok
            else f"clean={sorted(results.get(CLEAN, set()))} positive="
            f"{sorted(results.get(POSITIVE, set()))}"
        ),
    }


def run_attestation_control(base: Path, control_id: str, expect: str) -> dict[str, Any]:
    """Drive the execution-attestation verifier over a planted envelope pair.

    The aggregate resolution cannot separate every control pair, because no
    external trust root supplies verification key material at this root and the
    signature clause therefore resolves unresolved on any envelope whatsoever.
    A control that keyed on the aggregate alone would report the ingestion
    controls as inert for a reason that has nothing to do with ingestion. So the
    expectation names the discriminator each control actually turns on:
    ``ingested:false`` for the controls that must be refused before any clause
    runs, and ``resolution:fail`` for the control that must reach verification
    and fail a named binding clause.
    """
    outcomes: dict[str, dict[str, Any]] = {}
    for half in (CLEAN, POSITIVE):
        seed = load_seed(base, control_id, half)
        if not seed:
            return {
                "clean": Outcome.UNRUN,
                "positive": Outcome.UNRUN,
                "detail": f"{control_id} has no committed seed for both halves",
            }
        envelope = seed.get("envelope")
        policy = seed.get("policy") or {}
        expected = seed.get("expected") or {}
        raw = "" if envelope is None else json.dumps(envelope)
        ingested = attestation.ingest_envelope(raw)
        report = attestation.verify_envelope(ingested, policy, expected)
        outcomes[half] = {
            "ingested": bool(ingested.get("ingested")),
            "reason": str(ingested.get("reason") or ""),
            "resolution": str(report.get("resolution")),
        }

    def matches(row: dict[str, Any]) -> bool:
        if expect == "ingested:false":
            return not row["ingested"]
        if expect == "resolution:fail":
            return row["resolution"] == "fail"
        return False

    clean_ok = not matches(outcomes[CLEAN])
    positive_ok = matches(outcomes[POSITIVE])
    return {
        "clean": Outcome.CLEAN if clean_ok else Outcome.FIRED,
        "positive": Outcome.FIRED if positive_ok else Outcome.CLEAN,
        "detail": (
            f"discriminator {expect}; clean half {outcomes[CLEAN]} and planted half "
            f"{outcomes[POSITIVE]}"
        ),
    }


def run_budget_control(base: Path, control_id: str) -> dict[str, Any]:
    """Drive the budget-block determination over a declared and an absent manifest."""
    outcomes: dict[str, bool] = {}
    for half in (CLEAN, POSITIVE):
        seed = load_seed(base, control_id, half)
        if not seed:
            return {
                "clean": Outcome.UNRUN,
                "positive": Outcome.UNRUN,
                "detail": f"{control_id} has no committed seed for both halves",
            }
        with tempfile.TemporaryDirectory() as raw:
            staged = stage(seed, Path(raw))
            report = attestation.budget_determination(staged)
            outcomes[half] = bool(report.get("any_bundle_carries_budget_block"))

    clean_ok = outcomes.get(CLEAN) is False
    positive_ok = outcomes.get(POSITIVE) is True
    return {
        "clean": Outcome.CLEAN if clean_ok else Outcome.FIRED,
        "positive": Outcome.FIRED if positive_ok else Outcome.CLEAN,
        "detail": (
            "a manifest carrying only resource limits and timeouts was read as carrying no "
            "budget block while a manifest declaring budget_hours, budget_envelope and "
            "budget_margin was read as carrying one"
            if clean_ok and positive_ok
            else f"clean={outcomes.get(CLEAN)} positive={outcomes.get(POSITIVE)}"
        ),
    }


__all__ = [
    "CLEAN",
    "FIXTURE_SUBPATH",
    "POSITIVE",
    "SEED_FILENAME",
    "fixture_root",
    "load_seed",
    "run_attestation_control",
    "run_budget_control",
    "run_contamination_control",
    "run_source_integrity_control",
    "run_verify_control",
    "seed_path",
    "stage",
    "staged_bundles",
]
