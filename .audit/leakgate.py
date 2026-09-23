"""Leak gate family, discharging CRUCIBLE contract step 8b.

Step 8b asks two separate questions about every resident bundle and this module
answers each with its own instrument.

G-LEAK-CANARY asks whether the delivery-integrity marker survived authoring
intact. Every designated slot must carry the canary block exactly once, well
formed, with the same four values across all four designated files of that
bundle, and no other committed file may carry the block at all. The slots are
normalized with core.normalize_text, which is the audit harness's own
normalizer, never with the bundle's own solution/recompute.py: reusing the
authoring normalizer would let a bundle define away the very comparison the
audit exists to make.

G-LEAK-CONTAINMENT asks whether private carriers reached the agent-visible
surface. It recomputes normalized token n-gram containment of each private
carrier against the agent-visible bytes and scans those bytes for any verbatim
canary token. The one thing this module refuses to accept as evidence is the
claim that a framework mounts the private tree privately; a boundary is held
only where committed bytes show it held, and where the bytes are absent the
result is a coverage gap rather than a pass.

Step 8b also requires the recomputed canonical content hash to equal the task
artifact hash recorded in CRUCIBLE_VIEW and to derive the bundle uuid. The view
resident beside this project projects three task uuids, none of which is a
resident bundle, so that comparison is unprojected for every bundle here. That
single comparison is recorded as a coverage gap and every other check that can
be derived from committed bundle bytes alone still runs, because an instrument
that declines to fire at all caps the gate at BLOCK and this one can fire.
"""

from __future__ import annotations

import re
import uuid
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
    Severity,
    Standing,
)
from registry import REGISTRY, Category, EvidenceClass, Instrument

CANARY_INSTRUMENT = "G-LEAK-CANARY"
CONTAINMENT_INSTRUMENT = "G-LEAK-CONTAINMENT"

DESIGNATED_CANARY_SLOTS = (
    "solution/TRUTH.md",
    "solution/policy.yaml",
    "solution/provenance.yaml",
    "solution/rubrics.json",
)

CANARY_INDEX_COUNT = 4
EXPECTED_CANARY_INDICES = ("00", "01", "02", "03")
CANARY_MARKER = "forge-canary"

_CANARY_LOOSE = re.compile(r"forge-canary\s*\[([^\]\s]{0,8})\]\s*=\s*([0-9a-z]*)")
_CANARY_STRICT_VALUE = re.compile(r"\A[0-9a-f]{32}\Z")

PRIVATE_CARRIER_SLOTS = (
    "solution/TRUTH.md",
    "solution/rubrics.json",
    "solution/solve.sh",
)

PRIVATE_SUBTREES = ("solution", "tests", "environment", "trajectories")
TRAJECTORY_SUBTREE = "trajectories"
MANIFEST_NAME = "task.toml"

NGRAM_WIDTH = 5
DEFAULT_NEARDUP_THRESHOLD = 0.3
DEFAULT_NEARDUP_REVIEW_THRESHOLD = 0.15

CRUCIBLE_VIEW_RELATIVE = ("..", ".memory", "crucible_view.yaml")

TASK_HASH_GAP_ID = "D-LEAK-TASK-HASH-UNPROJECTED"
AGENT_TREE_GAP_ID = "D-LEAK-AGENT-TREE-UNAVAILABLE"
CANARY_INTERNAL_GAP_ID = "D-LEAK-CANARY-INTERNAL-ERROR"
CONTAINMENT_INTERNAL_GAP_ID = "D-LEAK-CONTAINMENT-INTERNAL-ERROR"
NO_BUNDLE_GAP_ID = "D-LEAK-NO-RESIDENT-BUNDLE"

DELIVERY_CRITICAL_CLASS = "delivery-integrity"
LEAK_CRITICAL_CLASS = "private-carrier-leak"

