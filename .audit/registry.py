"""Instrument registry under the Phase 1 item 4 twelve-field declaration schema.

Every tool CRUCIBLE runs declares its name, category, binary, argv builder,
ecosystems, timeout, required conditions, critical capability, evidence class,
parser requirement, raw-artifact requirement, and disposition cap on absence.
Declaring those in one table rather than inside each call site is what lets the
gate answer, from data alone, what a missing binary costs and whether a clean
result was even capable of being unclean.

All grounding instruments are pure Bucket D. They may only lower or cap a
disposition and never raise one, so no field here can express a promotion and
the cap on absence is constrained to HOLD or BLOCK at construction.
"""

from __future__ import annotations

import enum
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from core import Bucket, Disposition


class Category(enum.Enum):
    SCANNER = "scanner"
    LEAK_GATE = "leak-gate"
    PROVENANCE = "provenance"
    DELIVERY = "delivery"
    VERIFIER_ROBUSTNESS = "verifier-robustness"
    RUBRIC = "rubric"
    CONTAMINATION = "contamination"
    REWARD = "reward"
    ADVERSARY = "adversary"
    FIDELITY = "fidelity"
    REFERENCE = "reference"
    CALIBRATION = "calibration"
    BUDGET = "budget"
    LINEAGE = "lineage"
    ATTESTATION = "attestation"
    RECON = "recon"


class EvidenceClass(enum.Enum):
    """What kind of claim an instrument's output is allowed to support."""

    RAW_TOOL_OUTPUT = "raw-tool-output"
    RECOMPUTED_DIGEST = "recomputed-digest"
    SET_RELATION = "set-relation"
    SCHEMA_VALIDATION = "schema-validation"
    EXECUTION_REPLAY = "execution-replay"
    EXTERNAL_ATTESTATION = "external-attestation"


ArgvBuilder = Callable[..., list[str]]


@dataclass(frozen=True)
class Instrument:
    """One registered instrument declaration.

    disposition_cap_on_absence is the contract's load-bearing field: it records
    what the gate resolves to when the instrument cannot run at all, so an
    unavailable tool never silently reads as a clean result.
    """

    name: str
    category: Category
    binary: str
    ecosystems: tuple[str, ...]
    timeout_seconds: float
    required_conditions: tuple[str, ...]
    critical_capability: str
    evidence_class: EvidenceClass
    requires_parser: bool
    requires_raw_artifact: bool
    disposition_cap_on_absence: Disposition
    bucket: Bucket = Bucket.D
    argv_builder: ArgvBuilder | None = None
    database_pin: str = ""
    notes: str = ""
    fixture_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.disposition_cap_on_absence is Disposition.SHIP:
            raise ValueError(f"{self.name}: absence of a required instrument can never cap at SHIP")
        if self.bucket is not Bucket.D:
            raise ValueError(f"{self.name}: registered instruments are pure Bucket D")
        if self.requires_parser and not self.requires_raw_artifact:
            raise ValueError(
                f"{self.name}: a parsed instrument must retain its raw artifact for re-derivation"
            )

    def build_argv(self, **kwargs) -> list[str]:
        if self.argv_builder is None:
            raise ValueError(f"{self.name}: no argv builder declared")
        return self.argv_builder(**kwargs)

    def to_row(self) -> dict:
        return {
            "name": self.name,
            "category": self.category.value,
            "binary": self.binary,
            "ecosystems": list(self.ecosystems),
            "timeout_seconds": self.timeout_seconds,
            "required_conditions": list(self.required_conditions),
            "critical_capability": self.critical_capability,
            "evidence_class": self.evidence_class.value,
            "requires_parser": self.requires_parser,
            "requires_raw_artifact": self.requires_raw_artifact,
            "disposition_cap_on_absence": self.disposition_cap_on_absence.token,
            "bucket": self.bucket.value,
            "database_pin": self.database_pin,
            "notes": self.notes,
            "fixture_ids": list(self.fixture_ids),
        }


class Registry:
    """The single mutable table of registered instruments for a run."""

    def __init__(self) -> None:
        self._table: dict[str, Instrument] = {}

    def register(self, instrument: Instrument) -> Instrument:
        if instrument.name in self._table:
            raise ValueError(f"duplicate instrument registration: {instrument.name}")
        self._table[instrument.name] = instrument
        return instrument

    def get(self, name: str) -> Instrument:
        return self._table[name]

    def names(self) -> list[str]:
        return sorted(self._table)

    def by_category(self, category: Category) -> list[Instrument]:
        return [
            self._table[name] for name in self.names() if self._table[name].category is category
        ]

    def for_ecosystem(self, ecosystem: str) -> list[Instrument]:
        return [
            self._table[name]
            for name in self.names()
            if ecosystem in self._table[name].ecosystems or "*" in self._table[name].ecosystems
        ]

    def missing(self, available: Sequence[str]) -> list[Instrument]:
        present = set(available)
        return [
            self._table[name] for name in self.names() if self._table[name].binary not in present
        ]

    def to_rows(self) -> list[dict]:
        return [self._table[name].to_row() for name in self.names()]

    def __len__(self) -> int:
        return len(self._table)

    def __contains__(self, name: object) -> bool:
        return name in self._table


REGISTRY = Registry()
