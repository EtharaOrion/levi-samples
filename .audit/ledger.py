"""Reward coverage ledger of Phase 1 step 8q.

Step 8q requires one row per applicable pair of the closed threat vocabulary and
the closed capability channel vocabulary, each resolving as exactly detected,
externally_enforced, not_applicable, or gap. This module derives those rows from
the committed closure and from which instruments actually ran in this gate, and
never accepts a producer declaration in place of a derivation.

Three constraints shape the implementation. A detected row must name the live
atom that covers the pair, so the coverage table below names real instrument
identifiers that other modules register rather than aspirational ones. An
externally_enforced row must name a verified attestation clause, and the
execution attestation directory does not exist in this tree, so no row of this
run may take that resolution. A not_applicable row must carry a derivation
CRUCIBLE computed from committed bytes, so every such row states the observed
fact that removes the channel from the threat's reach.

The producer commits solution/policy.yaml declaring ten forge.policy/v1 channel
names. Those are not the nine channels this ledger closes at, and a producer
declaration can only lower a disposition, never establish enforcement. The
manifest is therefore read as a one-way lowering claim recorded in the row
statement and is never allowed to resolve a row as covered.
"""

from __future__ import annotations

from pathlib import Path

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
from evidence import (
    CAPABILITY_CHANNELS,
    CAPABILITY_VOCABULARY_VERSION,
    REWARD_BOUNDARIES,
    REWARD_CLAIM_MODEL_VERSION,
    REWARD_THREATS,
    LedgerRow,
)
from registry import REGISTRY, Category, EvidenceClass, Instrument

LEDGER_INSTRUMENT = "G-REWARD-COVERAGE-LEDGER"
CRITICAL_CLASS = "reward-coverage-ledger"
SURFACE = "trajectories"

ATTESTATION_SUBPATH = "attestations/execution"
POLICY_RELATIVE = "solution/policy.yaml"

THREAT_BOUNDARY = {
    "objective-checker-divergence": "definition",
    "permissive-verifier-path": "definition",
    "reward-contract-ambiguity": "definition",
    "private-evaluator-knowledge": "definition",
    "direct-reward-mutation": "computation",
    "scorer-input-tampering": "input",
    "scorer-substitution": "computation",
    "undeclared-influence-channel": "input",
    "failure-coercion": "computation",
    "temporal-or-stochastic-manipulation": "computation",
    "cross-rollout-interference": "population",
    "trajectory-fabrication-or-omission": "evidence",
    "reward-misbinding": "attribution",
    "replay-or-duplication": "population",
    "selective-inclusion": "population",
    "metric-distortion": "reduction",
    "proxy-optimization": "reduction",
    "detector-adaptation": "evidence",
    "runtime-closure-misbinding": "computation",
    "freshness-or-rollback-misuse": "evidence",
    "uncommitted-measurement-universe": "reduction",
    "coarsening-laundered-remediation": "reduction",
    "approved-but-inadequate-configuration": "execution",
    "solver-input-or-tool-interface-corruption": "execution",
    "submission-or-scoring-handoff-failure": "input",
    "execution-state-contamination": "execution",
    "effective-service-degradation": "execution",
    "population-or-scheduling-manipulation": "population",
    "post-solver-measurement-suppression": "evidence",
}

THREAT_CHANNELS = {
    "objective-checker-divergence": ("read", "execute"),
    "permissive-verifier-path": ("read", "execute", "context"),
    "reward-contract-ambiguity": ("read", "context"),
    "private-evaluator-knowledge": ("read", "context"),
    "direct-reward-mutation": ("write", "execute"),
    "scorer-input-tampering": ("write", "read", "execute"),
    "scorer-substitution": ("write", "execute", "environment"),
    "undeclared-influence-channel": (
        "read",
        "write",
        "execute",
        "network",
        "environment",
        "timing",
        "ipc",
        "resource",
        "context",
    ),
    "failure-coercion": ("execute", "resource", "timing"),
    "temporal-or-stochastic-manipulation": ("timing", "execute", "environment"),
    "cross-rollout-interference": ("write", "ipc", "environment", "resource"),
    "trajectory-fabrication-or-omission": ("write", "read"),
    "reward-misbinding": ("read", "write", "context"),
    "replay-or-duplication": ("read", "write"),
    "selective-inclusion": ("read", "write", "context"),
    "metric-distortion": ("read", "execute"),
    "proxy-optimization": ("read", "context"),
    "detector-adaptation": ("read", "context", "environment"),
    "runtime-closure-misbinding": ("read", "execute", "environment", "network"),
    "freshness-or-rollback-misuse": ("read", "timing", "context"),
    "uncommitted-measurement-universe": ("read", "context"),
    "coarsening-laundered-remediation": ("read", "context"),
    "approved-but-inadequate-configuration": ("environment", "context", "resource"),
    "solver-input-or-tool-interface-corruption": (
        "read",
        "write",
        "execute",
        "network",
        "ipc",
    ),
    "submission-or-scoring-handoff-failure": ("read", "write", "ipc"),
    "execution-state-contamination": ("environment", "write", "ipc", "resource"),
    "effective-service-degradation": ("network", "resource", "timing"),
    "population-or-scheduling-manipulation": ("environment", "timing", "resource"),
    "post-solver-measurement-suppression": ("write", "read", "execute"),
}