_REGISTRY_DECLARATIONS: tuple[dict[str, Any], ...] = (
    {
        "name": CANARY_INSTRUMENT,
        "critical_capability": "canary-slot-integrity-and-cross-file-agreement",
        "evidence_class": EvidenceClass.RECOMPUTED_DIGEST,
        "required_conditions": (
            "designated-slots-readable",
            "audit-owned-normalizer",
            "committed-bundle-bytes-present",
        ),
        "notes": "Normalizes with core.normalize_text only, never with solution/recompute.py.",
    },
    {
        "name": CONTAINMENT_INSTRUMENT,
        "critical_capability": "private-carrier-to-agent-surface-containment",
        "evidence_class": EvidenceClass.SET_RELATION,
        "required_conditions": (
            "agent-visible-closure-readable",
            "private-carriers-readable",
            "neardup-thresholds-declared",
        ),
        "notes": "Containment rather than Jaccard, so a small carrier cannot dilute a total leak.",
    },
)


def _register_declarations() -> None:
    """Register both step 8b instruments with the twelve required declaration fields.

    Registration is idempotent so that a second import of this family module
    cannot raise and thereby convert a re-import into a broken instrument.
    """
    for declaration in _REGISTRY_DECLARATIONS:
        if declaration["name"] in REGISTRY:
            continue
        REGISTRY.register(
            Instrument(
                name=declaration["name"],
                category=Category.LEAK_GATE,
                binary="python",
                ecosystems=("*",),
                timeout_seconds=600.0,
                required_conditions=declaration["required_conditions"],
                critical_capability=declaration["critical_capability"],
                evidence_class=declaration["evidence_class"],
                requires_parser=False,
                requires_raw_artifact=False,
                disposition_cap_on_absence=Disposition.BLOCK,
                bucket=Bucket.D,
                database_pin="",
                notes=declaration["notes"],
            )
        )


_register_declarations()


def _ascii_text(raw: str) -> str:
    """Force a statement into the ASCII the emitted YAML is restricted to."""
    return raw.encode("ascii", "backslashreplace").decode("ascii")


def read_text(path: Path) -> str:
    """Read a committed file as text, failing closed to the empty string.

    An unreadable file yields no bytes to measure rather than an exception, and
    the caller records the absence as a finding or a gap.
    """
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def normalized(path: Path) -> str:
    """Normalize one committed file under the audit harness's own normalizer."""
    return core.normalize_text(read_text(path))


def canary_matches(normalized_text: str) -> list[tuple[str, str]]:
    """Return every canary-shaped assignment found in already-normalized text.

    The pattern is deliberately loose on both index and value so that a malformed
    block is detected as malformed rather than missed entirely, which would let a
    corrupted marker read as an absent one.
    """
    return [(match.group(1), match.group(2)) for match in _CANARY_LOOSE.finditer(normalized_text)]


def _block_starts(matches: list[tuple[str, str]]) -> int:
    return sum(1 for index, _ in matches if index == EXPECTED_CANARY_INDICES[0])


def inspect_slot(normalized_text: str) -> dict[str, Any]:
    """Classify one designated slot's canary block from its normalized bytes.

    A slot is well formed only when it carries exactly one block of exactly four
    assignments whose indices read 00 through 03 in order and whose values are
    each exactly thirty-two lowercase hex characters after normalization. Any
    other shape is reported with the specific defect so the finding statement
    names what is wrong rather than reporting a generic failure.
    """
    matches = canary_matches(normalized_text)
    starts = _block_starts(matches)
    if not matches:
        return {"state": "missing", "detail": "no canary assignment present", "values": []}
    if starts == 0:
        return {
            "state": "malformed",
            "detail": "canary assignments present but none carries index 00",
            "values": [value for _, value in matches],
        }
    if starts > 1:
        return {
            "state": "duplicated",
            "detail": f"{starts} canary blocks present where exactly one is required",
            "values": [value for _, value in matches],
        }
    indices = tuple(index for index, _ in matches)
    values = [value for _, value in matches]
    if len(matches) != CANARY_INDEX_COUNT:
        return {
            "state": "malformed",
            "detail": f"{len(matches)} canary lines present where {CANARY_INDEX_COUNT} required",
            "values": values,
        }
    if indices != EXPECTED_CANARY_INDICES:
        return {
            "state": "malformed",
            "detail": f"canary indices read {'-'.join(indices)} rather than 00-01-02-03",
            "values": values,
        }
    bad = [value for value in values if not _CANARY_STRICT_VALUE.match(value)]
    if bad:
        return {
            "state": "malformed",
            "detail": f"{len(bad)} canary values are not exactly 32 lowercase hex characters",
            "values": values,
        }
    return {"state": "well_formed", "detail": "", "values": values}


