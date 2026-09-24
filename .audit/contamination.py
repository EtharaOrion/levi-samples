"""Contamination screening family, discharging CRUCIBLE contract steps 8i through 8n.

Six atoms run here with no presence gate and no exempt path: G-CON-EXCLUSION,
G-CON-FREEZE, G-CON-NEARDUP, G-CON-STRIP, G-CON-EMPTY, and G-CON-RECORD.

The ordering inside every atom is fixed by step 8i and is the whole point of the
family. Each atom first resolves the ENGRAM-owned roots by identity and immutable
digest, then derives its own result from committed bundle bytes, and only then
compares that derived result against whatever the producer claimed. A FORGE
outcome, a computed neighbour, a match record, and an author pass assertion are
never evidence. The shipped provenance carrier is a permitted one-way
producer-claim channel precisely because it can only lower a disposition, so
carrier agreement never raises one.

The governing situation at this root is worth stating plainly, because it decides
whether these atoms are live instruments or broken ones. The ENGRAM roots carry
per-unit determinations for three units that are not resident here, and every
resident carrier records its own screening roots as unsupplied and its own
screening atoms as unresolvable-root. What is absent is the producer's
determination. It is not the auditor's ability to derive one. The roots
themselves resolve: the exclusion list is pinned and carries its baseline rows,
and the near-duplicate corpus is pinned over its unit set with a measured floor
and a pinned calibration. Exclusion matching and near-duplicate screening are
therefore recomputed here from committed bundle bytes and report real derived
numbers. Reporting them as inert would be a broken instrument capping at BLOCK
under verifier principle 7, and would also be false.

Only the freeze atom is genuinely underivable. Step 8i requires the
task-generating-event timestamp, meaning issue creation or the bug-introducing
change, and explicitly refuses a rewritable commit timestamp as a substitute.
Every resident carrier records that timestamp as null. The commit timestamp is
still recorded here, labelled inadmissible, because the comparison it would lose
is the aggravating context a reviewer needs.
"""

from __future__ import annotations

import datetime
import json
import re
import sys
import tomllib
import unicodedata
from pathlib import Path
from typing import Any

import yaml

import core
from core import (
    Bucket,
    CoverageGap,
    Disposition,
    Finding,
    InstrumentResult,
    Severity,
    Standing,
)
from registry import REGISTRY, Category, EvidenceClass, Instrument

EXCLUSION_INSTRUMENT = "G-CON-EXCLUSION"
FREEZE_INSTRUMENT = "G-CON-FREEZE"
NEARDUP_INSTRUMENT = "G-CON-NEARDUP"
STRIP_INSTRUMENT = "G-CON-STRIP"
EMPTY_INSTRUMENT = "G-CON-EMPTY"
RECORD_INSTRUMENT = "G-CON-RECORD"

CONTAMINATION_CLASS = "contamination-screening"
ROOT_GOVERNANCE_CLASS = "screening-root-governance"
CARRIER_CLASS = "provenance-carrier-integrity"

PROVENANCE_CARRIER = "solution/provenance.yaml"
PROVENANCE_SIGNATURE = "solution/provenance.sig"
INSTRUCTION_CARRIER = "instruction.md"
FIX_CARRIER = "solution/fix.patch"
MANIFEST_CARRIER = "task.toml"

ROOT_DIRECTORY = Path("..") / ".memory" / "roots"
VIEW_RELATIVE = Path("..") / ".memory" / "crucible_view.yaml"

EXCLUSION_ROOT = "exclusion_list.json"
FREEZE_ROOT = "freeze_table.json"
NEARDUP_INDEX_ROOT = "neardup_index.json"
NEARDUP_CALIBRATION_ROOT = "neardup_calibration.json"
NEARDUP_CORPUS_ROOT = "neardup_corpus.json"
ATTESTATION_ROOT = "source_attestation.json"

SHINGLE_WIDTH = 7
NEARDUP_THRESHOLD = 0.3
NEARDUP_REVIEW_THRESHOLD = 0.15

AGENT_VISIBLE_SUBTREES = ("environment", INSTRUCTION_CARRIER)
VERIFIER_SUBTREES = ("tests",)
PRIVATE_SUBTREES = ("solution", "trajectories")

HISTORY_MARKERS = (
    ".git/objects",
    ".git/refs",
    ".git/logs",
    ".git/shallow",
    ".git/objects/info/alternates",
    ".git/worktrees",
    ".pack",
    ".idx",
)
REMOTE_CONFIGURATION = (
    "url = https://github.com",
    "url = git@",
    "[remote ",
    "credential.helper",
    ".git-credentials",
    "netrc",
)
REMOTE_ASSERTION = (
    'test -z "$(git remote)"',
    "remote absence asserted",
)
THREAD_MARKERS = (
    "issue_comments",
    "from mailer-daemon",
    "api.github.com/repos",
    "gh issue view",
    "gh pr view",
    ".mbox",
)
PERMITTED_DERIVATIVES = ("<issue_description>",)

_UPSTREAM_REFERENCE = re.compile(
    r"(?:github\.com/[\w.-]+/[\w.-]+/(?:pull|issues)/\d+|#\d{3,})", re.IGNORECASE
)
_INTERFACE_SIGNATURE = re.compile(r"^\s*(?:def |class |[\w.]+\s*:\s*[A-Z]\w*\[|@\w+|--[\w-]+)")


def classify_fix_fragment(fragment: str) -> str:
    """Separate an upstream-identity disclosure from a declared interface signature.

    Fix absence retains any fragment of the private fix diff reachable from the
    agent closure. The two kinds of hit are not the same defect. A fragment
    carrying an upstream pull-request or issue reference discloses where the real
    fix lives, which step 8i names as the reason the provenance carrier is
    private at all. A bare signature line is what an approved names-only
    interface specification is made of, so it is retained with its basis recorded
    rather than treated as a disclosure.
    """
    if _UPSTREAM_REFERENCE.search(fragment):
        return "upstream-identity-disclosure"
    if _INTERFACE_SIGNATURE.match(fragment):
        return "interface-signature"
    return "fix-body-fragment"


class LeafKind:
    """Value kinds a closed-schema leaf may carry.

    Step 8i makes the carrier schema exhaustive and closed and states that no
    field accepts free-form prose. Declaring the admissible kind for every leaf
    is how that clause becomes a deterministic check rather than a reading.
    """

    TOKEN = "token"
    DIGEST = "digest"
    IDENTITY = "identity"
    TIMESTAMP = "timestamp"
    INTEGER = "integer"
    REWARD = "reward"


CARRIER_SCHEMA: dict[str, Any] = {
    "schema": LeafKind.IDENTITY,
    "instance_id": LeafKind.IDENTITY,
    "slot_id": LeafKind.IDENTITY,
    "source": {
        "origin": LeafKind.TOKEN,
        "source_kind": LeafKind.TOKEN,
        "repository": LeafKind.IDENTITY,
        "repository_canonical_identity": LeafKind.IDENTITY,
        "repository_identity_state": LeafKind.TOKEN,
        "fork_ancestry_snapshot_digest": LeafKind.DIGEST,
        "fork_ancestry_state": LeafKind.TOKEN,
        "license": LeafKind.TOKEN,
        "base_commit_sha": LeafKind.DIGEST,
        "upstream_change_sha": LeafKind.IDENTITY,
        "upstream_change_committed_at": LeafKind.TIMESTAMP,
        "task_generating_event_at": LeafKind.TIMESTAMP,
        "task_generating_event_state": LeafKind.TOKEN,
        "ancestry_attestation_digest": LeafKind.DIGEST,
        "ancestry_attestation_signer": LeafKind.IDENTITY,
        "event_attestation_digest": LeafKind.DIGEST,
        "event_attestation_signer": LeafKind.IDENTITY,
        "attestation_state": LeafKind.TOKEN,
    },
    "measurement_provenance": {
        "state": LeafKind.TOKEN,
        "basis": LeafKind.TOKEN,
    },
    "screening_roots": {
        "exclusion_list": {
            "identity": LeafKind.IDENTITY,
            "digest": LeafKind.DIGEST,
            "state": LeafKind.TOKEN,
        },
        "freeze_date_table": {
            "identity": LeafKind.IDENTITY,
            "digest": LeafKind.DIGEST,
            "state": LeafKind.TOKEN,
        },
        "near_duplicate_index": {
            "identity": LeafKind.IDENTITY,
            "digest": LeafKind.DIGEST,
            "state": LeafKind.TOKEN,
        },
        "source_attestation_trust_root": {
            "identity": LeafKind.IDENTITY,
            "digest": LeafKind.DIGEST,
            "state": LeafKind.TOKEN,
        },
    },
    "atoms": {
        "exclusion_matching": {
            "applicability": LeafKind.TOKEN,
            "state": LeafKind.TOKEN,
            "result_digest": LeafKind.DIGEST,
        },
        "freeze_holdout": {
            "applicability": LeafKind.TOKEN,
            "state": LeafKind.TOKEN,
            "result_digest": LeafKind.DIGEST,
        },
        "near_duplicate_screening": {
            "applicability": LeafKind.TOKEN,
            "state": LeafKind.TOKEN,
            "result_digest": LeafKind.DIGEST,
        },
        "sanitization": {
            "applicability": LeafKind.TOKEN,
            "state": LeafKind.TOKEN,
            "result_digest": LeafKind.DIGEST,
        },
        "empty_submission_validation": {
            "applicability": LeafKind.TOKEN,
            "state": LeafKind.TOKEN,
            "result_digest": LeafKind.DIGEST,
        },
    },
    "sanitization_closure": {
        "agent_visible_paths": LeafKind.INTEGER,
        "image_digest": LeafKind.DIGEST,
        "history_absence": LeafKind.TOKEN,
        "remote_absence": LeafKind.TOKEN,
        "thread_absence": LeafKind.TOKEN,
        "fix_absence": LeafKind.TOKEN,
        "closure_identity": LeafKind.TOKEN,
    },
    "empty_submission": {
        "invocation": LeafKind.TOKEN,
        "measured_reward": LeafKind.REWARD,
        "requirement": LeafKind.TOKEN,
    },
    "instrument_versions": {
        "normalization_domain": LeafKind.IDENTITY,
        "emitter": LeafKind.IDENTITY,
        "recompute": LeafKind.IDENTITY,
    },
    "screening_measured_at": LeafKind.TIMESTAMP,
    "screening_interval_days": LeafKind.INTEGER,
    "screening_expires_at": LeafKind.TIMESTAMP,
    "binding": {
        "canonical_bundle_hash": LeafKind.DIGEST,
        "pinned_image_digest": LeafKind.DIGEST,
        "binding_envelope": LeafKind.TOKEN,
    },
}

