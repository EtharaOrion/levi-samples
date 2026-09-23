"""Task-collision and bundle-lineage instruments for contract steps 8v and 8w.

Two instruments live here because both reason about the relation between one
bundle and another bundle, and both are forbidden to resolve that relation from
producer-owned state.

G-DEL-COLLISION discharges step 8v. It runs the bound implementation,
``trinity/tools/collision.py check ./ <uuid> --json``, from the verification
root and retains the raw artifact whole, and it independently derives its own
design fingerprint from committed bundle bytes alone. The independent
derivation is not redundancy: the bound implementation is producer-owned code,
and an auditor whose only collision evidence is the producer's own tool cannot
detect a tool that stopped reporting. The fingerprint has two halves. The
structure key is a digest over the resolved environment identity together with
the sorted ``tests/`` and ``solution/`` path sets, which is the shell a task was
built in. The statement signature is a 128-position minhash over word shingles
of ``instruction.md``, normalized with ``core.normalize_text``, which is the
audit harness's own normalizer and never the authoring one, so a producer that
changes its normalization cannot move this signature.

The tier vocabulary is fixed and integer-valued so that a tier is recomputable
from the recorded evidence: ``duplicate`` when structure keys are identical or
statement signatures agree on at least 116 of 128 positions, ``near`` at 89, and
``related`` at 64. A duplicate is a retained ``task-collision``
delivery-integrity finding capping the later-sealed member at BLOCK. A ``near``
pair with no recorded adjudication is a coverage gap capping at HOLD with reason
``collision-unreviewed``. A ``related`` pair is recorded and caps nothing.

Seal order is read from a sealed queue and never from an author declaration,
because the later-sealed member is the member that should have been refused at
the merge and an author is the party with the motive to reorder that claim. No
sealed queue exists at this root, so a duplicate tier could not name its later
member and that inability is itself recorded as a gap rather than resolved by
falling back to a declaration.

This instrument reads neither ``.seed/designs/`` nor ``.seed/batch.yaml``: both
carry archetype and category the auditor must not hold, and holding them would
let the auditor's judgement be shaped by the author's own taxonomy. This is TASK
collision and is never the near-duplicate contamination screen. The two answer
different questions, one about two bundles in this corpus and one about this
corpus against an external index, and neither discharges the other.

G-DEL-LINEAGE discharges step 8w. Before any other instrument reads a byte it
records two auditor-owned registries, once per sealed digest and never
rewritten: a design fingerprint at ``.audit/fingerprints/<uuid>/<digest>.json``
and a verbatim copy of ``solution/predecessor.yaml`` at
``.audit/lineage/<uuid>/<digest>.json``, or an explicit ``absent`` marker where
that file does not exist. The ordering requirement is discharged by
create-only-ness rather than by dispatch order: both registries are pure
functions of committed bytes and neither is ever rewritten, so the bytes a
first-run registry records are the bytes any later run would record, and no
earlier instrument can have moved them.

``<digest>`` is the bundle's canonical digest as this module derives it:
``core.tree_digest`` over every committed relative path under the bundle. That
choice is deliberate over the alternatives. The manifest digest alone would
miss every change outside ``task.toml``. A producer-declared bundle hash would
make the registry key a producer claim, which defeats the purpose of an
auditor-owned registry. ``tree_digest`` records each member's path beside its
content digest and records a vanished member as the literal token ``absent``,
so a deletion moves the key instead of silently preserving it.

For a present lineage record only, the record is verified against auditor-owned
state and never against ``.seed/``: it must parse under a closed
``trinity.predecessor/v1`` schema carrying no extra, missing or prose-bearing
key; ``predecessor_uuid`` must be sealed at ``predecessor_digest`` in a queue
stream under ``.podium/queue/``; ``.audit/verdicts/<predecessor_uuid>/
<predecessor_digest>.json`` must record ``retained`` or ``clean``; ``lineage_id``
must equal the predecessor's recorded lineage_id or else the predecessor's uuid;
and ``attempt`` must equal the predecessor's attempt plus one, with an absent
record meaning attempt 1. Any failure is a retained ``lineage-unbound`` finding
capping at BLOCK, and an attempt above 4 is ``lineage-exhausted`` capping at
BLOCK.

Where every record is absent, as it is at this root, the correct outcome is
registries written, attempt 1 for every bundle, and no lineage finding. The
instrument records DEMONSTRATED_COVERAGE for the checks it genuinely performed
and records the checks it never exercised by name as INSUFFICIENT_EVIDENCE, so
an unexercised check is never readable as a clean one.

House rule: the rationale for every decision lives in these docstrings because
the contract is prompt-only, so the harness itself has to carry the reasoning as
audit evidence.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import tomllib
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
    RawArtifact,
    Severity,
    Standing,
)
from registry import REGISTRY, Category, EvidenceClass, Instrument

CRITICAL_CLASS = "delivery-format-and-ground-truth-integrity"

SIGNATURE_WIDTH = 128

SHINGLE_WORDS = 5

DUPLICATE_MATCHES = 116

NEAR_MATCHES = 89

RELATED_MATCHES = 64

ATTEMPT_CAP = 4

PREDECESSOR_SCHEMA = "trinity.predecessor/v1"

PREDECESSOR_KEYS: frozenset[str] = frozenset(
    {"schema", "predecessor_uuid", "predecessor_digest", "lineage_id", "attempt"}
)

PROSE_BEARING_MAX_WORDS = 8

COLLISION_TOOL = "./trinity/tools/collision.py"

COLLISION_TIMEOUT_SECONDS = 300.0

FINGERPRINT_DIRNAME = "fingerprints"

LINEAGE_DIRNAME = "lineage"

VERDICT_DIRNAME = "verdicts"

QUEUE_ROOT = Path(".podium") / "queue"

LINEAGE_CHECKS: tuple[str, ...] = (
    "record-presence-resolved",
    "closed-schema-parse",
    "predecessor-sealed-in-queue",
    "predecessor-verdict-recorded",
    "lineage-id-matches-predecessor",
    "attempt-is-predecessor-plus-one",
    "attempt-within-cap",
)


def _register() -> None:
    """Declare both step 8v and 8w instruments under the twelve-field schema.

    Phase 1 item 4 makes ``disposition_cap_on_absence`` the load-bearing field,
    and neither row may cap at SHIP: a collision screen that did not run and a
    lineage registry that was never written are both coverage gaps, never
    passes.
    """
    rows = (
        Instrument(
            name="G-DEL-COLLISION",
            category=Category.DELIVERY,
            binary="python3",
            ecosystems=("*",),
            timeout_seconds=COLLISION_TIMEOUT_SECONDS,
            required_conditions=("committed task bundles present",),
            critical_capability="task-collision detection over committed design fingerprints",
            evidence_class=EvidenceClass.RAW_TOOL_OUTPUT,
            requires_parser=True,
            requires_raw_artifact=True,
            disposition_cap_on_absence=Disposition.HOLD,
            argv_builder=lambda uuid: ["python3", COLLISION_TOOL, "check", "./", uuid, "--json"],
            notes="Never the near-duplicate contamination screen; neither discharges the other.",
        ),
        Instrument(
            name="G-DEL-LINEAGE",
            category=Category.LINEAGE,
            binary="",
            ecosystems=("*",),
            timeout_seconds=120.0,
            required_conditions=("committed task bundles present",),
            critical_capability="auditor-owned lineage registry and successor ancestry binding",
            evidence_class=EvidenceClass.RECOMPUTED_DIGEST,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.BLOCK,
            notes="Registries are create-only and are never verified against .seed/.",
        ),
    )
    for row in rows:
        if row.name not in REGISTRY:
            REGISTRY.register(row)


_register()


def _read_text(path: Path) -> str:
    """Read one committed file as text, failing closed to the empty string."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _load_toml(path: Path) -> dict[str, Any]:
    """Parse one task manifest, failing closed to an empty declaration."""
    try:
        with path.open("rb") as handle:
            loaded = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def bundles_of(base: Path) -> list[Path]:
    """Every resident bundle directory, derived from committed bytes alone."""
    return sorted(core.bundle_roots(base), key=lambda path: path.name)