def bundle_files(bundle: Path) -> list[Path]:
    """Every committed file of one bundle, in a fixed order."""
    return sorted(path for path in bundle.rglob("*") if path.is_file())


def agent_visible_files(bundle: Path) -> list[Path]:
    """The committed bytes the agent sees.

    instruction.md plus any other file sitting directly in the bundle root that is
    not the task manifest. Everything under solution/, tests/, environment/ and
    trajectories/ is evaluator-side or rollout-side and is excluded by subtree.
    """
    visible: list[Path] = []
    for path in sorted(bundle.iterdir()):
        if path.is_file() and path.name != MANIFEST_NAME:
            visible.append(path)
    return visible


def private_carrier_files(bundle: Path) -> list[Path]:
    """Every private carrier: the named solution carriers plus every rollout file."""
    carriers: list[Path] = []
    for relative in PRIVATE_CARRIER_SLOTS:
        candidate = bundle / relative
        if candidate.is_file():
            carriers.append(candidate)
    trajectories = bundle / TRAJECTORY_SUBTREE
    if trajectories.is_dir():
        carriers.extend(sorted(path for path in trajectories.rglob("*") if path.is_file()))
    return carriers


def load_neardup_parameters(base: Path) -> dict[str, float]:
    """Read the declared near-duplicate thresholds from .audit/scope.yaml.

    The thresholds are read from the approved scope rather than hardcoded so that
    a threshold change is visible as a scope change. An unreadable or silent
    scope fails closed to the contract defaults rather than to a permissive
    value, because a missing threshold must never widen what passes.
    """
    path = base / core.AUDIT_DIRNAME / core.SCOPE_FILENAME
    threshold = DEFAULT_NEARDUP_THRESHOLD
    review = DEFAULT_NEARDUP_REVIEW_THRESHOLD
    source = "contract-default"
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        document = None
    if isinstance(document, dict):
        parameters = document.get("neardup_parameters")
        if isinstance(parameters, dict):
            source = "scope.yaml"
            raw_threshold = parameters.get("neardup_threshold")
            raw_review = parameters.get("neardup_review_threshold")
            if isinstance(raw_threshold, int | float):
                threshold = float(raw_threshold)
            if isinstance(raw_review, int | float):
                review = float(raw_review)
    return {"threshold": threshold, "review_threshold": review, "source": source}


def load_crucible_view(base: Path) -> dict[str, Any]:
    """Load the CRUCIBLE_VIEW projection that step 8b compares the task hash against."""
    path = base.joinpath(*CRUCIBLE_VIEW_RELATIVE)
    try:
        resolved = path.resolve()
        raw = resolved.read_text(encoding="utf-8")
    except OSError:
        return {"present": False, "path": str(path), "raw": "", "document": {}}
    try:
        document = yaml.safe_load(raw)
    except yaml.YAMLError:
        document = None
    return {
        "present": True,
        "path": str(resolved),
        "raw": raw,
        "document": document if isinstance(document, dict) else {},
        "digest": core.sha256_bytes(raw.encode("utf-8")),
    }


def view_task_hash(view: dict[str, Any], bundle_uuid: str) -> str | None:
    """Return the projected task artifact hash for one bundle uuid, or None.

    None means the view projects no determination for this bundle at all, which
    is a different fact from a projected hash that disagrees, and the caller keeps
    the two apart.
    """
    if not view.get("present"):
        return None
    if bundle_uuid not in str(view.get("raw") or ""):
        return None
    for task in view.get("document", {}).get("tasks") or []:
        if not isinstance(task, dict):
            continue
        if bundle_uuid in core.canonical_json(task).decode("ascii"):
            candidate = task.get("task_hash")
            return str(candidate) if candidate else None
    return None