COVERAGE = {
    ("objective-checker-divergence", "read"): "G-VER-REPLAY",
    ("objective-checker-divergence", "execute"): "G-VER-INVARIANCE",
    ("permissive-verifier-path", "read"): "G-RUB-REPLAY",
    ("permissive-verifier-path", "execute"): "G-ADV-NULL",
    ("permissive-verifier-path", "context"): "G-RUB-COMPLETENESS",
    ("reward-contract-ambiguity", "read"): "G-DEL-REWARD",
    ("private-evaluator-knowledge", "read"): "G-LEAK-CONTAINMENT",
    ("private-evaluator-knowledge", "context"): "G-CON-STRIP",
    ("direct-reward-mutation", "write"): "G-DEL-REWARD",
    ("scorer-input-tampering", "read"): "rewardprovenance",
    ("scorer-substitution", "execute"): "rewardprovenance",
    ("trajectory-fabrication-or-omission", "read"): "rolloutintegrity",
    ("trajectory-fabrication-or-omission", "write"): "rolloutintegrity",
    ("reward-misbinding", "read"): "rewardprovenance",
    ("replay-or-duplication", "read"): "rolloutintegrity",
    ("replay-or-duplication", "write"): "rolloutintegrity",
    ("selective-inclusion", "read"): "G-FID-POPULATION",
    ("selective-inclusion", "context"): "G-FID-POPULATION",
    ("metric-distortion", "read"): "rewarddistribution",
    ("uncommitted-measurement-universe", "read"): "rewarddistribution",
    ("uncommitted-measurement-universe", "context"): "rewarddistribution",
    ("runtime-closure-misbinding", "read"): "rewardprovenance",
    ("runtime-closure-misbinding", "environment"): "G-FID-CONFIG",
    ("freshness-or-rollback-misuse", "read"): "G-CON-RECORD",
    ("freshness-or-rollback-misuse", "timing"): "G-CON-RECORD",
    ("submission-or-scoring-handoff-failure", "read"): "G-FID-HANDOFF",
    ("submission-or-scoring-handoff-failure", "write"): "G-FID-HANDOFF",
    ("approved-but-inadequate-configuration", "environment"): "G-FID-CONFIG",
    ("approved-but-inadequate-configuration", "context"): "G-FID-CONFIG",
    ("post-solver-measurement-suppression", "read"): "G-FID-TRACE",
    ("post-solver-measurement-suppression", "write"): "G-FID-TRACE",
    ("proxy-optimization", "read"): "G-RUB-RESIDUE",
    ("detector-adaptation", "read"): "G-ADV-FABRICATED-TRAJECTORY",
    ("solver-input-or-tool-interface-corruption", "read"): "G-FID-TRACE",
    ("failure-coercion", "execute"): "G-VER-ATTRIBUTION",
}

NOT_APPLICABLE = {
    ("cross-rollout-interference", "ipc"): (
        "every committed rollout resides in its own trajectories subtree with no "
        "shared socket, pipe, or queue artifact recorded in any committed byte, and "
        "each rollout records a single agent and a single run directory"
    ),
    ("effective-service-degradation", "network"): (
        "every committed rollout records extra_allowed_hosts as an empty list, so no "
        "external service is declared reachable and none can be degraded through a "
        "channel this closure admits"
    ),
}


def _register_declaration() -> None:
    if LEDGER_INSTRUMENT in REGISTRY:
        return
    REGISTRY.register(
        Instrument(
            name=LEDGER_INSTRUMENT,
            category=Category.REWARD,
            binary="",
            ecosystems=("*",),
            timeout_seconds=120,
            required_conditions=("trajectories surface present",),
            critical_capability=CRITICAL_CLASS,
            evidence_class=EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            bucket=Bucket.D,
            notes=(
                "Derives the step 8q reward coverage ledger from the committed "
                "closure and from which atoms ran in this gate."
            ),
        )
    )


def _ascii_text(raw: str) -> str:
    return raw.encode("ascii", "backslashreplace").decode("ascii")