PROSE_WORD_CEILING = 8

_HUNK_HEADER = re.compile(r"^@@[^@]*@@.*$", re.MULTILINE)
_FILE_HEADER = re.compile(r"^(?:diff --git |index |--- |\+\+\+ ).*$", re.MULTILINE)
_HEX_OBJECT_ID = re.compile(r"\b[0-9a-f]{7,}\b")
_WORD = re.compile(r"\w+")
_ISSUE_BLOCK = re.compile(
    r"<issue_description>(.*?)</issue_description>", re.DOTALL | re.IGNORECASE
)


def strip_diff_coordinates(text: str) -> str:
    """Remove diff hunk headers and file headers, per the bound normalization."""
    without_hunks = _HUNK_HEADER.sub(" ", text)
    return _FILE_HEADER.sub(" ", without_hunks)


def strip_hex_object_ids(text: str) -> str:
    """Remove runs of hex that encode object identity rather than content."""
    return _HEX_OBJECT_ID.sub(" ", text)


def bound_normalize(text: str) -> str:
    """Apply the normalization the near-duplicate root binds, in its stated order."""
    folded = unicodedata.normalize("NFKC", text).casefold()
    return strip_hex_object_ids(strip_diff_coordinates(folded))


def bound_tokens(text: str) -> list[str]:
    return _WORD.findall(bound_normalize(text))


def raw_tokens(text: str) -> list[str]:
    return text.split()


def shingles(tokens: list[str], width: int = SHINGLE_WIDTH) -> set[tuple[str, ...]]:
    if len(tokens) < width:
        return set()
    return {tuple(tokens[index : index + width]) for index in range(len(tokens) - width + 1)}


def jaccard(left: set[tuple[str, ...]], right: set[tuple[str, ...]]) -> float:
    if not left or not right:
        return 0.0
    union = len(left | right)
    if union == 0:
        return 0.0
    return len(left & right) / float(union)


def instruction_payload(text: str) -> tuple[str, str]:
    """Extract the payload the near-duplicate corpus indexes, with its basis.

    The corpus records its extraction rule as the issue description block for
    bundle-shaped sources. Falling back to the whole file when that block is
    absent is recorded rather than silent, because the fallback compares a
    different representation than the corpus indexed.
    """
    match = _ISSUE_BLOCK.search(text)
    if match:
        return match.group(1), "issue-description-block"
    return text, "whole-file-fallback"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except yaml.YAMLError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def load_root(base: Path, name: str) -> tuple[dict[str, Any], str | None, str]:
    """Resolve one ENGRAM root by path, returning its payload, digest, and state."""
    path = (base / ROOT_DIRECTORY / name).resolve()
    if not path.is_file():
        return {}, None, "unresolvable"
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}, None, "malformed"
    if not isinstance(payload, dict):
        return {}, None, "malformed"
    return payload, core.sha256_path(path), "resolved"


def parse_instant(value: Any) -> datetime.datetime | None:
    """Parse an RFC 3339 instant into an aware UTC datetime, or None."""
    if not isinstance(value, str) or not value.strip():
        return None
    token = value.strip()
    if token.endswith("Z"):
        token = token[:-1] + "+00:00"
    try:
        parsed = datetime.datetime.fromisoformat(token)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.UTC)
    return parsed.astimezone(datetime.UTC)


def freshness(carrier: dict[str, Any], now: datetime.datetime) -> dict[str, Any]:
    """Compute step 8n freshness from exact UTC instants, never truncated dates."""
    origin = parse_instant(carrier.get("screening_measured_at"))
    interval = carrier.get("screening_interval_days")
    declared_expiry = parse_instant(carrier.get("screening_expires_at"))
    derived_expiry = None
    if origin is not None and isinstance(interval, int):
        derived_expiry = origin + datetime.timedelta(days=interval)
    overdue = None
    if derived_expiry is not None:
        overdue = now >= derived_expiry
    agrees = None
    if derived_expiry is not None and declared_expiry is not None:
        agrees = derived_expiry == declared_expiry
    return {
        "origin": origin.isoformat() if origin else None,
        "interval_days": interval if isinstance(interval, int) else None,
        "declared_expiry": declared_expiry.isoformat() if declared_expiry else None,
        "derived_expiry": derived_expiry.isoformat() if derived_expiry else None,
        "comparison_instant": now.isoformat(),
        "overdue": overdue,
        "declared_expiry_agrees": agrees,
    }


def bundle_carrier(bundle: Path) -> dict[str, Any]:
    return load_yaml(bundle / PROVENANCE_CARRIER)


def agent_visible_files(bundle: Path) -> list[Path]:
    """Re-derive the agent-facing closure from committed bytes alone.

    The closure is derived from the two committed Dockerfiles rather than
    assumed. The environment Dockerfile builds the agent image and copies in the
    sanitize entrypoint and a build context it then removes; it never copies the
    tests tree. The tests Dockerfile builds a separate verifier image from the
    already sanitized agent image and copies the tests tree into it there. The
    tests tree is therefore verifier-side and is not agent-facing, which is what
    the carrier means when it declares two agent-visible paths.
    """
    resolved: list[Path] = []
    for entry in AGENT_VISIBLE_SUBTREES:
        candidate = bundle / entry
        if candidate.is_file():
            resolved.append(candidate)
        elif candidate.is_dir():
            resolved.extend(sorted(path for path in candidate.rglob("*") if path.is_file()))
    return resolved


def _registered(
    name: str,
    capability: str,
    evidence_class: EvidenceClass,
    conditions: tuple[str, ...],
    notes: str,
) -> Instrument:
    return REGISTRY.register(
        Instrument(
            name=name,
            category=Category.CONTAMINATION,
            binary="",
            ecosystems=("*",),
            timeout_seconds=600.0,
            required_conditions=conditions,
            critical_capability=capability,
            evidence_class=evidence_class,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.BLOCK,
            database_pin="engram roots pinned by immutable digest",
            notes=notes,
        )
    )


_registered(
    EXCLUSION_INSTRUMENT,
    "detects a resident unit already present in a named evaluation set",
    EvidenceClass.SET_RELATION,
    ("exclusion list root resolves", "committed bundle bytes readable"),
    "recomputes canonical repository identity, fork ancestry closure, and base commit sha",
)
_registered(
    FREEZE_INSTRUMENT,
    "detects a unit whose generating event precedes an applicable freeze cutoff",
    EvidenceClass.SET_RELATION,
    ("freeze table root resolves", "task generating event timestamp resolvable"),
    "requires the generating event instant; a rewritable commit timestamp is inadmissible",
)
_registered(
    NEARDUP_INSTRUMENT,
    "detects a near-duplicate neighbour at or above the bound threshold",
    EvidenceClass.RECOMPUTED_DIGEST,
    ("near duplicate index and corpus roots resolve", "committed bundle bytes readable"),
    "recomputes jaccard over seven token shingles across every indexed representation",
)
_registered(
    STRIP_INSTRUMENT,
    "detects history, remote, thread, or fix material surviving into the agent closure",
    EvidenceClass.SET_RELATION,
    ("agent facing closure resolvable", "pinned image layers resolvable"),
    "merged filesystem resolution alone never satisfies history absence",
)
_registered(
    EMPTY_INSTRUMENT,
    "detects an empty submission that resolves a graded target or earns above zero",
    EvidenceClass.EXECUTION_REPLAY,
    ("sanitized image resolvable at pinned digest", "frozen checker set resolvable"),
    "distinct from G-VER-BASELINE, which grades the unmodified base rather than a submission",
)
_registered(
    RECORD_INSTRUMENT,
    "detects a provenance carrier that is absent, unsigned, malformed, or unreconciled",
    EvidenceClass.EXTERNAL_ATTESTATION,
    ("carrier present and parseable", "external trust root resolvable"),
    "the atom result must live in the external signed proof and not in the carrier",
)