def _uuid_version(name: str) -> int | None:
    try:
        return uuid.UUID(name).version
    except ValueError:
        return None


def _bundle_binding(bundle: Path) -> dict[str, Any]:
    """Read the declared binding block from a bundle's provenance carrier."""
    path = bundle / "solution" / "provenance.yaml"
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    if not isinstance(document, dict):
        return {}
    binding = document.get("binding")
    return binding if isinstance(binding, dict) else {}


def _canary_findings_for_bundle(bundle: Path, base: Path) -> tuple[list[Finding], dict[str, Any]]:
    """Run every canary check derivable from one bundle's committed bytes."""
    findings: list[Finding] = []
    lane = core.lane_of(bundle, base)
    subject = bundle.name
    slot_rows: dict[str, Any] = {}
    well_formed: dict[str, tuple[str, ...]] = {}

    for relative in DESIGNATED_CANARY_SLOTS:
        path = bundle / relative
        if not path.is_file():
            findings.append(
                Finding(
                    finding_id=f"{CANARY_INSTRUMENT}-{subject}-SLOT-ABSENT-"
                    f"{core.sha256_bytes(relative.encode())[:8]}",
                    instrument=CANARY_INSTRUMENT,
                    critical_class=DELIVERY_CRITICAL_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=subject,
                    statement=_ascii_text(
                        f"Designated canary slot {relative} is absent from bundle {subject}, so "
                        "the delivery-integrity marker cannot be recomputed for that slot."
                    ),
                    evidence={"bundle": subject, "lane": lane, "slot": relative},
                )
            )
            slot_rows[relative] = {"state": "absent"}
            continue
        report = inspect_slot(normalized(path))
        slot_rows[relative] = {
            "state": report["state"],
            "detail": report["detail"],
            "value_count": len(report["values"]),
        }
        if report["state"] == "well_formed":
            well_formed[relative] = tuple(report["values"])
            continue
        findings.append(
            Finding(
                finding_id=f"{CANARY_INSTRUMENT}-{subject}-{report['state'].upper()}-"
                f"{core.sha256_bytes(relative.encode())[:8]}",
                instrument=CANARY_INSTRUMENT,
                critical_class=DELIVERY_CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject=subject,
                statement=_ascii_text(
                    f"Canary block in designated slot {relative} of bundle {subject} is "
                    f"{report['state']}: {report['detail']}. Recomputed under "
                    f"{core.normalization_domain()}, the audit harness's own normalizer."
                ),
                evidence={
                    "bundle": subject,
                    "lane": lane,
                    "slot": relative,
                    "state": report["state"],
                    "detail": report["detail"],
                    "normalization_domain": core.normalization_domain(),
                },
            )
        )

    distinct = sorted(set(well_formed.values()))
    if len(distinct) > 1:
        findings.append(
            Finding(
                finding_id=f"{CANARY_INSTRUMENT}-{subject}-CROSS-SLOT-DISAGREEMENT",
                instrument=CANARY_INSTRUMENT,
                critical_class=DELIVERY_CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject=subject,
                statement=_ascii_text(
                    f"The designated canary slots of bundle {subject} carry {len(distinct)} "
                    "distinct value sets where all four slots must carry one, so the marker does "
                    "not bind the carriers together."
                ),
                evidence={
                    "bundle": subject,
                    "lane": lane,
                    "slot_values": {
                        slot: list(values) for slot, values in sorted(well_formed.items())
                    },
                },
            )
        )

    designated = {(bundle / relative).resolve() for relative in DESIGNATED_CANARY_SLOTS}
    misplaced: list[str] = []
    for path in bundle_files(bundle):
        if path.resolve() in designated:
            continue
        text = normalized(path)
        if CANARY_MARKER not in text:
            continue
        misplaced.append(path.relative_to(bundle).as_posix())
    for relative in misplaced:
        findings.append(
            Finding(
                finding_id=f"{CANARY_INSTRUMENT}-{subject}-MISPLACED-"
                f"{core.sha256_bytes(relative.encode())[:8]}",
                instrument=CANARY_INSTRUMENT,
                critical_class=DELIVERY_CRITICAL_CLASS,
                severity=Severity.MEDIUM,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject=subject,
                statement=_ascii_text(
                    f"File {relative} of bundle {subject} carries a canary block while not being "
                    "one of the four designated slots, so the marker is present in more carriers "
                    "than the delivery contract designates and its placement is not derivable "
                    "from the designation alone."
                ),
                evidence={
                    "bundle": subject,
                    "lane": lane,
                    "path": relative,
                    "designated_slots": list(DESIGNATED_CANARY_SLOTS),
                },
            )
        )

    version = _uuid_version(subject)
    if version != 5:
        findings.append(
            Finding(
                finding_id=f"{CANARY_INSTRUMENT}-{subject}-UUID-SHAPE",
                instrument=CANARY_INSTRUMENT,
                critical_class=DELIVERY_CRITICAL_CLASS,
                severity=Severity.MEDIUM,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject=subject,
                statement=_ascii_text(
                    f"Bundle directory name {subject} does not parse as a version 5 uuid "
                    f"(parsed version {version}), so it cannot be a derived identity."
                ),
                evidence={"bundle": subject, "parsed_version": version},
            )
        )

    binding = _bundle_binding(bundle)
    declared_hash = str(binding.get("canonical_bundle_hash") or "")
    if not core.is_hex64(declared_hash):
        findings.append(
            Finding(
                finding_id=f"{CANARY_INSTRUMENT}-{subject}-BINDING-HASH-SHAPE",
                instrument=CANARY_INSTRUMENT,
                critical_class=DELIVERY_CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject=subject,
                statement=_ascii_text(
                    f"Bundle {subject} declares canonical_bundle_hash {declared_hash!r}, which is "
                    "not sixty-four lowercase hex characters, so no content binding is expressed."
                ),
                evidence={"bundle": subject, "declared": declared_hash},
            )
        )

    row = {
        "bundle": subject,
        "lane": lane,
        "slots": slot_rows,
        "distinct_value_sets": len(distinct),
        "misplaced_carriers": misplaced,
        "uuid_version": version,
        "declared_canonical_bundle_hash": declared_hash,
        "binding_envelope": str(binding.get("binding_envelope") or "unrecorded"),
        "audit_recomputed_tree_digest": core.tree_digest(
            bundle, [path.relative_to(bundle).as_posix() for path in bundle_files(bundle)]
        ),
        "normalization_domain": core.normalization_domain(),
    }
    return findings, row