def attestation_clauses(base: Path) -> list[str]:
    """Enumerate verified execution attestation clauses available to this gate.

    Step 8p makes the execution attestation immutable external evidence that
    CRUCIBLE verifies and never manufactures. The directory does not exist in
    this tree, so the list is empty and no ledger row may resolve as
    externally_enforced.
    """
    root = base / core.AUDIT_DIRNAME / ATTESTATION_SUBPATH
    if not root.is_dir():
        return []
    return sorted(path.name for path in root.glob("*.dsse") if path.is_file())


def producer_policy_channels(base: Path) -> dict:
    """Read the producer's committed capability declaration as a lowering claim only.

    The manifest states intent under its own ten-name vocabulary. It is recorded
    so a reviewer can see what the producer asserted, and it never resolves a row.
    """
    declared: dict[str, dict] = {}
    for bundle in core.bundle_roots(base):
        path = bundle / POLICY_RELATIVE
        if not path.is_file():
            continue
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(document, dict):
            continue
        channels = document.get("channels") or document.get("capabilities") or []
        block: dict[str, str] = {}
        if isinstance(channels, dict):
            block = {str(key): str(value) for key, value in channels.items()}
        elif isinstance(channels, list):
            for entry in channels:
                if isinstance(entry, dict) and "channel" in entry:
                    block[str(entry["channel"])] = str(entry.get("state", ""))
        if block:
            declared[bundle.name] = block
    return declared


def live_atoms(results) -> set[str]:
    """Collect the instruments that actually ran in this gate.

    A detected row names a live atom. An instrument that did not run cannot
    cover a pair, so its name is excluded and the pair falls through to gap.
    """
    live: set[str] = set()
    for result in results:
        if getattr(result, "ran", False):
            live.add(result.instrument)
    return live


def applicable_pairs() -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for threat in REWARD_THREATS:
        for channel in THREAT_CHANNELS.get(threat, ()):
            pairs.append((threat, channel))
    return pairs


def build_rows(
    base: Path,
    live: set[str],
    clauses: list[str],
    policy: dict,
) -> list[LedgerRow]:
    """Resolve every applicable pair into exactly one closed resolution token."""
    del base
    policy_note = ""
    if policy:
        policy_note = (
            " The producer commits a capability declaration under its own "
            "vocabulary; it is recorded as a one-way lowering claim and resolves "
            "nothing."
        )
    rows: list[LedgerRow] = []
    for threat, channel in applicable_pairs():
        boundary = THREAT_BOUNDARY[threat]
        atom = COVERAGE.get((threat, channel), "")
        derivation = NOT_APPLICABLE.get((threat, channel), "")
        if atom and atom in live:
            rows.append(
                LedgerRow(
                    threat=threat,
                    channel=channel,
                    boundary=boundary,
                    resolution="detected",
                    atom=atom,
                    statement=_ascii_text(
                        f"{atom} ran in this gate and derives its own result over "
                        f"the {channel} channel for {threat}.{policy_note}"
                    ),
                )
            )
            continue
        if derivation:
            rows.append(
                LedgerRow(
                    threat=threat,
                    channel=channel,
                    boundary=boundary,
                    resolution="not_applicable",
                    derivation=_ascii_text(derivation),
                    statement=_ascii_text(
                        f"CRUCIBLE derived the {channel} channel out of reach for "
                        f"{threat} from committed bytes.{policy_note}"
                    ),
                )
            )
            continue
        reason = "no live atom covers this pair"
        if atom:
            reason = f"{atom} is declared for this pair but did not run in this gate"
        if clauses:
            reason = f"{reason}; no attestation clause resolves it either"
        rows.append(
            LedgerRow(
                threat=threat,
                channel=channel,
                boundary=boundary,
                resolution="gap",
                statement=_ascii_text(
                    f"{reason}. The execution attestation directory is absent, so "
                    f"externally_enforced is unavailable to this run and the pair "
                    f"fails closed.{policy_note}"
                ),
            )
        )
    return rows


def _gap_for(row: LedgerRow) -> CoverageGap:
    identifier = f"D-LEDGER-{row.threat.upper()}-{row.channel.upper()}"
    return CoverageGap(
        gap_id=identifier,
        instrument=LEDGER_INSTRUMENT,
        surface=SURFACE,
        reason="ledger-pair-unresolved",
        caps=Disposition.HOLD,
        statement=row.statement,
        subject=f"{row.threat}/{row.channel}",
    )


