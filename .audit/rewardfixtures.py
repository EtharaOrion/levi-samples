"""Reward fixture runner, discharging CRUCIBLE contract Phase 1 item 12d.

Item 12d keeps the reward fixtures separate from the negative-control suite and
gives them a different shape. Every reward atom carries a planted positive and a
clean fixture, which is the ordinary both-halves discipline. Every derivation
rule additionally carries a near miss: material satisfying every join predicate
the rule needs except one, which the rule must not fire on. The near miss is the
part that earns its keep, because a rule that fires on it has degenerated from a
conjunction into a correlation and would report agreement wherever the subjects
merely look similar.

The atoms run against the committed reward arithmetic rather than a restatement
of it. Re-derivation uses reward.rederive_reward, exactness uses
reward.exact_reward, the statistic set uses reward.compute_statistics, and
custody uses reward.merkle_root, so a fixture passing means the shipped function
behaved and not that a copy of it did.

Exactness is itself one of the atoms. The contract closes the statistic set at
six figures each recomputed as an exact rational, so the planted positive for
that atom is a reward whose decimal expansion is unrepresentable in binary
floating point. A harness reducing it through float would agree to within an
epsilon and disagree exactly, which is the failure the atom exists to catch.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

import core
import reward
from core import Outcome

FIXTURE_SUBPATH = "fixtures/reward/v1"
MANIFEST_NAME = "manifest.yaml"

ATOM_IDS = (
    "RA-COMPONENT-REDERIVATION",
    "RA-EXACT-RATIONAL",
    "RA-ROLLOUT-CARDINALITY",
    "RA-MERKLE-ROOT",
    "RA-ZERO-ATTRIBUTION",
)

RULE_IDS = (
    "RR-NOOP-ABOVE-FLOOR",
    "RR-KNOWN-WRONG-ABOVE-FLOOR",
    "RR-ORACLE-BELOW-FULL",
    "RR-DISTRIBUTION-DIVERGENCE",
)


def fixture_root(base: Path) -> Path:
    """Resolve the committed reward fixture tree."""
    return base / core.AUDIT_DIRNAME / FIXTURE_SUBPATH


def load_fixture(base: Path, kind: str, subject: str, half: str) -> dict[str, Any]:
    """Read one committed reward fixture, failing closed to an empty mapping."""
    path = fixture_root(base) / kind / subject / f"{half}.yaml"
    if not path.is_file():
        return {}
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return document if isinstance(document, dict) else {}


def fixture_path(kind: str, subject: str, half: str) -> str:
    """Return the repository-relative path of one reward fixture."""
    return f"{core.AUDIT_DIRNAME}/{FIXTURE_SUBPATH}/{kind}/{subject}/{half}.yaml"


def evaluate_atom(atom_id: str, fixture: dict[str, Any]) -> bool:
    """Decide whether one atom fires on the material a fixture supplies.

    Firing means the atom found the defect it exists to find. Each branch drives
    the committed reward function rather than restating its arithmetic, so a
    fixture that passes is evidence about the shipped code.
    """
    if atom_id == "RA-COMPONENT-REDERIVATION":
        components = fixture.get("components") or {}
        declared = reward.exact_reward(fixture.get("declared_reward"))
        rederived = reward.rederive_reward(components)
        if rederived is None:
            return True
        return declared != rederived

    if atom_id == "RA-EXACT-RATIONAL":
        declared = fixture.get("declared_reward")
        exact = reward.exact_reward(declared)
        if exact is None:
            return True
        expected = fixture.get("expected_rational")
        return expected is not None and exact != Fraction(str(expected))

    if atom_id == "RA-ROLLOUT-CARDINALITY":
        observed = fixture.get("observed_rollouts")
        declared = fixture.get("declared_rollouts")
        return observed != declared

    if atom_id == "RA-MERKLE-ROOT":
        leaves = [str(leaf) for leaf in (fixture.get("leaves") or [])]
        recomputed = reward.merkle_root(leaves)
        return recomputed != str(fixture.get("declared_root") or "")

    if atom_id == "RA-ZERO-ATTRIBUTION":
        rows = fixture.get("rollouts") or []
        for row in rows:
            if not isinstance(row, dict):
                return True
            value = reward.exact_reward(row.get("reward"))
            if value == Fraction(0) and not str(row.get("reason") or "").strip():
                return True
        return False

    return False


def evaluate_rule(rule_id: str, fixture: dict[str, Any]) -> bool:
    """Decide whether one derivation rule fires on the material a fixture supplies.

    Every rule is a conjunction over named join predicates. The near-miss half
    satisfies all of them but one, so a rule reducing to a correlation over the
    remainder fires there and is caught.
    """
    floor = reward.exact_reward(fixture.get("declared_floor"))
    full = reward.exact_reward(fixture.get("full_reward"))

    if rule_id == "RR-NOOP-ABOVE-FLOOR":
        if not fixture.get("probe_is_noop"):
            return False
        measured = reward.exact_reward(fixture.get("measured_reward"))
        return measured is not None and floor is not None and measured > floor

    if rule_id == "RR-KNOWN-WRONG-ABOVE-FLOOR":
        if not fixture.get("control_is_known_wrong"):
            return False
        measured = reward.exact_reward(fixture.get("measured_reward"))
        return measured is not None and floor is not None and measured > floor

    if rule_id == "RR-ORACLE-BELOW-FULL":
        if not fixture.get("submission_is_oracle"):
            return False
        measured = reward.exact_reward(fixture.get("measured_reward"))
        return measured is not None and full is not None and measured < full

    if rule_id == "RR-DISTRIBUTION-DIVERGENCE":
        if not fixture.get("population_is_complete"):
            return False
        measured = [
            value
            for value in (reward.exact_reward(raw) for raw in (fixture.get("rewards") or []))
            if value is not None
        ]
        statistics = reward.compute_statistics(measured)
        declared = fixture.get("declared_statistics") or {}
        return any(
            str(statistics.get(name)) != str(declared.get(name))
            for name in reward.STATISTIC_NAMES
            if name in declared
        )

    return False


def run_atom(base: Path, atom_id: str) -> dict[str, Any]:
    """Drive one reward atom over its clean and planted fixture halves."""
    halves: dict[str, Any] = {}
    for half in ("clean", "positive"):
        fixture = load_fixture(base, "atoms", atom_id, half)
        halves[half] = None if not fixture else evaluate_atom(atom_id, fixture)
    if halves["clean"] is None or halves["positive"] is None:
        return {
            "clean": Outcome.UNRUN,
            "positive": Outcome.UNRUN,
            "detail": f"{atom_id} has no committed fixture for both halves",
        }
    return {
        "clean": Outcome.CLEAN if not halves["clean"] else Outcome.FIRED,
        "positive": Outcome.FIRED if halves["positive"] else Outcome.CLEAN,
        "detail": (
            f"{atom_id} stayed quiet on the clean fixture and fired on the planted one"
            if not halves["clean"] and halves["positive"]
            else f"{atom_id} clean={halves['clean']} positive={halves['positive']}"
        ),
    }


def run_rule(base: Path, rule_id: str) -> dict[str, Any]:
    """Drive one derivation rule over its planted positive and its near miss.

    The near miss takes the place of the clean half. A rule that fires on
    material satisfying every join predicate but one is reporting a correlation
    rather than the conjunction it declares, which is exactly what item 12d
    requires this fixture to expose.
    """
    halves: dict[str, Any] = {}
    for half in ("near_miss", "positive"):
        fixture = load_fixture(base, "derivations", rule_id, half)
        halves[half] = None if not fixture else evaluate_rule(rule_id, fixture)
    if halves["near_miss"] is None or halves["positive"] is None:
        return {
            "clean": Outcome.UNRUN,
            "positive": Outcome.UNRUN,
            "detail": f"{rule_id} has no committed fixture for both halves",
        }
    return {
        "clean": Outcome.CLEAN if not halves["near_miss"] else Outcome.FIRED,
        "positive": Outcome.FIRED if halves["positive"] else Outcome.CLEAN,
        "detail": (
            f"{rule_id} did not fire on material satisfying every join predicate but one, "
            "and fired on the planted positive"
            if not halves["near_miss"] and halves["positive"]
            else f"{rule_id} near_miss={halves['near_miss']} positive={halves['positive']}"
        ),
    }


def run_all(base: Path) -> list[dict[str, Any]]:
    """Drive every reward atom and derivation rule, returning one row each."""
    rows: list[dict[str, Any]] = []
    for atom_id in ATOM_IDS:
        row = run_atom(base, atom_id)
        row["subject"] = atom_id
        row["kind"] = "atom"
        rows.append(row)
    for rule_id in RULE_IDS:
        row = run_rule(base, rule_id)
        row["subject"] = rule_id
        row["kind"] = "derivation"
        rows.append(row)
    return rows


def aggregate_digest(base: Path) -> str:
    """Recompute the aggregate digest the scope file binds this fixture set by.

    The digest covers every fixture path and its own digest in sorted order, so
    editing any fixture byte moves it and re-triggers the scope sign-off gate.
    """
    members: list[list[str]] = []
    for kind, subjects, halves in (
        ("atoms", ATOM_IDS, ("clean", "positive")),
        ("derivations", RULE_IDS, ("near_miss", "positive")),
    ):
        for subject in subjects:
            for half in halves:
                relative = fixture_path(kind, subject, half)
                path = base / relative
                members.append([relative, core.sha256_path(path) if path.is_file() else "absent"])
    return core.canonical_digest(sorted(members))


__all__ = [
    "ATOM_IDS",
    "FIXTURE_SUBPATH",
    "MANIFEST_NAME",
    "RULE_IDS",
    "aggregate_digest",
    "evaluate_atom",
    "evaluate_rule",
    "fixture_path",
    "fixture_root",
    "load_fixture",
    "run_all",
    "run_atom",
    "run_rule",
]