def _task_hash_gap(bundle: Path, row: dict[str, Any], view: dict[str, Any]) -> CoverageGap:
    """Record the one step 8b comparison that committed bytes cannot decide."""
    return CoverageGap(
        gap_id=TASK_HASH_GAP_ID,
        instrument=CANARY_INSTRUMENT,
        surface="bundle_identity_binding",
        subject=bundle.name,
        reason="crucible-view-projects-no-determination-for-this-bundle",
        caps=Disposition.HOLD,
        statement=_ascii_text(
            f"The canonical content hash of bundle {bundle.name} cannot be reconciled against a "
            "task artifact hash, and the bundle uuid cannot be shown to derive from it, for three "
            f"reasons that all hold at once. The projection at {view.get('path')} carries "
            "determinations for other task uuids and no occurrence of this bundle uuid, so no "
            "task_hash is projected to compare against. The recipe the declared "
            "canonical_bundle_hash was produced by is not committed in this repository, so the "
            "audit harness cannot recompute that value independently; it recomputes its own tree "
            f"digest {row['audit_recomputed_tree_digest']} instead and records it as evidence "
            "rather than as a match. The declared binding reads envelope "
            f"{row['binding_envelope']}, so even the in-bundle hash "
            f"{row['declared_canonical_bundle_hash']} is unauthenticated. Every other step 8b "
            "check that committed bundle bytes can decide was still run."
        ),
    )


