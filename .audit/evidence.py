"""Emitter for .audit/evidence.yaml, the sole citable evidence source.

Phase 1 item 9 makes this file the only evidence source a downstream reviewer or
model may cite, and Phase 2 item 6 forbids the reviewing model from citing raw
files, guesses, or live code outside it. Every instrument therefore routes its
result through this module rather than writing YAML itself, so the schema stays
single-sourced and no instrument can quietly invent a field.

House rules keep this file emoji-free; flags belong to Markdown alone. The
document is written with sorted keys and block style so a byte diff between two
runs is readable and so the file's own digest is stable under reordering inside
the producing code.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from core import (
    EVIDENCE_FILENAME,
    CoverageGap,
    Disposition,
    Finding,
    InstrumentResult,
    audit_root,
    canonical_digest,
    cap_all,
)
from normalize import NormalizedIssue, identity_multiset

EVIDENCE_SCHEMA = "crucible.evidence/v1"
REWARD_CLAIM_MODEL_VERSION = 2
CAPABILITY_VOCABULARY_VERSION = 2

REWARD_BOUNDARIES = (
    "definition",
    "input",
    "computation",
    "attribution",
    "population",
    "reduction",
    "evidence",
    "execution",
)

CAPABILITY_CHANNELS = (
    "read",
    "write",
    "execute",
    "network",
    "environment",
    "timing",
    "ipc",
    "resource",
    "context",
)

REWARD_THREATS = (
    "objective-checker-divergence",
    "permissive-verifier-path",
    "reward-contract-ambiguity",
    "private-evaluator-knowledge",
    "direct-reward-mutation",
    "scorer-input-tampering",
    "scorer-substitution",
    "undeclared-influence-channel",
    "failure-coercion",
    "temporal-or-stochastic-manipulation",
    "cross-rollout-interference",
    "trajectory-fabrication-or-omission",
    "reward-misbinding",
    "replay-or-duplication",
    "selective-inclusion",
    "metric-distortion",
    "proxy-optimization",
    "detector-adaptation",
    "runtime-closure-misbinding",
    "freshness-or-rollback-misuse",
    "uncommitted-measurement-universe",
    "coarsening-laundered-remediation",
    "approved-but-inadequate-configuration",
    "solver-input-or-tool-interface-corruption",
    "submission-or-scoring-handoff-failure",
    "execution-state-contamination",
    "effective-service-degradation",
    "population-or-scheduling-manipulation",
    "post-solver-measurement-suppression",
)

LEDGER_RESOLUTIONS = ("detected", "externally_enforced", "not_applicable", "gap")


@dataclass(frozen=True)
class LedgerRow:
    """One (threat, capability channel) pair of the step 8q reward coverage ledger.

    not_applicable is derived by CRUCIBLE from the committed closure and is never
    accepted as a producer declaration, so the derivation field is mandatory for
    that resolution and the constructor refuses it when absent.
    """

    threat: str
    channel: str
    boundary: str
    resolution: str
    atom: str = ""
    attestation_clause: str = ""
    derivation: str = ""
    statement: str = ""

    def __post_init__(self) -> None:
        if self.threat not in REWARD_THREATS:
            raise ValueError(f"threat outside closed vocabulary: {self.threat}")
        if self.channel not in CAPABILITY_CHANNELS:
            raise ValueError(f"channel outside closed vocabulary: {self.channel}")
        if self.boundary not in REWARD_BOUNDARIES:
            raise ValueError(f"boundary outside closed vocabulary: {self.boundary}")
        if self.resolution not in LEDGER_RESOLUTIONS:
            raise ValueError(f"resolution outside closed vocabulary: {self.resolution}")
        if self.resolution == "detected" and not self.atom:
            raise ValueError("a detected row must name the live atom")
        if self.resolution == "externally_enforced" and not self.attestation_clause:
            raise ValueError("an externally_enforced row must name the verified clause")
        if self.resolution == "not_applicable" and not self.derivation:
            raise ValueError("a not_applicable row must carry its CRUCIBLE derivation")

    def to_row(self) -> dict:
        return {
            "threat": self.threat,
            "channel": self.channel,
            "boundary": self.boundary,
            "resolution": self.resolution,
            "atom": self.atom,
            "attestation_clause": self.attestation_clause,
            "derivation": self.derivation,
            "statement": self.statement,
        }


@dataclass
class EvidenceDocument:
    """The accumulating evidence record for one CRUCIBLE run."""

    run_id: str
    principal: str
    scope_digest: str
    recon: dict = field(default_factory=dict)
    instruments: list[InstrumentResult] = field(default_factory=list)
    issues: list[NormalizedIssue] = field(default_factory=list)
    ledger: list[LedgerRow] = field(default_factory=list)
    notes: dict = field(default_factory=dict)

    def add(self, result: InstrumentResult) -> None:
        self.instruments.append(result)

    def extend(self, results: Iterable[InstrumentResult]) -> None:
        self.instruments.extend(results)

    @property
    def findings(self) -> list[Finding]:
        return [f for result in self.instruments for f in result.findings]

    @property
    def gaps(self) -> list[CoverageGap]:
        return [g for result in self.instruments for g in result.gaps]

    @property
    def disposition(self) -> Disposition:
        return cap_all(result.disposition for result in self.instruments)

    def ledger_unresolved(self) -> list[LedgerRow]:
        return [row for row in self.ledger if row.resolution == "gap"]

    def to_document(self) -> dict:
        findings = sorted(self.findings, key=lambda f: (f.critical_class, f.finding_id))
        gaps = sorted(self.gaps, key=lambda g: g.gap_id)
        return {
            "schema": EVIDENCE_SCHEMA,
            "run_id": self.run_id,
            "principal": self.principal,
            "generated_at": _utc_now(),
            "scope_digest": self.scope_digest,
            "disposition": self.disposition.token,
            "recon": self.recon,
            "instruments": [result.to_row() for result in self.instruments],
            "findings": [f.to_row() for f in findings],
            "coverage_gaps": [g.to_row() for g in gaps],
            "normalized_issues": [issue.to_row() for issue in self.issues],
            "issue_identity_multiset": identity_multiset(self.issues),
            "reward_coverage_ledger": {
                "reward_claim_model_version": REWARD_CLAIM_MODEL_VERSION,
                "capability_vocabulary_version": CAPABILITY_VOCABULARY_VERSION,
                "rows": [row.to_row() for row in self.ledger],
                "unresolved_rows": len(self.ledger_unresolved()),
            },
            "notes": self.notes,
        }

    def content_digest(self) -> str:
        document = self.to_document()
        document.pop("generated_at", None)
        return canonical_digest(document)

    def write(self, path: Path | None = None) -> Path:
        target = path or (audit_root() / EVIDENCE_FILENAME)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = self.to_document()
        payload["content_digest"] = self.content_digest()
        target.write_text(dump_yaml(payload), encoding="utf-8")
        return target


def dump_yaml(payload: Mapping) -> str:
    return yaml.safe_dump(
        dict(payload),
        sort_keys=True,
        default_flow_style=False,
        allow_unicode=False,
        width=100,
    )


def load_evidence(path: Path | None = None) -> dict:
    target = path or (audit_root() / EVIDENCE_FILENAME)
    return yaml.safe_load(target.read_text(encoding="utf-8")) or {}


def append_rows(path: Path, rows: Sequence[Mapping], schema: str) -> Path:
    """Append per-task rows to a private side ledger such as budget.yaml or fidelity.yaml.

    Steps 8s and 8u require those two files to accumulate per-task outcomes and
    require fidelity.yaml to be stripped from every projection by name, so they
    are kept out of evidence.yaml rather than merged into it.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if path.exists():
        existing = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    current = list(existing.get("rows", []))
    current.extend(dict(row) for row in rows)
    document = {"schema": schema, "rows": current}
    path.write_text(dump_yaml(document), encoding="utf-8")
    return path


def _utc_now() -> str:
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()