def committed_relative_paths(bundle: Path) -> list[str]:
    """Every committed file under a bundle as a sorted POSIX relative path list."""
    found: list[str] = []
    for path in bundle.rglob("*"):
        if path.is_file() and not path.is_symlink():
            found.append(path.relative_to(bundle).as_posix())
    return sorted(found)


def bundle_digest(bundle: Path) -> str:
    """The canonical digest this module keys both auditor-owned registries on.

    ``core.tree_digest`` over every committed relative path. Each member
    contributes its path beside its content digest and a missing member
    contributes the token ``absent``, so the key moves on an addition, an edit
    and a deletion alike, which is what makes a create-only registry safe: a
    changed bundle lands at a new key rather than overwriting the old record.
    """
    return core.tree_digest(bundle, committed_relative_paths(bundle))


def environment_identity(bundle: Path) -> str:
    """Resolve the environment half of the structure key from committed bytes.

    The manifest's pinned runtime image is preferred because it is the identity
    a consumer actually runs. Where no image is pinned the committed Dockerfile
    is digested instead, so a bundle that ships a build recipe rather than a
    pinned image still contributes a real identity, and only a bundle carrying
    neither resolves to ``unbound``.
    """
    manifest = _load_toml(bundle / "task.toml")
    environment = manifest.get("environment")
    if isinstance(environment, dict):
        image = environment.get("docker_image")
        if isinstance(image, str) and image:
            return f"image:{image}"
    dockerfile = bundle / "environment" / "Dockerfile"
    if dockerfile.is_file():
        return f"dockerfile:{core.sha256_path(dockerfile)}"
    return "unbound"