def _run_canary(base: Path, bundles: list[Path]) -> InstrumentResult:
    """Run G-LEAK-CANARY, the designated-slot integrity half of contract step 8b."""
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    rows: list[dict[str, Any]] = []
    view = load_crucible_view(base)

    for bundle in bundles:
        bundle_findings, row = _canary_findings_for_bundle(bundle, base)
        findings.extend(bundle_findings)
        projected = view_task_hash(view, bundle.name)
        row["projected_task_hash"] = projected
        rows.append(row)
        if projected is None:
            gaps.append(_task_hash_gap(bundle, row, view))
            continue
        if projected != row["declared_canonical_bundle_hash"]:
            findings.append(
                Finding(
                    finding_id=f"{CANARY_INSTRUMENT}-{bundle.name}-TASK-HASH-MISMATCH",
                    instrument=CANARY_INSTRUMENT,
                    critical_class=DELIVERY_CRITICAL_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=_ascii_text(
                        f"The task artifact hash projected for bundle {bundle.name} is "
                        f"{projected} while the bundle declares "
                        f"{row['declared_canonical_bundle_hash']}, so the delivered bytes are not "
                        "the bytes the projection determined."
                    ),
                    evidence={
                        "projected": projected,
                        "declared": row["declared_canonical_bundle_hash"],
                    },
                )
            )

    standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=CANARY_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "bundles": rows,
            "designated_slots": list(DESIGNATED_CANARY_SLOTS),
            "normalization_domain": core.normalization_domain(),
            "normalizer": "core.normalize_text",
            "crucible_view": {
                "present": view.get("present"),
                "path": view.get("path"),
                "digest": view.get("digest"),
            },
        },
    )


def _surfaced_canary_tokens(bundle: Path, visible_text: str) -> list[str]:
    """Return every canary token from this bundle that is verbatim in agent-visible bytes."""
    tokens: set[str] = set()
    for relative in DESIGNATED_CANARY_SLOTS:
        path = bundle / relative
        if not path.is_file():
            continue
        for _, value in canary_matches(normalized(path)):
            if _CANARY_STRICT_VALUE.match(value):
                tokens.add(value)
    surfaced = sorted(token for token in tokens if token in visible_text)
    if CANARY_MARKER in visible_text:
        surfaced.append(CANARY_MARKER)
    return surfaced


