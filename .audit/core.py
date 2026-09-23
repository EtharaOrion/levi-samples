"""Shared contracts for the CRUCIBLE harness.

Every instrument module in this harness imports its vocabulary, its result
shapes, and its disposition lattice from this module. Nothing else defines a
disposition, a bucket, or an outcome token. The vocabularies below are closed:
a value outside one of them is a programming error and raises rather than
degrading into a silent pass.

The disposition lattice is a total order with SHIP at the top. Every operation
that combines results takes the minimum, so a family can only ever lower the
running disposition. No function in this harness raises a disposition, which is
the deterministic encoding of the rule that a clean grounding result is never
evidence of correctness.
"""

from __future__ import annotations

import dataclasses
import enum
import hashlib
import json
import os
import pathlib
import subprocess
import time
import unicodedata
from collections.abc import Iterable, Sequence
from typing import Any


class Disposition(enum.IntEnum):
    """Closed disposition vocabulary, ordered so that lower is worse.

    IntEnum rather than Enum so that ``min`` over a sequence of dispositions is
    the cap operation directly, with no comparison helper to get wrong.
    """

    BLOCK = 0
    HOLD = 1
    SHIP = 2

    @property
    def token(self) -> str:
        return self.name


def cap(*values: Disposition) -> Disposition:
    """Combine dispositions by taking the worst. Never raises a disposition."""
    if not values:
        return Disposition.SHIP
    return min(values)


def cap_all(values: Iterable[Disposition]) -> Disposition:
    collected = list(values)
    if not collected:
        return Disposition.SHIP
    return min(collected)


class Bucket(enum.Enum):
    """Bucket D is deterministic harness code. Bucket N is semantic residual.

    Every instrument in this harness is Bucket D. Bucket N exists in the
    vocabulary because the Phase 2 review lane emits judgements that must be
    labelled, and because a Bucket N record may never raise above a Bucket D
    record. The combination helper below enforces that asymmetry.
    """

    D = "deterministic"
    N = "semantic"


class Outcome(enum.Enum):
    """Closed per-check outcome vocabulary used by selfcheck rows.

    CLEAN means the check ran on a fixture carrying no planted defect and
    produced no finding. FIRED means the check ran on a planted positive and
    produced its finding. INERT means the check ran and could not produce a
    finding on a planted positive, which verifier principle 7 makes a broken
    instrument capping at BLOCK. UNRUN means the check did not execute.
    """

    CLEAN = "clean"
    FIRED = "fired"
    INERT = "inert"
    UNRUN = "unrun"


# Outcome tokens that cap the gate at BLOCK under verifier principle 7.
BROKEN_OUTCOMES = frozenset({Outcome.INERT, Outcome.UNRUN})