def statement_signature(text: str) -> tuple[str, ...]:
    """A 128-position minhash over normalized word shingles of the statement.

    Each position is the minimum of a seeded blake2b digest over the shingle
    set, so two statements agree at a position exactly when they share the
    shingle that minimizes that seed. The number of agreeing positions is an
    unbiased estimate of shingle Jaccard similarity, and it is an integer, which
    is what lets a tier threshold be stated exactly and recomputed from the
    recorded evidence rather than trusted.

    ``core.normalize_text`` is the audit harness's own normalizer. Step 8b
    forbids normalizing a designated slot with the authoring normalizer, and the
    same reasoning applies here: a signature computed under producer-owned
    normalization moves whenever the producer changes it.
    """
    tokens = core.normalize_text(text).split()
    if not tokens:
        return ()
    if len(tokens) < SHINGLE_WORDS:
        shingles = {" ".join(tokens)}
    else:
        shingles = {
            " ".join(tokens[index : index + SHINGLE_WORDS])
            for index in range(len(tokens) - SHINGLE_WORDS + 1)
        }
    ordered = sorted(shingles)
    digests = [hashlib.blake2b(shingle.encode("utf-8"), digest_size=8) for shingle in ordered]
    signature: list[str] = []
    for seed in range(SIGNATURE_WIDTH):
        salt = str(seed).encode("utf-8")
        signature.append(
            min(
                hashlib.blake2b(digest.digest() + salt, digest_size=8).hexdigest()
                for digest in digests
            )
        )
    return tuple(signature)


def design_fingerprint(bundle: Path) -> dict[str, Any]:
    """Derive this auditor's own design fingerprint from committed bundle bytes.

    The structure key answers what shell the task was built in and the
    statement signature answers what the task says. They are kept separate
    because a batch authored from one template against one pinned image carries
    one shell across every unrelated slot, so a shared shell alone is never
    evidence that two bundles are the same task.
    """
    environment = environment_identity(bundle)
    relatives = committed_relative_paths(bundle)
    tests_paths = sorted(
        path.removeprefix("tests/") for path in relatives if path.startswith("tests/")
    )
    solution_paths = sorted(
        path.removeprefix("solution/") for path in relatives if path.startswith("solution/")
    )
    signature = statement_signature(_read_text(bundle / "instruction.md"))
    return {
        "uuid": bundle.name,
        "bundle_digest": bundle_digest(bundle),
        "environment_identity": environment,
        "environment_key": core.sha256_bytes(environment.encode("utf-8")),
        "structure_key": core.canonical_digest(
            {
                "environment": environment,
                "solution_paths": solution_paths,
                "tests_paths": tests_paths,
            }
        ),
        "statement_signature": list(signature),
        "signature_width": SIGNATURE_WIDTH,
        "shingle_words": SHINGLE_WORDS,
        "normalization_domain": core.normalization_domain(),
        "tests_paths": tests_paths,
        "solution_paths": solution_paths,
    }


def signature_matches(left: dict[str, Any], right: dict[str, Any]) -> int:
    """Count the signature positions on which two fingerprints agree."""
    a = left.get("statement_signature") or []
    b = right.get("statement_signature") or []
    if not a or not b:
        return 0
    return sum(1 for x, y in zip(a, b, strict=False) if x == y)