def _containment_for_bundle(
    bundle: Path, base: Path, parameters: dict[str, float]
) -> tuple[list[Finding], list[CoverageGap], dict[str, Any]]:
    """Recompute carrier-to-agent-surface containment for one bundle."""
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    subject = bundle.name
    lane = core.lane_of(bundle, base)

    visible_files = agent_visible_files(bundle)
    visible_raw = "\n".join(read_text(path) for path in visible_files)
    visible_text = core.normalize_text(visible_raw)
    visible_rows = [path.relative_to(bundle).as_posix() for path in visible_files]

    gaps.append(
        CoverageGap(
            gap_id=AGENT_TREE_GAP_ID,
            instrument=CONTAINMENT_INSTRUMENT,
            surface="agent_visible_closure",
            subject=subject,
            reason="mounted-working-tree-not-committed-in-this-repository",
            caps=Disposition.HOLD,
            statement=_ascii_text(
                f"The agent-visible surface of bundle {subject} is instruction.md plus the "
                "repository working tree the container mounts. Only the committed half is present "
                f"here, namely {', '.join(visible_rows) or 'no committed agent-visible file'}. The "
                "mounted half lives inside a pinned image that this repository does not carry, so "
                "containment is measured over the committed half alone. That the framework mounts "
                "the remainder privately is a producer claim and is not accepted here as evidence "
                "that the boundary held."
            ),
        )
    )

    if not visible_text:
        gaps.append(
            CoverageGap(
                gap_id=CONTAINMENT_INTERNAL_GAP_ID,
                instrument=CONTAINMENT_INSTRUMENT,
                surface="agent_visible_closure",
                subject=subject,
                reason="agent-visible-closure-empty",
                caps=Disposition.HOLD,
                statement=_ascii_text(
                    f"Bundle {subject} exposes no readable agent-visible bytes, so containment "
                    "against that surface measures nothing and no negative result is available."
                ),
            )
        )
        return findings, gaps, {"bundle": subject, "lane": lane, "agent_visible": visible_rows}

    surfaced = _surfaced_canary_tokens(bundle, visible_text)
    if surfaced:
        findings.append(
            Finding(
                finding_id=f"{CONTAINMENT_INSTRUMENT}-{subject}-CANARY-SURFACED",
                instrument=CONTAINMENT_INSTRUMENT,
                critical_class=LEAK_CRITICAL_CLASS,
                severity=Severity.CRITICAL,
                caps=Disposition.BLOCK,
                bucket=Bucket.D,
                subject=subject,
                statement=_ascii_text(
                    f"The agent-visible bytes of bundle {subject} carry {len(surfaced)} verbatim "
                    "canary token(s) that belong to the private carriers, which is a direct "
                    "crossing of the delivery boundary."
                ),
                evidence={"bundle": subject, "lane": lane, "tokens": surfaced},
            )
        )

    threshold = parameters["threshold"]
    review = parameters["review_threshold"]
    measurements: list[dict[str, Any]] = []
    for carrier in private_carrier_files(bundle):
        relative = carrier.relative_to(bundle).as_posix()
        carrier_raw = read_text(carrier)
        forward = core.ngram_containment(carrier_raw, visible_raw, NGRAM_WIDTH)
        reverse = core.ngram_containment(visible_raw, carrier_raw, NGRAM_WIDTH)
        row = {
            "path": relative,
            "containment": round(forward, 6),
            "reverse_containment": round(reverse, 6),
            "carrier_ngrams": len(set(core.token_ngrams(carrier_raw, NGRAM_WIDTH))),
            "visible_ngrams": len(set(core.token_ngrams(visible_raw, NGRAM_WIDTH))),
            "band": "clear",
        }
        if forward >= threshold:
            row["band"] = "retained"
        elif forward >= review:
            row["band"] = "review"
        measurements.append(row)
        if row["band"] == "clear":
            continue
        retained = row["band"] == "retained"
        findings.append(
            Finding(
                finding_id=f"{CONTAINMENT_INSTRUMENT}-{subject}-"
                f"{core.sha256_bytes(relative.encode())[:12]}",
                instrument=CONTAINMENT_INSTRUMENT,
                critical_class=LEAK_CRITICAL_CLASS,
                severity=Severity.HIGH if retained else Severity.LOW,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject=subject,
                statement=_ascii_text(
                    f"Private carrier {relative} of bundle {subject} shares "
                    f"{row['containment']:.6f} of its normalized {NGRAM_WIDTH}-gram set with the "
                    f"agent-visible bytes, at or above the "
                    f"{'retention' if retained else 'review'} threshold "
                    f"{threshold if retained else review}. Reverse containment is "
                    f"{row['reverse_containment']:.6f} over "
                    f"{row['carrier_ngrams']} carrier and {row['visible_ngrams']} visible "
                    "distinct n-grams. Containment is symmetric in its overlap and differs only "
                    "in denominator, so this measurement records that the two surfaces share "
                    "material and does not by itself establish which surface the material "
                    "originated on; the overlap is retained for adjudication rather than "
                    "discharged as clean."
                ),
                evidence={
                    "bundle": subject,
                    "lane": lane,
                    "carrier": relative,
                    "ngram_width": NGRAM_WIDTH,
                    "normalization_domain": core.normalization_domain(),
                    "threshold": threshold,
                    "review_threshold": review,
                    "threshold_source": parameters["source"],
                    **row,
                },
            )
        )

    measurements.sort(key=lambda entry: (-float(entry["containment"]), entry["path"]))
    return (
        findings,
        gaps,
        {
            "bundle": subject,
            "lane": lane,
            "agent_visible": visible_rows,
            "carrier_count": len(measurements),
            "surfaced_canary_tokens": surfaced,
            "measurements": measurements,
        },
    )