def _run_exclusion(base: Path, bundles: list[Path], now: datetime.datetime) -> InstrumentResult:
    """Recompute the three exclusion relations from committed bytes.

    The relations are canonical repository identity resolved through renames and
    transfers, membership of any ancestor in the full fork-ancestry closure, and
    the base commit sha. Repository-level presence alone is not a match under a
    root whose stated relation is exact org, repo, and pull-request identity, so
    a screened repository that carries no matching instance is reported as the
    partial resolution it is rather than as a clean screen.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    root, digest, state = load_root(base, EXCLUSION_ROOT)
    if state != "resolved":
        gaps.append(
            CoverageGap(
                gap_id="D-CON-EXCLUSION-ROOT-UNRESOLVED",
                instrument=EXCLUSION_INSTRUMENT,
                surface="task_corpus",
                reason="exclusion-root-unresolvable",
                caps=Disposition.HOLD,
                statement=(
                    "The exclusion list root did not resolve to a parseable document, so no "
                    "exclusion relation could be recomputed for any resident bundle."
                ),
            )
        )
        return InstrumentResult(
            instrument=EXCLUSION_INSTRUMENT,
            ran=False,
            gaps=gaps,
            standing=Standing.INSUFFICIENT_EVIDENCE,
            notes={"root_state": state},
        )

    authority_mode = root.get("authority_mode")
    if authority_mode == "replace":
        requirements_present = (base / "requirements").is_dir()
        if not requirements_present:
            findings.append(
                Finding(
                    finding_id="F-CON-EXCLUSION-REPLACE-UNSELECTED",
                    instrument=EXCLUSION_INSTRUMENT,
                    critical_class=ROOT_GOVERNANCE_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject="project",
                    statement=(
                        "The exclusion root declares replace authority mode, which removes "
                        "baseline rows, but no requirements surface exists at this root to "
                        "select it explicitly."
                    ),
                    evidence={"authority_mode": authority_mode, "root_digest": digest},
                )
            )

    candidates = root.get("screened_candidates") or []
    screened_repositories = set(root.get("screened_repositories") or [])
    candidate_commits = {
        str(entry.get("base_commit")) for entry in candidates if isinstance(entry, dict)
    }
    candidate_instances = {
        str(entry.get("instance_id")) for entry in candidates if isinstance(entry, dict)
    }
    sets = [entry for entry in (root.get("sets") or []) if isinstance(entry, dict)]

    rows: list[dict[str, Any]] = []
    ancestry_unresolved: list[str] = []
    pr_identity_unresolved: list[str] = []

    for bundle in bundles:
        carrier = bundle_carrier(bundle)
        source = carrier.get("source") or {}
        uuid = bundle.name
        repository = source.get("repository")
        canonical = source.get("repository_canonical_identity")
        canonical_state = source.get("repository_identity_state")
        base_commit = source.get("base_commit_sha")
        ancestry_state = source.get("fork_ancestry_state")
        ancestry_digest = source.get("fork_ancestry_snapshot_digest")
        instance_id = carrier.get("instance_id")

        identity_match = canonical in {
            str(entry.get("repository_canonical_identity"))
            for entry in candidates
            if isinstance(entry, dict)
        }
        commit_match = str(base_commit) in candidate_commits
        instance_match = str(instance_id) in candidate_instances
        repository_screened = repository in screened_repositories

        if ancestry_state != "resolved" or not core.is_hex64(str(ancestry_digest or "")):
            ancestry_unresolved.append(uuid)

        if repository_screened and not instance_match:
            pr_identity_unresolved.append(uuid)

        if identity_match or commit_match or instance_match:
            findings.append(
                Finding(
                    finding_id=f"F-CON-EXCLUSION-MATCH-{uuid[:8]}",
                    instrument=EXCLUSION_INSTRUMENT,
                    critical_class=CONTAMINATION_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement=(
                        "A recomputed exclusion relation matched a row in the pinned exclusion "
                        "root, so this unit is present in a named evaluation set."
                    ),
                    evidence={
                        "canonical_identity_match": identity_match,
                        "base_commit_match": commit_match,
                        "instance_identity_match": instance_match,
                        "root_digest": digest,
                    },
                )
            )

        rows.append(
            {
                "uuid": uuid,
                "repository": repository,
                "repository_canonical_identity": canonical,
                "repository_identity_state": canonical_state,
                "base_commit_sha": base_commit,
                "instance_id": instance_id,
                "canonical_identity_match": identity_match,
                "base_commit_match": commit_match,
                "instance_identity_match": instance_match,
                "repository_in_screened_set": repository_screened,
                "fork_ancestry_state": ancestry_state,
                "carrier_claimed_state": (
                    (carrier.get("atoms") or {}).get("exclusion_matching") or {}
                ).get("state"),
            }
        )

    if ancestry_unresolved:
        gaps.append(
            CoverageGap(
                gap_id="D-CON-EXCLUSION-ANCESTRY-UNRESOLVED",
                instrument=EXCLUSION_INSTRUMENT,
                surface="task_corpus",
                reason="fork-ancestry-closure-unresolvable",
                caps=Disposition.HOLD,
                statement=(
                    "The second exclusion relation requires membership of any ancestor in the "
                    "full fork-ancestry closure rather than the direct parent alone. No "
                    "committed byte at this root resolves that closure for the named bundles, "
                    "so the relation was computed over the direct identity only and the "
                    "ancestor arm remains underivable."
                ),
                subject=",".join(ancestry_unresolved),
            )
        )

    if pr_identity_unresolved:
        gaps.append(
            CoverageGap(
                gap_id="D-CON-EXCLUSION-PR-IDENTITY-UNRESOLVED",
                instrument=EXCLUSION_INSTRUMENT,
                surface="task_corpus",
                reason="pull-request-identity-unresolvable",
                caps=Disposition.HOLD,
                statement=(
                    "The exclusion root states its relation as exact organization, repository, "
                    "and pull-request identity. The named bundles sit in a repository the root "
                    "already screened, but no committed byte carries the pull-request numbers "
                    "their spans cover, so repository-level absence of a match is not the same "
                    "as an exact-identity clean screen."
                ),
                subject=",".join(pr_identity_unresolved),
            )
        )

    gaps.append(
        CoverageGap(
            gap_id="D-CON-ATTESTATION-UNAVAILABLE",
            instrument=EXCLUSION_INSTRUMENT,
            surface="task_corpus",
            reason="attestation-unavailable",
            caps=Disposition.HOLD,
            statement=(
                "Step 8k requires this atom to re-resolve a signed platform attestation against "
                "the source attestation trust root and reconcile the attested value against the "
                "declaration. That trust root is absent from the projection, and every carrier "
                "records attestation_state as attestation-unavailable, so the reconciliation "
                "did not run."
            ),
        )
    )

    shipped_states = {
        bundle.name: (
            (bundle_carrier(bundle).get("screening_roots") or {}).get("exclusion_list") or {}
        ).get("state")
        for bundle in bundles
    }
    if any(value != "resolved" for value in shipped_states.values()):
        gaps.append(
            CoverageGap(
                gap_id="D-CON-SHIPPED-ROOT-UNRESOLVABLE",
                instrument=EXCLUSION_INSTRUMENT,
                surface="task_corpus",
                reason="shipped-under-root-unresolvable",
                caps=Disposition.HOLD,
                statement=(
                    "Step 8l requires recording the shipped-under root digest, the currently "
                    "effective root digest, and whether they differ. Every resident carrier "
                    "records its shipped-under exclusion root as unsupplied with no digest, so "
                    "the differential re-screen has no shipped-under side to compare against."
                ),
            )
        )

    standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=EXCLUSION_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "root_digest": digest,
            "authority_mode": authority_mode,
            "declared_set_count": len(sets),
            "screened_candidate_count": len(candidates),
            "screened_repositories": sorted(screened_repositories),
            "effective_root_digest": digest,
            "shipped_under_root_state": shipped_states,
            "bundles": rows,
            "freshness": {
                bundle.name: freshness(bundle_carrier(bundle), now) for bundle in bundles
            },
        },
    )


def _run_freeze(base: Path, bundles: list[Path], now: datetime.datetime) -> InstrumentResult:
    """Compare the generating event instant against every applicable freeze row.

    The admissible input is the task-generating-event timestamp, meaning issue
    creation or the bug-introducing change. The upstream commit timestamp is
    recorded alongside it and labelled inadmissible, because a commit timestamp
    is rewritable and step 8i refuses a value available only from a mutable
    source.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    freeze_root, freeze_digest, freeze_state = load_root(base, FREEZE_ROOT)
    exclusion_root, _, exclusion_state = load_root(base, EXCLUSION_ROOT)
    if freeze_state != "resolved":
        gaps.append(
            CoverageGap(
                gap_id="D-CON-FREEZE-ROOT-UNRESOLVED",
                instrument=FREEZE_INSTRUMENT,
                surface="task_corpus",
                reason="freeze-root-unresolvable",
                caps=Disposition.HOLD,
                statement="The freeze date table root did not resolve to a parseable document.",
            )
        )
        return InstrumentResult(
            instrument=FREEZE_INSTRUMENT,
            ran=False,
            gaps=gaps,
            standing=Standing.INSUFFICIENT_EVIDENCE,
            notes={"root_state": freeze_state},
        )

    cutoffs = [
        entry for entry in (freeze_root.get("per_set_cutoffs") or []) if isinstance(entry, dict)
    ]
    cutoff_sets = {str(entry.get("set_identity")) for entry in cutoffs}
    named_sets: list[dict[str, Any]] = []
    if exclusion_state == "resolved":
        named_sets = [
            entry for entry in (exclusion_root.get("sets") or []) if isinstance(entry, dict)
        ]
    missing_rows = [
        str(entry.get("set_identity"))
        for entry in named_sets
        if str(entry.get("set_identity")) not in cutoff_sets
        and entry.get("coverage") != "not_applicable"
    ]
    if missing_rows:
        findings.append(
            Finding(
                finding_id="F-CON-FREEZE-ROW-MISSING",
                instrument=FREEZE_INSTRUMENT,
                critical_class=ROOT_GOVERNANCE_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject="project",
                statement=(
                    "A named set covered by the exclusion root carries no versioned freeze row, "
                    "so no cutoff binds any resident unit against that set."
                ),
                evidence={
                    "sets_without_freeze_row": sorted(missing_rows),
                    "freeze_root_digest": freeze_digest,
                },
            )
        )

    rows: list[dict[str, Any]] = []
    underivable: list[str] = []
    for bundle in bundles:
        carrier = bundle_carrier(bundle)
        source = carrier.get("source") or {}
        uuid = bundle.name
        event_at = parse_instant(source.get("task_generating_event_at"))
        event_state = source.get("task_generating_event_state")
        commit_at = parse_instant(source.get("upstream_change_committed_at"))
        inadmissible_violations = []
        if commit_at is not None:
            for entry in cutoffs:
                cutoff = parse_instant(entry.get("cutoff"))
                if cutoff is not None and commit_at <= cutoff:
                    inadmissible_violations.append(
                        {
                            "set_identity": entry.get("set_identity"),
                            "cutoff": entry.get("cutoff"),
                        }
                    )
        if event_at is None:
            underivable.append(uuid)
        else:
            violated = []
            for entry in cutoffs:
                cutoff = parse_instant(entry.get("cutoff"))
                if cutoff is not None and not event_at > cutoff:
                    violated.append(entry.get("set_identity"))
            if violated:
                findings.append(
                    Finding(
                        finding_id=f"F-CON-FREEZE-NOT-LATER-{uuid[:8]}",
                        instrument=FREEZE_INSTRUMENT,
                        critical_class=CONTAMINATION_CLASS,
                        severity=Severity.CRITICAL,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=uuid,
                        statement=(
                            "The task generating event instant is not strictly later than every "
                            "applicable versioned freeze row."
                        ),
                        evidence={"violated_sets": violated},
                    )
                )
        rows.append(
            {
                "uuid": uuid,
                "task_generating_event_at": source.get("task_generating_event_at"),
                "task_generating_event_state": event_state,
                "inadmissible_commit_timestamp": source.get("upstream_change_committed_at"),
                "inadmissible_comparison_violations": inadmissible_violations,
                "carrier_claimed_state": (
                    (carrier.get("atoms") or {}).get("freeze_holdout") or {}
                ).get("state"),
            }
        )

    if underivable:
        gaps.append(
            CoverageGap(
                gap_id="D-CON-FREEZE-UNDERIVABLE",
                instrument=FREEZE_INSTRUMENT,
                surface="task_corpus",
                reason="no-admissible-generating-event-timestamp",
                caps=Disposition.HOLD,
                statement=(
                    "Step 8i requires the task-generating-event timestamp, meaning issue "
                    "creation or the bug-introducing change, and refuses a rewritable commit "
                    "timestamp as a substitute. Every named bundle records that timestamp as "
                    "null with state unresolved, so the freeze comparison is underivable. The "
                    "commit timestamps are recorded in the notes as inadmissible context, and "
                    "at least one of them precedes a listed cutoff."
                ),
                subject=",".join(underivable),
            )
        )

    gaps.append(
        CoverageGap(
            gap_id="D-CON-FREEZE-ATTESTATION-UNAVAILABLE",
            instrument=FREEZE_INSTRUMENT,
            surface="task_corpus",
            reason="attestation-unavailable",
            caps=Disposition.HOLD,
            statement=(
                "Step 8k requires this atom to re-resolve its signed platform attestation "
                "against the source attestation trust root. That root is absent from the "
                "projection, so the attested event time was never reconciled against the "
                "declared one."
            ),
        )
    )

    standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=FREEZE_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "freeze_root_digest": freeze_digest,
            "cutoff_rows": cutoffs,
            "named_sets_without_freeze_row": sorted(missing_rows),
            "bundles": rows,
        },
    )