def collision_tier(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve the collision tier for one ordered pair of fingerprints.

    A bundle whose statement says nothing has no design to repeat, so an empty
    signature yields no tier rather than matching everything by vacuity.
    """
    if not left.get("statement_signature") or not right.get("statement_signature"):
        return None
    matches = signature_matches(left, right)
    same_shell = left["structure_key"] == right["structure_key"]
    for fired, tier, reason in (
        (same_shell, "duplicate", "structure-key"),
        (matches >= DUPLICATE_MATCHES, "duplicate", "statement-signature"),
        (matches >= NEAR_MATCHES, "near", "statement-signature"),
        (matches >= RELATED_MATCHES, "related", "statement-signature"),
    ):
        if fired:
            members = sorted((left["uuid"], right["uuid"]))
            return {
                "left": members[0],
                "right": members[1],
                "tier": tier,
                "reason": reason,
                "matches": matches,
                "signature_width": SIGNATURE_WIDTH,
                "structure_keys_identical": same_shell,
            }
    return None


def sealed_queue_streams(base: Path) -> list[str]:
    """Every sealed queue stream available to resolve seal order.

    Seal order is the merge-time fact that decides which member of a duplicate
    pair is refused. It is read only from a sealed queue, because an author
    declaration of its own position in the seal order is exactly the claim a
    colliding author has a motive to move.
    """
    queue = base / QUEUE_ROOT
    if not queue.is_dir():
        return []
    return sorted(child.name for child in queue.iterdir() if child.is_file())


def run_collision(base: Path) -> InstrumentResult:
    """G-DEL-COLLISION, contract step 8v: task collision over design fingerprints.

    The bound implementation runs once per bundle and its raw artifact is kept
    whole, exit code and streams included, so a reader can re-derive what the
    producer's own tool reported. Its refusal is not converted into a pass: if
    the tool adjudicates nothing, an explicit gap records that the bound channel
    produced no determination, and only the independent derivation stands.

    Every unordered pair of resident bundles is then compared under this
    auditor's own fingerprint. A duplicate is a retained ``task-collision``
    finding capping the later-sealed member at BLOCK, and where no sealed queue
    exists to name that member, the finding caps every member of the pair and a
    gap records that seal order was unresolvable, because refusing to name a
    member is not the same as having no member to refuse.
    """
    bundles = bundles_of(base)
    artifacts: list[RawArtifact] = []
    tool_rows: list[dict[str, Any]] = []
    for bundle in bundles:
        artifact = core.run_capture(
            ["python3", COLLISION_TOOL, "check", "./", bundle.name, "--json"],
            artifact_id=f"collision-check-{bundle.name}",
            cwd=base,
            timeout=COLLISION_TIMEOUT_SECONDS,
            env={"PYTHONDONTWRITEBYTECODE": "1"},
        )
        artifacts.append(artifact)
        parsed: Any = None
        if artifact.stdout.strip().startswith(("{", "[")):
            try:
                parsed = json.loads(artifact.stdout)
            except ValueError:
                parsed = None
        tool_rows.append(
            {
                "uuid": bundle.name,
                "exit_code": artifact.exit_code,
                "blocked_reason": artifact.blocked_reason,
                "adjudicated": parsed is not None,
                "parsed": parsed,
                "stdout_head": artifact.stdout.strip().splitlines()[:3],
            }
        )

    fingerprints = {bundle.name: design_fingerprint(bundle) for bundle in bundles}
    pairs: list[dict[str, Any]] = []
    for left, right in itertools.combinations(sorted(fingerprints), 2):
        tier = collision_tier(fingerprints[left], fingerprints[right])
        pairs.append(
            {
                "left": left,
                "right": right,
                "matches": signature_matches(fingerprints[left], fingerprints[right]),
                "structure_keys_identical": (
                    fingerprints[left]["structure_key"] == fingerprints[right]["structure_key"]
                ),
                "tier": tier["tier"] if tier else "none",
                "reason": tier["reason"] if tier else "",
            }
        )

    streams = sealed_queue_streams(base)
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []

    if not any(row["adjudicated"] for row in tool_rows):
        gaps.append(
            CoverageGap(
                gap_id="D-DEL-COLLISION-TOOL-UNADJUDICATED",
                instrument="G-DEL-COLLISION",
                surface="task_collision",
                reason="bound-implementation-produced-no-determination",
                caps=Disposition.HOLD,
                subject="project",
                statement=(
                    "The bound implementation trinity/tools/collision.py check produced no "
                    "machine-readable adjudication for any resident bundle, so the "
                    "producer-owned collision channel is unverified and only this "
                    "auditor's independently derived fingerprint comparison stands. Its "
                    "raw artifacts are retained whole as evidence of the refusal."
                ),
            )
        )

    for pair in pairs:
        if pair["tier"] == "duplicate":
            findings.append(
                Finding(
                    finding_id=(f"F-DEL-COLLISION-TASK-COLLISION-{pair['left']}-{pair['right']}"),
                    instrument="G-DEL-COLLISION",
                    critical_class=CRITICAL_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=f"{pair['left']},{pair['right']}",
                    statement=(
                        "task-collision: two resident bundles are the same task under "
                        "different bytes at duplicate tier by " + pair["reason"] + "."
                    ),
                    evidence={"pair": pair, "sealed_queue_streams": streams},
                )
            )
            if not streams:
                gaps.append(
                    CoverageGap(
                        gap_id=(
                            f"D-DEL-COLLISION-SEAL-ORDER-UNRESOLVED-{pair['left']}-{pair['right']}"
                        ),
                        instrument="G-DEL-COLLISION",
                        surface="task_collision",
                        reason="sealed-queue-absent",
                        caps=Disposition.HOLD,
                        subject=f"{pair['left']},{pair['right']}",
                        statement=(
                            "A duplicate-tier pair fired and no sealed queue exists under "
                            ".podium/queue/, so the later-sealed member cannot be named "
                            "and the finding caps both members rather than resolving seal "
                            "order from an author declaration."
                        ),
                    )
                )
        elif pair["tier"] == "near":
            gaps.append(
                CoverageGap(
                    gap_id=f"D-DEL-COLLISION-UNREVIEWED-{pair['left']}-{pair['right']}",
                    instrument="G-DEL-COLLISION",
                    surface="task_collision",
                    reason="collision-unreviewed",
                    caps=Disposition.HOLD,
                    subject=f"{pair['left']},{pair['right']}",
                    statement=(
                        "A near-tier collision pair carries no recorded adjudication, so "
                        "whether the two bundles are the same task is undetermined."
                    ),
                )
            )

    return InstrumentResult(
        instrument="G-DEL-COLLISION",
        ran=True,
        findings=findings,
        gaps=gaps,
        artifacts=artifacts,
        standing=(Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE),
        notes={
            "bound_implementation": tool_rows,
            "pairs": pairs,
            "fingerprints": {
                uuid: {key: value for key, value in row.items() if key != "statement_signature"}
                for uuid, row in fingerprints.items()
            },
            "tier_thresholds": {
                "duplicate_matches": DUPLICATE_MATCHES,
                "near_matches": NEAR_MATCHES,
                "related_matches": RELATED_MATCHES,
                "signature_width": SIGNATURE_WIDTH,
            },
            "sealed_queue_root": str(base / QUEUE_ROOT),
            "sealed_queue_streams": streams,
            "screen_identity": (
                "task collision over two resident bundles; this is never the "
                "near-duplicate contamination screen against an external index, and "
                "neither discharges the other"
            ),
            "forbidden_inputs_not_read": [".seed/designs/", ".seed/batch.yaml"],
        },
    )


def _registry_write(path: Path, payload: dict[str, Any]) -> str:
    """Write one auditor-owned registry record, create-only, never rewriting.

    Create-only is what makes the registry an auditor-owned fact rather than a
    running summary: a record written under a sealed digest is the record for
    that digest forever, so a later run that disagrees produces a second record
    at a second key rather than erasing the first.
    """
    if path.exists():
        return "preexisting"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return "created"


def predecessor_record(bundle: Path) -> dict[str, Any]:
    """Read solution/predecessor.yaml verbatim, or resolve it as explicitly absent.

    Absence is recorded as a marker rather than as silence. A lineage registry
    that simply held no entry for a bundle would be indistinguishable from one
    that was never asked, and step 8w requires the absent case to be a recorded
    determination meaning attempt 1.
    """
    path = bundle / "solution" / "predecessor.yaml"
    if not path.is_file():
        return {
            "present": False,
            "state": "absent",
            "path": "solution/predecessor.yaml",
            "verbatim": "",
            "parsed": None,
            "parse_error": "",
            "source_sha256": "",
        }
    verbatim = _read_text(path)
    parsed: Any = None
    error = ""
    try:
        parsed = yaml.safe_load(verbatim)
    except yaml.YAMLError as failure:
        error = str(failure)
    return {
        "present": True,
        "state": "present",
        "path": "solution/predecessor.yaml",
        "verbatim": verbatim,
        "parsed": parsed if isinstance(parsed, dict) else None,
        "parse_error": error,
        "source_sha256": core.sha256_path(path),
    }


def _schema_violations(parsed: dict[str, Any] | None) -> list[str]:
    """Check a present record against the closed trinity.predecessor/v1 schema.

    The schema is closed in all three directions: an extra key, a missing key
    and a prose-bearing value are each violations. Prose is rejected because a
    free-form value in a record the auditor parses is a covert-payload and
    prompt-injection surface, and because a field that can hold an explanation
    can hold an excuse.
    """
    if parsed is None:
        return ["record-does-not-parse-as-a-mapping"]
    violations: list[str] = []
    keys = set(parsed)
    for extra in sorted(keys - PREDECESSOR_KEYS):
        violations.append(f"extra-key:{extra}")
    for missing in sorted(PREDECESSOR_KEYS - keys):
        violations.append(f"missing-key:{missing}")
    if str(parsed.get("schema") or "") != PREDECESSOR_SCHEMA:
        violations.append("schema-token-mismatch")
    for key, value in sorted(parsed.items()):
        if isinstance(value, str) and len(value.split()) > PROSE_BEARING_MAX_WORDS:
            violations.append(f"prose-bearing-key:{key}")
    attempt = parsed.get("attempt")
    if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
        violations.append("attempt-is-not-a-positive-integer")
    return violations


def _queue_seals(base: Path, uuid: str, digest: str) -> dict[str, Any]:
    """Resolve whether a predecessor uuid is sealed at a digest in a queue stream."""
    queue = base / QUEUE_ROOT
    streams = sealed_queue_streams(base)
    sealed = False
    for name in streams:
        text = _read_text(queue / name)
        if uuid in text and digest in text:
            sealed = True
            break
    return {"queue_present": queue.is_dir(), "streams": streams, "sealed": sealed}


def _recorded_verdict(base: Path, uuid: str, digest: str) -> dict[str, Any]:
    """Read the auditor's own verdict for a predecessor at a digest."""
    path = base / core.AUDIT_DIRNAME / VERDICT_DIRNAME / uuid / f"{digest}.json"
    if not path.is_file():
        return {"path": str(path), "present": False, "standing": ""}
    document = json.loads(_read_text(path) or "{}")
    standing = ""
    if isinstance(document, dict):
        standing = str(document.get("standing") or document.get("verdict") or "")
    return {"path": str(path), "present": True, "standing": standing}


def _lineage_findings(
    base: Path, bundle: Path, record: dict[str, Any]
) -> tuple[list[Finding], dict[str, Any]]:
    """Verify one present lineage record against auditor-owned state only.

    Every input is auditor-owned or a sealed queue: the closed schema, the
    ``.podium/queue/`` seal, the ``.audit/verdicts/`` standing. Nothing under
    ``.seed/`` is consulted, because verifying a producer's ancestry claim
    against the producer's own state proves only internal consistency.
    """
    findings: list[Finding] = []
    parsed = record["parsed"] if isinstance(record["parsed"], dict) else None
    violations = _schema_violations(parsed)
    detail: dict[str, Any] = {"schema_violations": violations}

    if violations or parsed is None:
        findings.append(
            Finding(
                finding_id=f"F-DEL-LINEAGE-UNBOUND-SCHEMA-{bundle.name}",
                instrument="G-DEL-LINEAGE",
                critical_class=CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.BLOCK,
                bucket=Bucket.D,
                subject=bundle.name,
                statement=(
                    "lineage-unbound: the committed predecessor record does not parse "
                    "under the closed trinity.predecessor/v1 schema: " + ", ".join(violations)
                ),
                evidence=detail,
            )
        )
        return findings, detail

    predecessor_uuid = str(parsed.get("predecessor_uuid") or "")
    predecessor_digest = str(parsed.get("predecessor_digest") or "")
    lineage_id = str(parsed.get("lineage_id") or "")
    attempt = int(parsed.get("attempt"))

    seal = _queue_seals(base, predecessor_uuid, predecessor_digest)
    verdict = _recorded_verdict(base, predecessor_uuid, predecessor_digest)
    predecessor_record_row = predecessor_registry_record(base, predecessor_uuid, predecessor_digest)
    expected_lineage = predecessor_record_row.get("lineage_id") or predecessor_uuid
    expected_attempt = int(predecessor_record_row.get("attempt") or 1) + 1

    detail.update(
        {
            "predecessor_uuid": predecessor_uuid,
            "predecessor_digest": predecessor_digest,
            "lineage_id": lineage_id,
            "attempt": attempt,
            "queue": seal,
            "verdict": verdict,
            "expected_lineage_id": expected_lineage,
            "expected_attempt": expected_attempt,
        }
    )

    unbound: list[str] = []
    if not seal["sealed"]:
        unbound.append("predecessor-not-sealed-at-digest-in-any-queue-stream")
    if verdict["standing"] not in {"retained", "clean"}:
        unbound.append("predecessor-verdict-not-recorded-as-retained-or-clean")
    if lineage_id != expected_lineage:
        unbound.append("lineage-id-does-not-match-predecessor")
    if attempt != expected_attempt:
        unbound.append("attempt-is-not-predecessor-attempt-plus-one")

    if unbound:
        findings.append(
            Finding(
                finding_id=f"F-DEL-LINEAGE-UNBOUND-{bundle.name}",
                instrument="G-DEL-LINEAGE",
                critical_class=CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.BLOCK,
                bucket=Bucket.D,
                subject=bundle.name,
                statement=(
                    "lineage-unbound: the declared ancestry is not confirmed by the "
                    "auditor's own registries: " + ", ".join(unbound)
                ),
                evidence=detail,
            )
        )
    if attempt > ATTEMPT_CAP:
        findings.append(
            Finding(
                finding_id=f"F-DEL-LINEAGE-EXHAUSTED-{bundle.name}",
                instrument="G-DEL-LINEAGE",
                critical_class=CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.BLOCK,
                bucket=Bucket.D,
                subject=bundle.name,
                statement=(
                    f"lineage-exhausted: attempt {attempt} passes the cap of {ATTEMPT_CAP}."
                ),
                evidence=detail,
            )
        )
    return findings, detail


def predecessor_registry_record(base: Path, uuid: str, digest: str) -> dict[str, Any]:
    """Read a predecessor's own lineage registry entry, failing closed to absent.

    An absent record means attempt 1 under step 8w, so the fallback is a
    determination rather than a hole.
    """
    path = base / core.AUDIT_DIRNAME / LINEAGE_DIRNAME / uuid / f"{digest}.json"
    if not path.is_file():
        return {"present": False, "attempt": 1, "lineage_id": ""}
    document = json.loads(_read_text(path) or "{}")
    if not isinstance(document, dict):
        return {"present": False, "attempt": 1, "lineage_id": ""}
    parsed = document.get("parsed")
    if not isinstance(parsed, dict):
        return {"present": True, "attempt": 1, "lineage_id": ""}
    attempt = parsed.get("attempt")
    return {
        "present": True,
        "attempt": attempt if isinstance(attempt, int) and not isinstance(attempt, bool) else 1,
        "lineage_id": str(parsed.get("lineage_id") or ""),
    }


def run_lineage(base: Path) -> InstrumentResult:
    """G-DEL-LINEAGE, contract step 8w: auditor-owned registries and ancestry binding.

    Both registries are written first and create-only, so their bytes are a
    function of committed bytes alone and no other instrument could have moved
    them. A present record is then verified against auditor-owned state and
    never against ``.seed/``. Where every record is absent, the determination is
    attempt 1 with no lineage finding, and the checks that never had a record to
    exercise are named individually as insufficient evidence so that an
    unexercised check is never readable as a clean one.
    """
    audit = base / core.AUDIT_DIRNAME
    findings: list[Finding] = []
    per_bundle: list[dict[str, Any]] = []
    exercised: set[str] = set()

    for bundle in bundles_of(base):
        digest = bundle_digest(bundle)
        fingerprint = design_fingerprint(bundle)
        record = predecessor_record(bundle)
        exercised.add("record-presence-resolved")

        fingerprint_path = audit / FINGERPRINT_DIRNAME / bundle.name / f"{digest}.json"
        lineage_path = audit / LINEAGE_DIRNAME / bundle.name / f"{digest}.json"
        fingerprint_state = _registry_write(fingerprint_path, fingerprint)
        lineage_state = _registry_write(
            lineage_path,
            {
                "uuid": bundle.name,
                "bundle_digest": digest,
                "digest_basis": (
                    "core.tree_digest over every committed relative path under the bundle"
                ),
                "source_path": record["path"],
                "state": record["state"],
                "source_sha256": record["source_sha256"],
                "verbatim": record["verbatim"],
                "parsed": record["parsed"],
                "parse_error": record["parse_error"],
            },
        )

        detail: dict[str, Any] = {}
        attempt = 1
        if record["present"]:
            bundle_findings, detail = _lineage_findings(base, bundle, record)
            findings.extend(bundle_findings)
            exercised.update(LINEAGE_CHECKS)
            attempt = int(detail.get("attempt") or 1)

        per_bundle.append(
            {
                "uuid": bundle.name,
                "bundle_digest": digest,
                "fingerprint_registry": {
                    "path": str(fingerprint_path.relative_to(base)),
                    "write_state": fingerprint_state,
                },
                "lineage_registry": {
                    "path": str(lineage_path.relative_to(base)),
                    "write_state": lineage_state,
                    "record_state": record["state"],
                },
                "attempt": attempt,
                "attempt_basis": (
                    "an absent predecessor record means attempt 1 under step 8w"
                    if not record["present"]
                    else "read from the committed predecessor record"
                ),
                "verification": detail,
            }
        )

    unexercised = sorted(set(LINEAGE_CHECKS) - exercised)
    return InstrumentResult(
        instrument="G-DEL-LINEAGE",
        ran=True,
        findings=findings,
        gaps=[],
        artifacts=[],
        standing=(Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE),
        notes={
            "per_bundle": per_bundle,
            "registry_roots": {
                "fingerprints": str((audit / FINGERPRINT_DIRNAME).relative_to(base)),
                "lineage": str((audit / LINEAGE_DIRNAME).relative_to(base)),
            },
            "registry_semantics": "create-only; a record is never rewritten once written",
            "digest_basis": (
                "core.tree_digest over every committed relative path under the bundle, so "
                "an addition, an edit or a deletion all move the registry key"
            ),
            "checks_demonstrated": sorted(exercised),
            "checks_not_exercised": unexercised,
            "checks_not_exercised_standing": Standing.INSUFFICIENT_EVIDENCE.value,
            "checks_not_exercised_basis": (
                "every resident bundle resolves solution/predecessor.yaml as absent, so "
                "these checks had no record to run against and are recorded as "
                "unexercised rather than as clean"
            ),
            "verified_against": [
                ".podium/queue/",
                ".audit/verdicts/",
                ".audit/lineage/",
            ],
            "never_verified_against": [".seed/"],
        },
    )


def _guard(name: str, runner: Any, base: Path) -> InstrumentResult:
    """Run one instrument and convert any unexpected failure into a coverage gap.

    run_family must never raise, and an instrument that crashed must never read
    as a clean result, so a crash becomes an explicit gap naming the exception.
    """
    try:
        return runner(base)
    except Exception as error:
        return InstrumentResult(
            instrument=name,
            ran=False,
            gaps=[
                CoverageGap(
                    gap_id=f"D-INSTRUMENT-CRASHED-{name}",
                    instrument=name,
                    surface="harness_code",
                    reason="instrument-raised",
                    caps=Disposition.HOLD,
                    subject="project",
                    statement=(
                        f"The instrument {name} raised {type(error).__name__} and produced "
                        f"no determination: {error}"
                    ),
                )
            ],
        )


def run_family(base: Path, reconnaissance: Any) -> list[InstrumentResult]:
    """Execute steps 8v and 8w and return both results.

    G-DEL-LINEAGE is dispatched first because step 8w requires its registries to
    be recorded before any other instrument reads a byte. Dispatch order alone
    cannot discharge that requirement across families, so the registries are
    additionally create-only and derived from committed bytes alone, which is
    what actually makes the recorded bytes independent of when they were
    recorded.
    """
    results = [
        _guard("G-DEL-LINEAGE", run_lineage, base),
        _guard("G-DEL-COLLISION", run_collision, base),
    ]
    recorded = getattr(reconnaissance, "git_sha", "")
    if recorded:
        results[0].notes["recon_git_sha"] = str(recorded)
    return results


__all__ = [
    "DUPLICATE_MATCHES",
    "NEAR_MATCHES",
    "RELATED_MATCHES",
    "SIGNATURE_WIDTH",
    "bundle_digest",
    "bundles_of",
    "collision_tier",
    "design_fingerprint",
    "environment_identity",
    "predecessor_record",
    "run_collision",
    "run_family",
    "run_lineage",
    "sealed_queue_streams",
    "signature_matches",
    "statement_signature",
]