def _run_containment(base: Path, bundles: list[Path]) -> InstrumentResult:
    """Run G-LEAK-CONTAINMENT, the carrier-leak half of contract step 8b."""
    parameters = load_neardup_parameters(base)
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    rows: list[dict[str, Any]] = []
    for bundle in bundles:
        bundle_findings, bundle_gaps, row = _containment_for_bundle(bundle, base, parameters)
        findings.extend(bundle_findings)
        gaps.extend(bundle_gaps)
        rows.append(row)
    standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=CONTAINMENT_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "bundles": rows,
            "ngram_width": NGRAM_WIDTH,
            "normalization_domain": core.normalization_domain(),
            "neardup_parameters": parameters,
        },
    )


def _internal_error_result(instrument: str, gap_id: str, error: Exception) -> InstrumentResult:
    return InstrumentResult(
        instrument=instrument,
        ran=False,
        gaps=[
            CoverageGap(
                gap_id=gap_id,
                instrument=instrument,
                surface="bundle_bytes",
                reason="instrument-raised-internally",
                caps=Disposition.HOLD,
                statement=_ascii_text(
                    f"{instrument} raised {type(error).__name__} before producing a "
                    f"determination, so it covered nothing: {error}"
                ),
            )
        ],
        standing=Standing.INSUFFICIENT_EVIDENCE,
    )


def _no_bundle_result(instrument: str) -> InstrumentResult:
    return InstrumentResult(
        instrument=instrument,
        ran=False,
        gaps=[
            CoverageGap(
                gap_id=NO_BUNDLE_GAP_ID,
                instrument=instrument,
                surface="bundle_bytes",
                reason="no-resident-bundle-resolved",
                caps=Disposition.HOLD,
                statement=_ascii_text(
                    f"{instrument} resolved no resident bundle carrying a task manifest, so the "
                    "leak gate had no substrate and its silence is a gap, not a clean result."
                ),
            )
        ],
        standing=Standing.INSUFFICIENT_EVIDENCE,
    )


def run_family(base: Path, reconnaissance: recon.Recon) -> list[InstrumentResult]:
    """Run the step 8b leak gate over every resident bundle.

    Returns G-LEAK-CANARY then G-LEAK-CONTAINMENT. Neither instrument raises: an
    internal failure and an empty bundle set each become a coverage gap, because
    an instrument that returns nothing without saying why reads downstream as a
    pass and caps the gate at BLOCK under the InstrumentResult contract.
    """
    del reconnaissance
    results: list[InstrumentResult] = []
    try:
        bundles = core.bundle_roots(base)
    except OSError as error:
        return [
            _internal_error_result(CANARY_INSTRUMENT, CANARY_INTERNAL_GAP_ID, error),
            _internal_error_result(CONTAINMENT_INSTRUMENT, CONTAINMENT_INTERNAL_GAP_ID, error),
        ]

    for instrument, gap_id, runner in (
        (CANARY_INSTRUMENT, CANARY_INTERNAL_GAP_ID, _run_canary),
        (CONTAINMENT_INSTRUMENT, CONTAINMENT_INTERNAL_GAP_ID, _run_containment),
    ):
        if not bundles:
            results.append(_no_bundle_result(instrument))
            continue
        try:
            results.append(runner(base, bundles))
        except Exception as error:
            results.append(_internal_error_result(instrument, gap_id, error))
    return results


__all__ = [
    "CANARY_INSTRUMENT",
    "CONTAINMENT_INSTRUMENT",
    "DESIGNATED_CANARY_SLOTS",
    "NGRAM_WIDTH",
    "agent_visible_files",
    "canary_matches",
    "inspect_slot",
    "load_crucible_view",
    "load_neardup_parameters",
    "private_carrier_files",
    "run_family",
    "view_task_hash",
]