def _representations(bundle: Path) -> dict[str, str]:
    """The representations step 8i names, read from committed bundle bytes."""
    instruction = read_text(bundle / INSTRUCTION_CARRIER)
    payload, basis = instruction_payload(instruction)
    fix_patch = read_text(bundle / FIX_CARRIER)
    config = bundle / "tests" / "config.json"
    graded = ""
    if config.is_file():
        try:
            parsed = json.loads(config.read_text(encoding="utf-8", errors="replace"))
            targets = list(parsed.get("f2p_tests") or []) + list(parsed.get("p2p_tests") or [])
            graded = "\n".join(str(item) for item in targets)
        except (OSError, json.JSONDecodeError):
            graded = ""
    return {
        "instruction": payload,
        "instruction_extraction": basis,
        "fix_patch": fix_patch,
        "graded_target_set": graded,
        "combined": payload + "\n" + fix_patch,
    }


def _run_neardup(base: Path, bundles: list[Path], now: datetime.datetime) -> InstrumentResult:
    """Recompute containment against the pinned index over every representation.

    Step 8j requires each representation to be compared raw and under every bound
    semantic-preserving normalization. A neighbour at or above the bound
    threshold is a hash-bound critical floor breach capping at BLOCK. A neighbour
    in the review band opens a mandatory recorded semantic adjudication, and an
    unadjudicated review-band neighbour is a coverage gap.

    The pinned corpus publishes each unit as a payload digest and a shingle
    count rather than as payload text, so cross-corpus similarity is not
    computable from what the root supplies. Exact payload identity against that
    corpus is computable and is performed. The resident pairwise comparison is
    fully computable and is performed over every representation in both forms.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    index_root, index_digest, index_state = load_root(base, NEARDUP_INDEX_ROOT)
    corpus_root, corpus_digest, corpus_state = load_root(base, NEARDUP_CORPUS_ROOT)
    calibration_root, calibration_digest, calibration_state = load_root(
        base, NEARDUP_CALIBRATION_ROOT
    )
    if index_state != "resolved":
        gaps.append(
            CoverageGap(
                gap_id="D-CON-NEARDUP-INDEX-UNRESOLVED",
                instrument=NEARDUP_INSTRUMENT,
                surface="task_corpus",
                reason="neardup-index-unreachable",
                caps=Disposition.HOLD,
                statement="The near duplicate index root did not resolve to a parseable document.",
            )
        )
        return InstrumentResult(
            instrument=NEARDUP_INSTRUMENT,
            ran=False,
            gaps=gaps,
            standing=Standing.INSUFFICIENT_EVIDENCE,
            notes={"root_state": index_state},
        )

    threshold = float(index_root.get("neardup_threshold", NEARDUP_THRESHOLD))
    review_threshold = float(index_root.get("neardup_review_threshold", NEARDUP_REVIEW_THRESHOLD))
    width = int(index_root.get("shingle_size", SHINGLE_WIDTH))
    representations = [
        "instruction",
        "fix_patch",
        "combined",
        "graded_target_set",
    ]

    prepared: dict[str, dict[str, Any]] = {}
    for bundle in bundles:
        texts = _representations(bundle)
        entry: dict[str, Any] = {"extraction": texts["instruction_extraction"]}
        for representation in representations:
            body = texts[representation]
            entry[representation] = {
                "normalized": shingles(bound_tokens(body), width),
                "raw": shingles(raw_tokens(body), width),
                "payload_sha256": core.sha256_bytes(body.encode("utf-8", "replace")),
                "normalized_payload_sha256": core.sha256_bytes(
                    bound_normalize(body).encode("utf-8", "replace")
                ),
                "token_count": len(bound_tokens(body)),
            }
        prepared[bundle.name] = entry

    pairwise: list[dict[str, Any]] = []
    review_band: list[dict[str, Any]] = []
    names = [bundle.name for bundle in bundles]
    for left_index in range(len(names)):
        for right_index in range(left_index + 1, len(names)):
            left, right = names[left_index], names[right_index]
            scores: dict[str, dict[str, float]] = {}
            worst = 0.0
            worst_key = ""
            for representation in representations:
                for form in ("normalized", "raw"):
                    value = jaccard(
                        prepared[left][representation][form],
                        prepared[right][representation][form],
                    )
                    scores.setdefault(representation, {})[form] = round(value, 6)
                    if value > worst:
                        worst = value
                        worst_key = f"{representation}.{form}"
            row = {
                "left": left,
                "right": right,
                "scores": scores,
                "max_similarity": round(worst, 6),
                "max_representation": worst_key,
            }
            pairwise.append(row)
            if worst >= threshold:
                findings.append(
                    Finding(
                        finding_id=f"F-CON-NEARDUP-NEIGHBOUR-{left[:8]}-{right[:8]}",
                        instrument=NEARDUP_INSTRUMENT,
                        critical_class=CONTAMINATION_CLASS,
                        severity=Severity.CRITICAL,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=f"{left},{right}",
                        statement=(
                            "A recomputed neighbour scored at or above the bound near-duplicate "
                            "threshold on an indexed representation."
                        ),
                        evidence=row,
                    )
                )
            elif worst >= review_threshold:
                review_band.append(row)

    for row in review_band:
        gaps.append(
            CoverageGap(
                gap_id=f"D-CON-NEARDUP-REVIEW-UNADJUDICATED-{row['left'][:8]}-{row['right'][:8]}",
                instrument=NEARDUP_INSTRUMENT,
                surface="task_corpus",
                reason="review-band-unadjudicated",
                caps=Disposition.HOLD,
                statement=(
                    "Step 8j opens a mandatory recorded semantic adjudication for a neighbour "
                    "from the review threshold up to but excluding the near-duplicate "
                    "threshold. No adjudication record exists for this pair, and a semantic "
                    "adjudication may only lower a disposition and may never certify absence."
                ),
                subject=f"{row['left']},{row['right']}",
            )
        )

    index_entries = [
        entry for entry in (index_root.get("entries") or []) if isinstance(entry, dict)
    ]
    index_instruction_hashes = {str(entry.get("instruction_sha256")) for entry in index_entries}
    index_fix_hashes = {str(entry.get("fix_patch_sha256")) for entry in index_entries}

    corpus_units = []
    corpus_payload_hashes: set[str] = set()
    if corpus_state == "resolved":
        corpus_units = [
            entry for entry in (corpus_root.get("units") or []) if isinstance(entry, dict)
        ]
        corpus_payload_hashes = {str(entry.get("payload_sha256")) for entry in corpus_units}

    identity_rows: list[dict[str, Any]] = []
    repository_neighbours: list[dict[str, Any]] = []
    for bundle in bundles:
        uuid = bundle.name
        carrier = bundle_carrier(bundle)
        instruction_hash = prepared[uuid]["instruction"]["payload_sha256"]
        fix_hash = prepared[uuid]["fix_patch"]["payload_sha256"]
        in_index = instruction_hash in index_instruction_hashes or fix_hash in index_fix_hashes
        in_corpus = instruction_hash in corpus_payload_hashes
        if in_index or in_corpus:
            findings.append(
                Finding(
                    finding_id=f"F-CON-NEARDUP-EXACT-{uuid[:8]}",
                    instrument=NEARDUP_INSTRUMENT,
                    critical_class=CONTAMINATION_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement=(
                        "A recomputed payload digest for this bundle is already present in the "
                        "pinned near-duplicate index or corpus."
                    ),
                    evidence={"in_index": in_index, "in_corpus": in_corpus},
                )
            )
        repository = (carrier.get("source") or {}).get("repository")
        prefix = ""
        if isinstance(repository, str) and "/" in repository:
            owner, name = repository.split("/", 1)
            prefix = f"{owner}__{name}"
        same_repository = []
        if prefix:
            same_repository = [
                {
                    "unit_id": entry.get("unit_id"),
                    "source": entry.get("source"),
                    "shingle_count": entry.get("shingle_count"),
                }
                for entry in corpus_units
                if str(entry.get("identity", "")).startswith(prefix)
            ]
        if same_repository:
            repository_neighbours.append({"uuid": uuid, "units": same_repository})
        identity_rows.append(
            {
                "uuid": uuid,
                "instruction_payload_sha256": instruction_hash,
                "fix_patch_sha256": fix_hash,
                "instruction_extraction": prepared[uuid]["extraction"],
                "present_in_pinned_index": in_index,
                "present_in_pinned_corpus": in_corpus,
                "same_repository_corpus_units": len(same_repository),
                "carrier_claimed_state": (
                    (carrier.get("atoms") or {}).get("near_duplicate_screening") or {}
                ).get("state"),
            }
        )

    if repository_neighbours:
        findings.append(
            Finding(
                finding_id="F-CON-NEARDUP-SAME-REPOSITORY-CORPUS-UNIT",
                instrument=NEARDUP_INSTRUMENT,
                critical_class=CONTAMINATION_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject="project",
                statement=(
                    "The pinned corpus already carries units drawn from the same upstream "
                    "repository as a resident bundle. The corpus publishes each unit as a "
                    "payload digest and a shingle count rather than payload text, so a "
                    "similarity score against those units is not computable from what the root "
                    "supplies, and same-repository presence is therefore recorded as an "
                    "unmeasurable neighbourhood rather than as a clean screen."
                ),
                evidence={"neighbours": repository_neighbours},
            )
        )

    gaps.append(
        CoverageGap(
            gap_id="D-CON-NEARDUP-CORPUS-OPAQUE",
            instrument=NEARDUP_INSTRUMENT,
            surface="task_corpus",
            reason="corpus-publishes-digests-not-payloads",
            caps=Disposition.HOLD,
            statement=(
                "The pinned corpus root publishes each of its units as an identity, a payload "
                "digest, and a shingle count, and publishes no shingle set or payload text. "
                "Exact payload identity against that corpus is computable and was computed. "
                "The similarity score the bound threshold is defined against is not computable "
                "from those bytes, so the cross-corpus arm of this atom is unresolved and a "
                "clean exact-identity result never certifies absence of a near neighbour."
            ),
        )
    )

    if calibration_state != "resolved":
        gaps.append(
            CoverageGap(
                gap_id="D-CON-NEARDUP-CALIBRATION-UNRESOLVED",
                instrument=NEARDUP_INSTRUMENT,
                surface="task_corpus",
                reason="calibration-unresolvable",
                caps=Disposition.HOLD,
                statement="The near duplicate calibration root did not resolve.",
            )
        )

    standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=NEARDUP_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "index_digest": index_digest,
            "corpus_digest": corpus_digest,
            "calibration_digest": calibration_digest,
            "neardup_threshold": threshold,
            "neardup_review_threshold": review_threshold,
            "shingle_size": width,
            "normalizations": index_root.get("neardup_normalizations"),
            "representations_compared": representations,
            "forms_compared": ["normalized", "raw"],
            "resident_pairwise": pairwise,
            "exact_identity": identity_rows,
            "corpus_unit_count": len(corpus_units),
        },
    )


def _names_only_interface_declared(bundle: Path) -> bool:
    """True when the bundle's committed task.toml declares a names-only interface.

    Contract step 8i keeps the fix-absence check fail-closed, but a signature
    fragment that realizes the approved names-only interface specification is
    the approved design rather than a disclosure. The declaration is read from
    committed bundle bytes, never from a producer assertion outside them.
    """
    manifest = bundle / "task.toml"
    if not manifest.is_file():
        return False
    try:
        with manifest.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return False
    spec = data.get("interface_spec")
    if not isinstance(spec, dict):
        return False
    return str(spec.get("mode")) == "names-only"


def _run_strip(base: Path, bundles: list[Path], now: datetime.datetime) -> InstrumentResult:
    """Re-derive the agent-facing closure and run the five absence checks.

    History absence is the one check that cannot be satisfied from what this root
    supplies. Step 8i states that resolving only the merged container filesystem
    does not satisfy history absence, because deleted objects remain recoverable
    from lower layers, and that the shortfall must be recorded as unimplemented
    rather than as a pass. No layer set is resolvable here at all, so the
    shortfall is recorded exactly that way.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    rows: list[dict[str, Any]] = []

    for bundle in bundles:
        uuid = bundle.name
        carrier = bundle_carrier(bundle)
        closure = agent_visible_files(bundle)
        relative = [str(path.relative_to(bundle)) for path in closure]
        blob = "\n".join(read_text(path) for path in closure)
        normalized_blob = bound_normalize(blob)

        history_hits = [marker for marker in HISTORY_MARKERS if marker in "\n".join(relative)]
        remote_hits = [
            marker for marker in REMOTE_CONFIGURATION if marker.casefold() in normalized_blob
        ]
        remote_assertions = [
            marker for marker in REMOTE_ASSERTION if marker.casefold() in normalized_blob
        ]
        thread_hits = [marker for marker in THREAD_MARKERS if marker.casefold() in normalized_blob]

        fix_text = read_text(bundle / FIX_CARRIER)
        fix_fragments = [
            line[1:].strip()
            for line in fix_text.splitlines()
            if line.startswith("+") and not line.startswith("+++") and len(line.strip()) > 40
        ]
        surfaced_fragments = [
            fragment
            for fragment in fix_fragments
            if bound_normalize(fragment) and bound_normalize(fragment) in normalized_blob
        ]

        if remote_hits:
            findings.append(
                Finding(
                    finding_id=f"F-CON-STRIP-REMOTE-{uuid[:8]}",
                    instrument=STRIP_INSTRUMENT,
                    critical_class=CONTAMINATION_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement=(
                        "Remote absence failed: repository remote or credential material is "
                        "reachable from the re-derived agent-facing closure."
                    ),
                    evidence={"markers": remote_hits},
                )
            )
        if thread_hits:
            findings.append(
                Finding(
                    finding_id=f"F-CON-STRIP-THREAD-{uuid[:8]}",
                    instrument=STRIP_INSTRUMENT,
                    critical_class=CONTAMINATION_CLASS,
                    severity=Severity.MEDIUM,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement=(
                        "Thread absence flagged issue or pull-request export material in the "
                        "agent-facing closure. A sanitized instruction is a permitted "
                        "derivative, so the marker set is recorded for adjudication rather than "
                        "asserted as an export capture."
                    ),
                    evidence={"markers": thread_hits},
                )
            )
        classified: dict[str, list[str]] = {}
        for fragment in surfaced_fragments:
            classified.setdefault(classify_fix_fragment(fragment), []).append(fragment)
        disclosures = classified.get("upstream-identity-disclosure", [])
        body_fragments = classified.get("fix-body-fragment", [])
        signatures = classified.get("interface-signature", [])

        signature_adjudication = None
        if disclosures or body_fragments:
            findings.append(
                Finding(
                    finding_id=f"F-CON-STRIP-FIX-{uuid[:8]}",
                    instrument=STRIP_INSTRUMENT,
                    critical_class=CONTAMINATION_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement=(
                        "Fix absence failed: normalized fragments of the privately bound "
                        "post-base fix diff are reachable from the agent-facing closure. The "
                        "disclosing fragments name the upstream pull request the fix landed in, "
                        "so the agent is handed the location of the real change it is being "
                        "asked to reproduce."
                    ),
                    evidence={
                        "upstream_identity_disclosures": len(disclosures),
                        "fix_body_fragments": len(body_fragments),
                        "closure_files": relative,
                        "examples": [
                            fragment[:160] for fragment in (disclosures + body_fragments)[:5]
                        ],
                        "sample_digest": core.sha256_bytes(
                            "\n".join(disclosures + body_fragments).encode("utf-8", "replace")
                        ),
                    },
                )
            )
        elif signatures:
            if _names_only_interface_declared(bundle):
                signature_adjudication = {
                    "outcome": "within-approved-design",
                    "basis": (
                        "the bundle's committed task.toml [interface_spec] declares mode "
                        "names-only, so restating a signature realizes the approved design; "
                        "adjudicated per the operator change request recorded on the feedback "
                        "chain (sequence 11), and no fragment carries an upstream pull-request "
                        "or issue reference"
                    ),
                    "interface_signature_fragments": len(signatures),
                    "examples": [fragment[:160] for fragment in signatures[:5]],
                }
            else:
                findings.append(
                    Finding(
                        finding_id=f"F-CON-STRIP-FIX-SIGNATURE-{uuid[:8]}",
                        instrument=STRIP_INSTRUMENT,
                        critical_class=CONTAMINATION_CLASS,
                        severity=Severity.MEDIUM,
                        caps=Disposition.HOLD,
                        bucket=Bucket.D,
                        subject=uuid,
                        statement=(
                            "Fix absence matched signature lines of the private fix diff in the "
                            "agent-facing statement, and no approved names-only interface "
                            "specification exists for this bundle to place them within the "
                            "approved design. No fragment carries an upstream pull-request or "
                            "issue reference."
                        ),
                        evidence={
                            "interface_signature_fragments": len(signatures),
                            "examples": [fragment[:160] for fragment in signatures[:5]],
                        },
                    )
                )

        verifier_closure = [
            path
            for entry in VERIFIER_SUBTREES
            for path in sorted((bundle / entry).rglob("*"))
            if path.is_file()
        ]
        verifier_blob = bound_normalize("\n".join(read_text(path) for path in verifier_closure))
        verifier_fragments = [
            fragment
            for fragment in fix_fragments
            if bound_normalize(fragment) and bound_normalize(fragment) in verifier_blob
        ]

        declared_paths = (carrier.get("sanitization_closure") or {}).get("agent_visible_paths")
        rows.append(
            {
                "uuid": uuid,
                "closure_file_count": len(relative),
                "closure_digest": core.tree_digest(bundle, relative),
                "declared_agent_visible_paths": declared_paths,
                "history_absence": "unimplemented",
                "history_markers_in_committed_closure": history_hits,
                "remote_absence": "fired" if remote_hits else "unresolved",
                "remote_producer_assertions": remote_assertions,
                "thread_absence": "fired" if thread_hits else "clean",
                "permitted_derivatives_present": [
                    marker
                    for marker in PERMITTED_DERIVATIVES
                    if marker.casefold() in normalized_blob
                ],
                "fix_absence": "fired" if surfaced_fragments else "clean",
                "fix_fragment_classification": {
                    key: len(value) for key, value in sorted(classified.items())
                },
                "fix_fragments_tested": len(fix_fragments),
                "signature_adjudication": signature_adjudication,
                "fix_fragments_in_verifier_tree": len(verifier_fragments),
                "closure_identity": "unresolved",
                "carrier_claimed_state": (
                    (carrier.get("atoms") or {}).get("sanitization") or {}
                ).get("state"),
                "carrier_claimed_result_digest": (
                    (carrier.get("atoms") or {}).get("sanitization") or {}
                ).get("result_digest"),
            }
        )

    gaps.append(
        CoverageGap(
            gap_id="D-CON-STRIP-HISTORY-UNIMPLEMENTED",
            instrument=STRIP_INSTRUMENT,
            surface="containers",
            reason="layer-set-unresolvable",
            caps=Disposition.HOLD,
            statement=(
                "History absence must reject git object databases, packfiles, refs, reflogs, "
                "shallow metadata, alternates, bundles, and worktrees in every unpacked layer "
                "including later-whiteouted content. No image layer set resolves at this root, "
                "and step 8i states that resolving only a merged filesystem does not satisfy "
                "this check because deleted objects remain recoverable from lower layers. The "
                "shortfall is recorded as unimplemented and never as a pass."
            ),
        )
    )
    gaps.append(
        CoverageGap(
            gap_id="D-CON-STRIP-CLOSURE-IDENTITY-UNRESOLVED",
            instrument=STRIP_INSTRUMENT,
            surface="containers",
            reason="closure-identity-unresolvable",
            caps=Disposition.HOLD,
            statement=(
                "Closure identity requires the scanned manifest, configuration, history, and "
                "layer set to equal what the delivery block pinned and what the committed "
                "evidence executed under. No layer or configuration set resolves here, so the "
                "equality was never tested and the re-derived closure covers committed bundle "
                "bytes only."
            ),
        )
    )
    gaps.append(
        CoverageGap(
            gap_id="D-CON-STRIP-NETWORK-POLICY-UNRESOLVED",
            instrument=STRIP_INSTRUMENT,
            surface="containers",
            reason="runtime-network-policy-unobserved",
            caps=Disposition.HOLD,
            statement=(
                "Remote absence must also reject a runtime network policy permitting repository "
                "access, and must reject remotes and credential caches inside the built image. "
                "No committed byte records the enforced policy mode for the evaluated runs, and "
                "the only evidence that the image carries no remote is the build recipe "
                "asserting it, which is a producer claim about an artifact this run cannot "
                "resolve rather than an independent observation."
            ),
        )
    )

    standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=STRIP_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "checks": [
                "history-absence",
                "remote-absence",
                "thread-absence",
                "fix-absence",
                "closure-identity",
            ],
            "agent_visible_subtrees": list(AGENT_VISIBLE_SUBTREES),
            "verifier_subtrees": list(VERIFIER_SUBTREES),
            "private_subtrees": list(PRIVATE_SUBTREES),
            "closure_derivation_basis": (
                "the environment Dockerfile builds the agent image and copies only the sanitize "
                "entrypoint and a build context it later removes, while the tests Dockerfile "
                "builds a separate verifier image from the already sanitized agent image and "
                "copies the tests tree into that image instead, so the tests tree is verifier "
                "side and is not part of the agent-facing closure"
            ),
            "verifier_tree_observation": (
                "fragments of the post-base fix diff are present in the verifier-side rubric "
                "file, which is expected because the rubric probes are literal golden strings "
                "drawn from the fix, and is recorded here as an observation rather than as a "
                "leak because that file is not reachable from the agent-facing closure"
            ),
            "bundles": rows,
        },
    )