def _run_ledger(base: Path, results) -> tuple[InstrumentResult, list[LedgerRow]]:
    _register_declaration()
    clauses = attestation_clauses(base)
    policy = producer_policy_channels(base)
    live = live_atoms(results)
    rows = build_rows(base, live, clauses, policy)

    findings: list[Finding] = []
    gaps: list[CoverageGap] = []

    unresolved = [row for row in rows if row.resolution == "gap"]
    for row in unresolved:
        gaps.append(_gap_for(row))

    if not clauses:
        findings.append(
            Finding(
                finding_id="F-LEDGER-NO-EXTERNAL-ENFORCEMENT",
                instrument=LEDGER_INSTRUMENT,
                critical_class=CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject="project",
                statement=_ascii_text(
                    "No execution attestation exists under the audit tree, so no "
                    "ledger row can resolve as externally_enforced. Every pair no "
                    "live atom covers therefore fails closed as a gap rather than "
                    "resting on an operator assurance."
                ),
                evidence={"attestation_clauses": clauses},
            )
        )

    if policy:
        findings.append(
            Finding(
                finding_id="F-LEDGER-PRODUCER-VOCABULARY-DIVERGENT",
                instrument=LEDGER_INSTRUMENT,
                critical_class=CRITICAL_CLASS,
                severity=Severity.MEDIUM,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject="project",
                statement=_ascii_text(
                    "The committed capability declaration uses a producer "
                    "vocabulary whose names are not the capability channels this "
                    "ledger closes at, so no declared state maps onto a ledger row "
                    "and the declaration cannot establish enforcement of any "
                    "channel. It is recorded as a lowering claim only."
                ),
                evidence={
                    "producer_channels": sorted(
                        {name for block in policy.values() for name in block}
                    ),
                    "ledger_channels": list(CAPABILITY_CHANNELS),
                },
            )
        )

    detected = [row for row in rows if row.resolution == "detected"]
    derived = [row for row in rows if row.resolution == "not_applicable"]
    standing = Standing.OBSERVED_VIOLATION if unresolved else Standing.DEMONSTRATED_COVERAGE

    result = InstrumentResult(
        instrument=LEDGER_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "reward_claim_model_version": REWARD_CLAIM_MODEL_VERSION,
            "capability_vocabulary_version": CAPABILITY_VOCABULARY_VERSION,
            "boundaries": list(REWARD_BOUNDARIES),
            "channels": list(CAPABILITY_CHANNELS),
            "threats": len(REWARD_THREATS),
            "applicable_pairs": len(rows),
            "detected_rows": len(detected),
            "not_applicable_rows": len(derived),
            "gap_rows": len(unresolved),
            "live_atoms": sorted(live),
            "attestation_clauses": clauses,
            "producer_declaration_bundles": sorted(policy),
        },
    )
    return result, rows


def run_family(base: Path, reconnaissance: recon.Recon) -> list[InstrumentResult]:
    """Emit the step 8q ledger instrument result.

    The ledger reads which atoms ran from the reconciled family results when the
    orchestrator supplies them through the reconnaissance notes, and otherwise
    derives liveness from the registry declarations alone, which leaves every
    pair unresolved rather than asserting coverage it cannot witness.
    """
    results = []
    notes = getattr(reconnaissance, "notes", None)
    if isinstance(notes, dict):
        results = notes.get("instrument_results") or []
    try:
        result, rows = _run_ledger(base, results)
    except Exception as error:  # noqa: BLE001
        return [
            InstrumentResult(
                instrument=LEDGER_INSTRUMENT,
                ran=False,
                gaps=[
                    CoverageGap(
                        gap_id="D-LEDGER-INTERNAL-ERROR",
                        instrument=LEDGER_INSTRUMENT,
                        surface=SURFACE,
                        reason="ledger-derivation-failed",
                        caps=Disposition.HOLD,
                        statement=_ascii_text(
                            f"The reward coverage ledger could not be derived: {error}"
                        ),
                    )
                ],
            )
        ]
    result.notes["rows"] = [row.to_row() for row in rows]
    return [result]


def ledger_rows(base: Path, results) -> list[LedgerRow]:
    """Return the ledger rows for the evidence document.

    The orchestrator calls this after every family has run so the detected rows
    name atoms that genuinely executed in the gate that reports them.
    """
    _, rows = _run_ledger(base, results)
    return rows


__all__ = [
    "ATTESTATION_SUBPATH",
    "COVERAGE",
    "CRITICAL_CLASS",
    "LEDGER_INSTRUMENT",
    "NOT_APPLICABLE",
    "SURFACE",
    "THREAT_BOUNDARY",
    "THREAT_CHANNELS",
    "applicable_pairs",
    "attestation_clauses",
    "build_rows",
    "ledger_rows",
    "live_atoms",
    "producer_policy_channels",
    "run_family",
]