class Standing(enum.Enum):
    """Three-valued detector standing under verifier principle 8.

    A negative conclusion is reachable only through DEMONSTRATED_COVERAGE. A
    self-reported zero, a missing marker, a conversion-only trace, and an
    unsupported harness version all resolve as INSUFFICIENT_EVIDENCE, which is
    a coverage gap capping at HOLD and never a pass.
    """

    OBSERVED_VIOLATION = "observed_violation"
    DEMONSTRATED_COVERAGE = "demonstrated_coverage"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class Severity(enum.Enum):
    """Normalized severity. Unknown input fails closed to MEDIUM or worse."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


_SEVERITY_ALIASES = {
    "critical": Severity.CRITICAL,
    "crit": Severity.CRITICAL,
    "blocker": Severity.CRITICAL,
    "high": Severity.HIGH,
    "error": Severity.HIGH,
    "moderate": Severity.MEDIUM,
    "medium": Severity.MEDIUM,
    "warning": Severity.MEDIUM,
    "low": Severity.LOW,
    "minor": Severity.LOW,
    "note": Severity.LOW,
    "info": Severity.INFO,
    "informational": Severity.INFO,
}


def normalize_severity(raw: Any) -> Severity:
    """Map a scanner severity onto the closed vocabulary, failing closed.

    Phase 1 item 7 requires that an unknown severity resolve to at least
    MEDIUM. An unrecognized token, a null, or a non-string therefore becomes
    MEDIUM rather than LOW or INFO. A recognized token below MEDIUM keeps its
    own value because it was recognized, not guessed.
    """
    if isinstance(raw, Severity):
        return raw
    if not isinstance(raw, str):
        return Severity.MEDIUM
    token = raw.strip().lower()
    if not token:
        return Severity.MEDIUM
    resolved = _SEVERITY_ALIASES.get(token)
    if resolved is None:
        return Severity.MEDIUM
    return resolved


HEX64_LENGTH = 64


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_hex64(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != HEX64_LENGTH:
        return False
    return all(character in "0123456789abcdef" for character in value)


def canonical_json(payload: Any) -> bytes:
    """Deterministic JSON encoding used for every payload hash in this harness."""
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=_json_default,
    ).encode("utf-8")


def _json_default(value: Any) -> Any:
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, pathlib.Path):
        return str(value)
    if isinstance(value, frozenset | set):
        return sorted(value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return dataclasses.asdict(value)
    raise TypeError(f"no canonical encoding for {type(value)!r}")


def canonical_digest(payload: Any) -> str:
    return sha256_bytes(canonical_json(payload))


def tree_digest(root: pathlib.Path, relative_paths: Sequence[str]) -> str:
    """Aggregate digest over a named path set, order independent and total.

    Each member contributes its POSIX relative path and its content digest, or
    the literal token ``absent`` when the path does not resolve to a file. An
    absent member is recorded rather than skipped so that a vanished file moves
    the aggregate instead of silently preserving it.
    """
    members: list[list[str]] = []
    for relative in sorted(set(relative_paths)):
        candidate = root / relative
        if candidate.is_file():
            members.append([relative, sha256_path(candidate)])
        else:
            members.append([relative, "absent"])
    return canonical_digest(members)


_NORMALIZATION_DOMAIN = "nfkc_fold+lowercase+collapse_whitespace"


def normalization_domain() -> str:
    return _NORMALIZATION_DOMAIN


def normalize_text(raw: str) -> str:
    """The audit harness's own normalizer.

    Step 8b requires that the audit harness normalize designated slots with its
    own normalizer and never with the authoring one. This function is that
    normalizer. It is deliberately independent of solution/recompute.py and is
    never imported from bundle bytes.
    """
    folded = unicodedata.normalize("NFKC", raw).casefold()
    return " ".join(folded.split())


def token_ngrams(raw: str, width: int) -> list[tuple[str, ...]]:
    if width < 1:
        raise ValueError("ngram width must be at least 1")
    tokens = normalize_text(raw).split()
    if len(tokens) < width:
        return []
    return [tuple(tokens[index : index + width]) for index in range(len(tokens) - width + 1)]


def ngram_containment(needle: str, haystack: str, width: int) -> float:
    """Fraction of the needle's distinct n-grams that appear in the haystack.

    Containment rather than Jaccard because the private carrier is typically far
    smaller than the agent-visible closure, and Jaccard would dilute a total
    leak of a small carrier into a small number.
    """
    needle_grams = set(token_ngrams(needle, width))
    if not needle_grams:
        return 0.0
    haystack_grams = set(token_ngrams(haystack, width))
    if not haystack_grams:
        return 0.0
    return len(needle_grams & haystack_grams) / float(len(needle_grams))


@dataclasses.dataclass(frozen=True)
class Finding:
    """A retained defect. Always carries the disposition it caps at."""

    finding_id: str
    instrument: str
    critical_class: str
    severity: Severity
    caps: Disposition
    bucket: Bucket
    subject: str
    statement: str
    evidence: dict[str, Any] = dataclasses.field(default_factory=dict)

    def to_row(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "instrument": self.instrument,
            "critical_class": self.critical_class,
            "severity": self.severity.value,
            "caps": self.caps.token,
            "bucket": self.bucket.value,
            "subject": self.subject,
            "statement": self.statement,
            "evidence": self.evidence,
        }


@dataclasses.dataclass(frozen=True)
class CoverageGap:
    """A D-COVERAGE-GAP. Never converted to model judgement, always caps."""

    gap_id: str
    instrument: str
    surface: str
    reason: str
    caps: Disposition
    statement: str
    subject: str = "project"

    def __post_init__(self) -> None:
        if self.caps is Disposition.SHIP:
            raise ValueError(f"coverage gap {self.gap_id} must cap below SHIP")

    def to_row(self) -> dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "instrument": self.instrument,
            "surface": self.surface,
            "subject": self.subject,
            "reason": self.reason,
            "caps": self.caps.token,
            "statement": self.statement,
        }


@dataclasses.dataclass(frozen=True)
class RawArtifact:
    """A captured tool invocation, recorded whole so evidence is auditable."""

    artifact_id: str
    argv: list[str]
    exit_code: int | None
    stdout: str
    stderr: str
    elapsed_seconds: float
    timed_out: bool
    blocked_reason: str | None = None

    def to_row(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "argv": list(self.argv),
            "exit_code": self.exit_code,
            "stdout_sha256": sha256_bytes(self.stdout.encode("utf-8", "replace")),
            "stderr_sha256": sha256_bytes(self.stderr.encode("utf-8", "replace")),
            "stdout_bytes": len(self.stdout.encode("utf-8", "replace")),
            "stderr_bytes": len(self.stderr.encode("utf-8", "replace")),
            "elapsed_seconds": round(self.elapsed_seconds, 6),
            "timed_out": self.timed_out,
            "blocked_reason": self.blocked_reason,
        }


@dataclasses.dataclass
class InstrumentResult:
    """What every instrument in this harness returns.

    ``ran`` false with an empty gap list is illegal: an instrument that did not
    run must say why in a gap, otherwise its silence would read as a pass.
    """

    instrument: str
    ran: bool
    findings: list[Finding] = dataclasses.field(default_factory=list)
    gaps: list[CoverageGap] = dataclasses.field(default_factory=list)
    artifacts: list[RawArtifact] = dataclasses.field(default_factory=list)
    standing: Standing = Standing.INSUFFICIENT_EVIDENCE
    notes: dict[str, Any] = dataclasses.field(default_factory=dict)

    @property
    def disposition(self) -> Disposition:
        """The cap this instrument imposes. Never above SHIP."""
        values = [finding.caps for finding in self.findings]
        values.extend(gap.caps for gap in self.gaps)
        if not self.ran and not self.gaps:
            return Disposition.BLOCK
        return cap_all(values)

    def to_row(self) -> dict[str, Any]:
        return {
            "instrument": self.instrument,
            "ran": self.ran,
            "standing": self.standing.value,
            "disposition_cap": self.disposition.token,
            "findings": [finding.to_row() for finding in self.findings],
            "coverage_gaps": [gap.to_row() for gap in self.gaps],
            "raw_artifacts": [artifact.to_row() for artifact in self.artifacts],
            "notes": self.notes,
        }


@dataclasses.dataclass(frozen=True)
class SelfcheckRow:
    """One row of .audit/selfcheck.yaml, per Phase 1 item 11."""

    check_id: str
    instrument: str
    argv: list[str]
    exit_code: int | None
    elapsed_seconds: float
    clean_half: Outcome
    positive_half: Outcome
    required: bool
    detail: str = ""

    @property
    def outcome(self) -> Outcome:
        """Both-halves outcome. Either half broken makes the row broken."""
        if self.clean_half is Outcome.UNRUN or self.positive_half is Outcome.UNRUN:
            return Outcome.UNRUN
        if self.positive_half is not Outcome.FIRED:
            return Outcome.INERT
        if self.clean_half is not Outcome.CLEAN:
            return Outcome.INERT
        return Outcome.FIRED

    @property
    def caps(self) -> Disposition:
        if not self.required:
            return Disposition.SHIP
        if self.outcome in BROKEN_OUTCOMES:
            return Disposition.BLOCK
        return Disposition.SHIP

    def to_row(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "instrument": self.instrument,
            "argv": list(self.argv),
            "exit_code": self.exit_code,
            "elapsed_seconds": round(self.elapsed_seconds, 6),
            "required": self.required,
            "clean_half": self.clean_half.value,
            "positive_half": self.positive_half.value,
            "outcome": self.outcome.value,
            "caps": self.caps.token,
            "detail": self.detail,
        }


def run_capture(
    argv: Sequence[str],
    *,
    artifact_id: str,
    cwd: pathlib.Path | None = None,
    timeout: float = 600.0,
    env: dict[str, str] | None = None,
) -> RawArtifact:
    """Run a command and capture its real exit code, stdout, and stderr.

    Phase 1 item 6 requires real exit codes and full raw artifacts. A nonzero
    exit is recorded as evidence, never converted into an automatic failure
    here; the calling instrument decides what a given exit code means for its
    own tool. A missing binary is recorded as blocked rather than crashing,
    because a blocked tool is a coverage gap for the caller to raise and not an
    exception that would abort the whole run.
    """
    merged_env = dict(os.environ)
    if env:
        merged_env.update(env)
    started = time.monotonic()
    try:
        completed = subprocess.run(  # noqa: S603
            list(argv),
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            env=merged_env,
            check=False,
        )
    except FileNotFoundError as error:
        return RawArtifact(
            artifact_id=artifact_id,
            argv=list(argv),
            exit_code=None,
            stdout="",
            stderr=str(error),
            elapsed_seconds=time.monotonic() - started,
            timed_out=False,
            blocked_reason="binary-not-found",
        )
    except subprocess.TimeoutExpired as error:
        return RawArtifact(
            artifact_id=artifact_id,
            argv=list(argv),
            exit_code=None,
            stdout=error.stdout or "" if isinstance(error.stdout, str) else "",
            stderr=error.stderr or "" if isinstance(error.stderr, str) else "",
            elapsed_seconds=time.monotonic() - started,
            timed_out=True,
            blocked_reason="timeout",
        )
    except PermissionError as error:
        return RawArtifact(
            artifact_id=artifact_id,
            argv=list(argv),
            exit_code=None,
            stdout="",
            stderr=str(error),
            elapsed_seconds=time.monotonic() - started,
            timed_out=False,
            blocked_reason="permission-denied",
        )
    return RawArtifact(
        artifact_id=artifact_id,
        argv=list(argv),
        exit_code=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
        elapsed_seconds=time.monotonic() - started,
        timed_out=False,
        blocked_reason=None,
    )


AUDIT_DIRNAME = ".audit"
SCOPE_FILENAME = "scope.yaml"
SCOPE_APPROVED_FILENAME = "scope.approved"
CAPABILITIES_FILENAME = "capabilities.yaml"
EVIDENCE_FILENAME = "evidence.yaml"
SELFCHECK_FILENAME = "selfcheck.yaml"
BUDGET_FILENAME = "budget.yaml"
FIDELITY_FILENAME = "fidelity.yaml"
FINDINGS_FILENAME = "findings.yaml"
REVIEW_FILENAME = "review.md"


def project_root() -> pathlib.Path:
    """The verification root: the directory whose direct child is .audit."""
    here = pathlib.Path(__file__).resolve().parent
    return here.parent


def audit_root() -> pathlib.Path:
    return project_root() / AUDIT_DIRNAME


def bundle_roots(root: pathlib.Path | None = None) -> list[pathlib.Path]:
    """Every resident bundle directory, resolved from committed bytes alone.

    A bundle is a direct child of a lane root carrying a task.toml. The lane
    roots are staging/, samples/, and delivery/ when present, plus the project
    root itself, which is where this verification root holds its bundles.
    """
    base = root or project_root()
    candidates: list[pathlib.Path] = []
    lanes = [base, base / "staging", base / "samples", base / "delivery"]
    for lane in lanes:
        if not lane.is_dir():
            continue
        for child in sorted(lane.iterdir()):
            if not child.is_dir():
                continue
            if child.name.startswith("."):
                continue
            if (child / "task.toml").is_file():
                candidates.append(child)
    unique: list[pathlib.Path] = []
    seen: set[pathlib.Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(candidate)
    return unique


def lane_of(bundle: pathlib.Path, root: pathlib.Path | None = None) -> str:
    base = (root or project_root()).resolve()
    parent = bundle.resolve().parent
    if parent == base:
        return "root"
    return parent.name