def _run_empty(base: Path, bundles: list[Path], now: datetime.datetime) -> InstrumentResult:
    """Derive the empty-submission outcome, and gap the replay that cannot run.

    This atom is not G-VER-BASELINE. Baseline grades the unmodified base and
    requires the preserve set green. This atom replays an empty submission
    through the bound invocation and requires every intended fail-to-pass target
    to remain unresolved with the bound reward schema yielding exactly zero.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    rows: list[dict[str, Any]] = []
    unreplayable: list[str] = []

    try:
        import liveexec
    except ImportError:
        liveexec = None

    for bundle in bundles:
        uuid = bundle.name
        carrier = bundle_carrier(bundle)
        config_path = bundle / "tests" / "config.json"
        f2p: list[str] = []
        if config_path.is_file():
            try:
                parsed = json.loads(config_path.read_text(encoding="utf-8", errors="replace"))
                f2p = [str(item) for item in (parsed.get("f2p_tests") or [])]
            except (OSError, json.JSONDecodeError):
                f2p = []
        manifest = read_text(bundle / MANIFEST_CARRIER)
        digest_pinned = "@sha256:" in manifest
        if not f2p:
            findings.append(
                Finding(
                    finding_id=f"F-CON-EMPTY-NO-TARGETS-{uuid[:8]}",
                    instrument=EMPTY_INSTRUMENT,
                    critical_class=CONTAMINATION_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement=(
                        "The frozen checker set declares no fail-to-pass target, so an empty "
                        "submission cannot be shown to leave any intended target unresolved."
                    ),
                    evidence={"config": str(config_path.relative_to(bundle))},
                )
            )
        replay = None
        if liveexec is not None:
            replay = liveexec.empty_run(base, bundle)
        if replay is not None and replay.get("status") == liveexec.STATUS_MEASURED:
            measured = replay.get("reward")
            components = replay.get("components") or {}
            resolved = components.get("targets_resolved")
            if measured != 0.0 or (isinstance(resolved, int) and resolved > 0):
                findings.append(
                    Finding(
                        finding_id=f"F-CON-EMPTY-NONZERO-{uuid[:8]}",
                        instrument=EMPTY_INSTRUMENT,
                        critical_class=CONTAMINATION_CLASS,
                        severity=Severity.CRITICAL,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=uuid,
                        statement=(
                            "The empty submission replayed through the bound invocation inside "
                            "the pinned sanitized image did not yield exactly zero with every "
                            "fail-to-pass target unresolved."
                        ),
                        evidence={
                            "measured_reward": measured,
                            "measured_reason": replay.get("reason"),
                            "targets_resolved": resolved,
                        },
                    )
                )
        else:
            unreplayable.append(uuid)
        rows.append(
            {
                "uuid": uuid,
                "declared_f2p_targets": len(f2p),
                "measured_empty_reward": (replay or {}).get("reward"),
                "measured_empty_reason": (replay or {}).get("reason"),
                "measured_empty_status": (replay or {}).get("status"),
                "static_expected_reward": "0.0",
                "static_basis": (
                    "with no working-tree change the submission diff is empty, every declared "
                    "fail-to-pass target resolves to a non-PASS verdict, and the committed "
                    "reward formula divides a zero hit count by the declared target count"
                ),
                "image_digest_pinned_in_manifest": digest_pinned,
                "carrier_claimed_measured_reward": (carrier.get("empty_submission") or {}).get(
                    "measured_reward"
                ),
                "carrier_claimed_state": (
                    (carrier.get("atoms") or {}).get("empty_submission_validation") or {}
                ).get("state"),
            }
        )

    if unreplayable:
        gaps.append(
            CoverageGap(
                gap_id="D-CON-EMPTY-REPLAY-UNAVAILABLE",
                instrument=EMPTY_INSTRUMENT,
                surface="containers",
                reason="sanitized-image-unresolvable",
                caps=Disposition.HOLD,
                statement=(
                    "The empty submission must be replayed through the exact bound invocation "
                    "inside the final sanitized image at its pinned digest against the frozen "
                    "checker set. No sanitized image resolves at this root, so the replay did "
                    "not run. A static derivation over the committed reward code is recorded "
                    "in the notes and is not accepted in place of the replay."
                ),
                subject=",".join(unreplayable),
            )
        )

    claimed_measured = [
        bundle.name
        for bundle in bundles
        if (
            (bundle_carrier(bundle).get("atoms") or {}).get("empty_submission_validation") or {}
        ).get("state")
        == "measured"
        and not core.is_hex64(
            str(
                (
                    (bundle_carrier(bundle).get("atoms") or {}).get("empty_submission_validation")
                    or {}
                ).get("result_digest")
                or ""
            )
        )
    ]
    if claimed_measured:
        gaps.append(
            CoverageGap(
                gap_id="D-CON-UNMEASURED-ATOM",
                instrument=EMPTY_INSTRUMENT,
                surface="task_corpus",
                reason="claimed-measured-without-result-digest",
                caps=Disposition.HOLD,
                statement=(
                    "The named carriers record this atom as measured while carrying no result "
                    "digest to bind that claim to. A claim of measurement with no recomputable "
                    "result is not evidence of measurement, so the atom resolves as a coverage "
                    "gap rather than as a producer pass."
                ),
                subject=",".join(claimed_measured),
            )
        )

    standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=EMPTY_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "distinct_from": "G-VER-BASELINE",
            "requirement": "every intended fail-to-pass target unresolved and reward exactly zero",
            "bundles": rows,
        },
    )


def _walk_schema(
    observed: Any, schema: Any, path: str, unknown: list[str], missing: list[str], prose: list[str]
) -> None:
    """Validate an observed carrier against the closed schema, both directions."""
    if isinstance(schema, dict):
        if not isinstance(observed, dict):
            missing.append(path or "<root>")
            return
        for key in observed:
            if key not in schema:
                unknown.append(f"{path}{key}" if path else key)
        for key, child in schema.items():
            child_path = f"{path}{key}." if isinstance(child, dict) else f"{path}{key}"
            if key not in observed:
                missing.append(f"{path}{key}" if path else key)
                continue
            _walk_schema(observed[key], child, child_path, unknown, missing, prose)
        return
    if isinstance(observed, str) and len(observed.split()) > PROSE_WORD_CEILING:
        prose.append(path)


def _run_record(base: Path, bundles: list[Path], now: datetime.datetime) -> InstrumentResult:
    """Re-resolve the provenance carrier against auditor-owned state.

    The carrier is a one-way producer-claim channel. Its schema is exhaustive and
    closed, unknown keys are retained findings capping at BLOCK, and no field
    accepts free-form prose. The atom result itself must reside in an external
    signed proof rather than in the carrier, and the carrier is private under the
    leak gate exactly like the ground-truth file.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    rows: list[dict[str, Any]] = []
    _, attestation_digest, attestation_state = load_root(base, ATTESTATION_ROOT)

    for bundle in bundles:
        uuid = bundle.name
        carrier_path = bundle / PROVENANCE_CARRIER
        signature_path = bundle / PROVENANCE_SIGNATURE
        carrier = bundle_carrier(bundle)
        if not carrier:
            findings.append(
                Finding(
                    finding_id=f"F-CON-RECORD-CARRIER-UNPARSEABLE-{uuid[:8]}",
                    instrument=RECORD_INSTRUMENT,
                    critical_class=CARRIER_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement="The provenance carrier is absent or did not parse.",
                    evidence={"path": PROVENANCE_CARRIER},
                )
            )
            continue

        unknown: list[str] = []
        missing: list[str] = []
        prose: list[str] = []
        _walk_schema(carrier, CARRIER_SCHEMA, "", unknown, missing, prose)

        if unknown:
            findings.append(
                Finding(
                    finding_id=f"F-CON-RECORD-UNKNOWN-KEY-{uuid[:8]}",
                    instrument=RECORD_INSTRUMENT,
                    critical_class=CARRIER_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement=(
                        "The provenance carrier declares keys outside its closed schema. Step "
                        "8i makes the carrier schema exhaustive, so an unrecognized key is a "
                        "retained finding capping at BLOCK."
                    ),
                    evidence={"unknown_keys": sorted(unknown)},
                )
            )
        if missing:
            findings.append(
                Finding(
                    finding_id=f"F-CON-RECORD-MISSING-KEY-{uuid[:8]}",
                    instrument=RECORD_INSTRUMENT,
                    critical_class=CARRIER_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement="The provenance carrier omits keys its closed schema requires.",
                    evidence={"missing_keys": sorted(missing)},
                )
            )
        if prose:
            findings.append(
                Finding(
                    finding_id=f"F-CON-RECORD-FREE-FORM-PROSE-{uuid[:8]}",
                    instrument=RECORD_INSTRUMENT,
                    critical_class=CARRIER_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement=(
                        "Fields of the provenance carrier that its closed schema defines as "
                        "tokens or digests instead carry free-form prose. Step 8i states that "
                        "no field of this carrier accepts free-form prose, because prose is not "
                        "recomputable and turns a bound claim into an assertion."
                    ),
                    evidence={"prose_fields": sorted(prose)},
                )
            )

        signature_present = signature_path.is_file()
        if not signature_present:
            findings.append(
                Finding(
                    finding_id=f"F-CON-RECORD-SIGNATURE-ABSENT-{uuid[:8]}",
                    instrument=RECORD_INSTRUMENT,
                    critical_class=CARRIER_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement=(
                        "The detached provenance signature is absent, so the canonical payload "
                        "carries no signer identity and the screening measurement instant, "
                        "interval, and expiry are unsigned."
                    ),
                    evidence={"path": PROVENANCE_SIGNATURE},
                )
            )

        binding = carrier.get("binding") or {}
        envelope = binding.get("binding_envelope")
        if envelope != "signed":
            findings.append(
                Finding(
                    finding_id=f"F-CON-RECORD-ENVELOPE-UNSIGNED-{uuid[:8]}",
                    instrument=RECORD_INSTRUMENT,
                    critical_class=CARRIER_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement=(
                        "The binding envelope over the canonical payload hash, the canonical "
                        "bundle hash, and the pinned image digest is not signed, so the binding "
                        "block is an unauthenticated declaration."
                    ),
                    evidence={"binding_envelope": envelope},
                )
            )

        closure = agent_visible_files(bundle)
        carrier_visible = any(
            path.name == "provenance.yaml" and "solution" not in path.parts for path in closure
        )
        if carrier_visible:
            findings.append(
                Finding(
                    finding_id=f"F-CON-RECORD-CARRIER-AGENT-VISIBLE-{uuid[:8]}",
                    instrument=RECORD_INSTRUMENT,
                    critical_class=CARRIER_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=uuid,
                    statement=(
                        "The provenance carrier is reachable from the agent-facing closure. It "
                        "is private under the leak gate exactly like the ground-truth file, so "
                        "its visibility creates both a leak finding and a screening finding."
                    ),
                    evidence={"closure_size": len(closure)},
                )
            )

        roots_block = carrier.get("screening_roots") or {}
        unsupplied = sorted(
            name
            for name, value in roots_block.items()
            if isinstance(value, dict) and value.get("state") != "resolved"
        )
        rows.append(
            {
                "uuid": uuid,
                "carrier_digest": core.sha256_path(carrier_path)
                if carrier_path.is_file()
                else None,
                "unknown_keys": sorted(unknown),
                "missing_keys": sorted(missing),
                "free_form_prose_fields": sorted(prose),
                "signature_present": signature_present,
                "binding_envelope": envelope,
                "declared_canonical_bundle_hash": binding.get("canonical_bundle_hash"),
                "recomputed_canonical_bundle_hash": None,
                "screening_roots_unsupplied": unsupplied,
                "freshness": freshness(carrier, now),
                "instrument_versions": carrier.get("instrument_versions"),
            }
        )

    gaps.append(
        CoverageGap(
            gap_id="D-CON-RECORD-BINDING-RECOMPUTE-UNPROJECTED",
            instrument=RECORD_INSTRUMENT,
            surface="task_corpus",
            reason="canary-normalized-bundle-hash-algorithm-unprojected",
            caps=Disposition.HOLD,
            statement=(
                "Step 8i requires CRUCIBLE to recompute the binding block independently using "
                "the same canary-normalized canonical bundle hash the leak gate recomputes, and "
                "to retain any divergence as a hash-bound critical floor breach. The projection "
                "carries no bound definition of that hash, and the only definition present is "
                "the authoring generator inside the bundle, which step 8b forbids this harness "
                "from adopting as its own normalizer. The recomputation therefore did not run "
                "and the declared binding block is neither confirmed nor refuted."
            ),
        )
    )

    if attestation_state != "resolved" or not attestation_digest:
        gaps.append(
            CoverageGap(
                gap_id="D-CON-RECORD-TRUST-ROOT-ABSENT",
                instrument=RECORD_INSTRUMENT,
                surface="task_corpus",
                reason="external-trust-root-absent",
                caps=Disposition.HOLD,
                statement=(
                    "The detached signature must verify against a signer identity and an "
                    "external trust root. The source attestation trust root is recorded as "
                    "absent with a null identity, so no external root exists to verify against."
                ),
            )
        )

    gaps.append(
        CoverageGap(
            gap_id="D-CON-RECORD-EXTERNAL-PROOF-ABSENT",
            instrument=RECORD_INSTRUMENT,
            surface="task_corpus",
            reason="external-signed-proof-absent",
            caps=Disposition.HOLD,
            statement=(
                "Step 8i requires the provenance atom result to reside in the external signed "
                "proof rather than in the carrier. No external signed proof is delivered at "
                "this root, so the atom result exists only as a carrier claim, and a carrier "
                "claim can lower a disposition but can never establish one."
            ),
        )
    )

    gaps.append(
        CoverageGap(
            gap_id="D-CON-RECORD-REAUDIT-ENVELOPE-UNDELIVERABLE",
            instrument=RECORD_INSTRUMENT,
            surface="task_corpus",
            reason="reaudit-proof-sink-not-writable",
            caps=Disposition.HOLD,
            statement=(
                "Step 8n requires each re-audit to be wrapped in a signed envelope delivered to "
                "the parent proof directory. That directory is outside this verification root "
                "and is not writable from here, and a prompt-only contract cannot schedule the "
                "external work, so the standing re-audit lane has no sink and no scheduler."
            ),
        )
    )

    standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=RECORD_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "closed_schema_top_level": sorted(CARRIER_SCHEMA),
            "attestation_root_state": attestation_state,
            "bundles": rows,
        },
    )


def run_family(base: Path, reconnaissance: Any) -> list[InstrumentResult]:
    """Run the six contamination atoms over every resident bundle.

    Contamination screening has no presence gate and no exempt path, and it
    re-audits every committed bundle on each invocation because a prior pass
    binds earlier roots. A degenerate tree with no resident bundle still runs the
    atoms and reports the absence as a gap, because silence would read as a clean
    screen.
    """
    sys.dont_write_bytecode = True
    now = datetime.datetime.now(datetime.UTC)
    bundles = core.bundle_roots(base)
    if not bundles:
        return [
            InstrumentResult(
                instrument=name,
                ran=False,
                gaps=[
                    CoverageGap(
                        gap_id=f"D-CON-NO-RESIDENT-BUNDLE-{name.rsplit('-', 1)[-1]}",
                        instrument=name,
                        surface="task_corpus",
                        reason="no-resident-bundle",
                        caps=Disposition.HOLD,
                        statement=(
                            "No resident bundle resolved under any lane root, so this atom had "
                            "no subject to screen."
                        ),
                    )
                ],
                standing=Standing.INSUFFICIENT_EVIDENCE,
            )
            for name in (
                EXCLUSION_INSTRUMENT,
                FREEZE_INSTRUMENT,
                NEARDUP_INSTRUMENT,
                STRIP_INSTRUMENT,
                EMPTY_INSTRUMENT,
                RECORD_INSTRUMENT,
            )
        ]
    return [
        _run_exclusion(base, bundles, now),
        _run_freeze(base, bundles, now),
        _run_neardup(base, bundles, now),
        _run_strip(base, bundles, now),
        _run_empty(base, bundles, now),
        _run_record(base, bundles, now),
    ]


__all__ = [
    "CARRIER_SCHEMA",
    "EMPTY_INSTRUMENT",
    "EXCLUSION_INSTRUMENT",
    "FREEZE_INSTRUMENT",
    "NEARDUP_INSTRUMENT",
    "RECORD_INSTRUMENT",
    "STRIP_INSTRUMENT",
    "bound_normalize",
    "bound_tokens",
    "freshness",
    "jaccard",
    "run_family",
    "shingles",
    "strip_diff_coordinates",
    "strip_hex_object_ids",
]
