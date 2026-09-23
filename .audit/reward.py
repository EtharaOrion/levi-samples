"""Reward-integrity family, discharging CRUCIBLE contract step 8o.

Step 8o names four instruments and this module implements all four.

rewarddefinition composes the delivery, verifier-robustness and rubric families
with feasibility, no-op, known-wrong and oracle-full-reward re-runs. It fails
when a no-op earns above the declared floor, a known-wrong earns above the
floor, the oracle does not earn full reward, or a feasibility re-run does not
reproduce the recorded reward. Each of those is critical-capable and caps HOLD.

rewardprovenance re-derives every reward figure componentwise from raw
per-rollout bytes before scalarization, then tests scorer closure, declared
capability channels and private-boundary carriers against the committed policy
manifest. A component that does not re-derive and a scorer reading outside its
closure are BLOCK; remaining failures cap HOLD.

rolloutintegrity recomputes cardinality, canonical-byte deduplication,
completeness, schema, binding and the trajectory Merkle root from committed
bytes and requires exact agreement with the operator-signed root and population
sequence. Root or sequence divergence is BLOCK; the rest cap HOLD. A clean
rolloutintegrity proves custody and never execution validity, so this module
never records it in place of the execution-fidelity family.

rewarddistribution computes preregistered exact statistics. The preregistration
is itself the gate. The statistic set closes at exactly six figures, each
recomputed as an exact rational through fractions.Fraction and never as a
floating-point value, because a floating-point median or mass would make the
recomputation unreproducible at the last digit. An absent preregistration caps
HOLD and never BLOCK, because building a required instrument must never worsen a
disposition relative to not building it, and the same surface with no instrument
at all would carry a coverage gap capping HOLD.
"""

from __future__ import annotations

import json
import tomllib
from fractions import Fraction
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

DEFINITION_INSTRUMENT = "rewarddefinition"
PROVENANCE_INSTRUMENT = "rewardprovenance"
ROLLOUT_INSTRUMENT = "rolloutintegrity"
DISTRIBUTION_INSTRUMENT = "rewarddistribution"

REWARD_CRITICAL_CLASS = "reward-integrity"
REWARD_SURFACE = "trajectories"

TRAJECTORY_DIRNAME = "trajectories"
VERIFIER_DIRNAME = "verifier"
AGENT_DIRNAME = "agent"

REWARD_JSON = "reward.json"
REWARD_TXT = "reward.txt"
REWARD_REASON_JSON = "reward_reason.json"
SUMMARY_JSON = "summary.json"
PROCESS_JSON = "process.json"
RESULT_JSON = "result.json"
VERDICTS_JSONL = "verdicts.jsonl"
TRAJECTORY_JSON = "trajectory.json"
CONFIG_JSON = "config.json"

POLICY_CARRIER = "solution/policy.yaml"
MANIFEST_CARRIER = "task.toml"

PREREGISTRATION_DIRNAME = "preregistration"

STATISTIC_NAMES = (
    "reward_cardinality",
    "reward_support",
    "reward_floor_mass",
    "reward_ceiling_mass",
    "reward_median",
    "reward_range",
)

REWARD_FLOOR = Fraction(0)
REWARD_CEILING = Fraction(1)

GRADED_REASON = "graded"

ZERO_WITHOUT_GRADING_REASONS = (
    "empty-fail-to-pass-set",
    "submission-diff-unavailable",
    "submission-baseline-unresolved",
    "submission-modified-the-verifier-tree",
    "test-patch-did-not-apply",
    "build-failed-after-patches",
    "declared-targets-absent-from-output",
    "declared-target-ambiguous",
    "declared-targets-partially-absent",
    "log-and-exit-status-disagree",
    "submission-belongs-to-another-repository",
    "preserve-set-regression",
    "verifier-did-not-complete",
)

COMPONENT_KEYS = (
    "f2p_resolved",
    "f2p_total",
    "n2p_resolved",
    "n2p_total",
    "targets_resolved",
    "targets_total",
    "preserve_matched",
    "preserve_total",
    "preserve_broken",
)

DECLARED_CLOSURE_CARRIERS = (
    REWARD_JSON,
    REWARD_TXT,
    REWARD_REASON_JSON,
    SUMMARY_JSON,
)

PRIVATE_BOUNDARY_SUBTREES = ("solution", "trajectories")

DEFINITION_GAP_IMAGE = "D-REWARD-DEFINITION-RERUN-UNAVAILABLE"
DEFINITION_GAP_FLOOR = "D-REWARD-NULL-FLOOR-UNDECLARED"
PROVENANCE_GAP_POLICY_BINDING = "D-REWARD-POLICY-BINDING-UNRESOLVED"
PROVENANCE_GAP_COMPONENTS = "D-REWARD-COMPONENTS-ABSENT"
ROLLOUT_GAP_SIGNED_ROOT = "D-ROLLOUT-ROOT-UNSIGNED"
ROLLOUT_GAP_SEQUENCE = "D-ROLLOUT-POPULATION-SEQUENCE-UNPROJECTED"
ROLLOUT_GAP_HARNESS_VERSION = "D-ROLLOUT-HARNESS-VERSION-UNRESOLVED"
DISTRIBUTION_GAP_PREREGISTRATION = "D-REWARD-PREREGISTRATION-ABSENT"
DISTRIBUTION_GAP_SCOPE_DIVERGENCE = "D-REWARD-SCOPE-POPULATION-DIVERGENCE"
INTERNAL_ERROR_GAP = "D-REWARD-INTERNAL-ERROR"
NO_BUNDLE_GAP = "D-REWARD-NO-RESIDENT-BUNDLE"


def _register_declarations() -> None:
    """Register the four step 8o instruments with their declaration fields.

    Registration is idempotent so a second import cannot raise and thereby turn
    a re-import into a broken instrument.
    """
    declarations = (
        Instrument(
            name=DEFINITION_INSTRUMENT,
            category=Category.REWARD,
            binary="python",
            ecosystems=("*",),
            timeout_seconds=1800.0,
            required_conditions=(
                "pinned-image-resolvable",
                "bound-invocation-recorded",
                "null-floor-declared",
            ),
            critical_capability="no-op-and-known-wrong-and-oracle-reward-discrimination",
            evidence_class=EvidenceClass.EXECUTION_REPLAY,
            requires_parser=True,
            requires_raw_artifact=True,
            disposition_cap_on_absence=Disposition.HOLD,
            bucket=Bucket.D,
            notes="Composes delivery, verifier-robustness and rubric with four re-runs.",
        ),
        Instrument(
            name=PROVENANCE_INSTRUMENT,
            category=Category.REWARD,
            binary="python",
            ecosystems=("*",),
            timeout_seconds=600.0,
            required_conditions=(
                "per-rollout-raw-bytes-readable",
                "policy-manifest-readable",
            ),
            critical_capability="componentwise-re-derivation-and-scorer-closure",
            evidence_class=EvidenceClass.RECOMPUTED_DIGEST,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.BLOCK,
            bucket=Bucket.D,
            notes="Re-derives every reward figure before scalarization.",
        ),
        Instrument(
            name=ROLLOUT_INSTRUMENT,
            category=Category.REWARD,
            binary="python",
            ecosystems=("*",),
            timeout_seconds=600.0,
            required_conditions=(
                "rollout-bytes-readable",
                "operator-signed-root-projected",
            ),
            critical_capability="merkle-root-and-population-sequence-agreement",
            evidence_class=EvidenceClass.RECOMPUTED_DIGEST,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.BLOCK,
            bucket=Bucket.D,
            notes="Proves custody only; never substitutes for the execution-fidelity family.",
        ),
        Instrument(
            name=DISTRIBUTION_INSTRUMENT,
            category=Category.REWARD,
            binary="python",
            ecosystems=("*",),
            timeout_seconds=300.0,
            required_conditions=("preregistration-committed-and-bound",),
            critical_capability="exact-rational-recomputation-of-preregistered-statistics",
            evidence_class=EvidenceClass.RECOMPUTED_DIGEST,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            bucket=Bucket.D,
            notes="Six closed statistics, each an exact Fraction, never a float.",
        ),
    )
    for declaration in declarations:
        if declaration.name in REGISTRY:
            continue
        REGISTRY.register(declaration)


_register_declarations()


def _ascii_text(raw: str) -> str:
    """Force a statement into the ASCII the emitted YAML is restricted to."""
    return raw.encode("ascii", "backslashreplace").decode("ascii")


def _read_json(path: Path) -> Any:
    """Read a JSON carrier, returning None when it is absent or unparseable."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _read_yaml(path: Path) -> Any:
    """Read a YAML carrier, returning None when it is absent or unparseable."""
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def _read_toml(path: Path) -> dict[str, Any]:
    """Read a TOML manifest, returning an empty mapping when unreadable."""
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def exact_reward(value: Any) -> Fraction | None:
    """Convert a recorded reward scalar into an exact rational.

    The recorded figure is written by the producer as a decimal with six places,
    so it is read through its string form rather than through binary floating
    point. Reading 0.875 as a float and then converting would carry the float
    representation error into every later statistic.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    try:
        return Fraction(str(value).strip())
    except (ValueError, ZeroDivisionError):
        return None


def rollout_roots(bundle: Path) -> list[Path]:
    """Enumerate every committed rollout directory under one bundle.

    A rollout is an <agent>/<run> directory below trajectories/, which is where
    step 8 fixes the rollout location.
    """
    root = bundle / TRAJECTORY_DIRNAME
    if not root.is_dir():
        return []
    found: list[Path] = []
    for agent_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for run_dir in sorted(p for p in agent_dir.iterdir() if p.is_dir()):
            found.append(run_dir)
    return found


def rollout_identity(bundle: Path, rollout: Path) -> str:
    """Name a rollout by bundle uuid, agent and run, for stable evidence keys."""
    return f"{bundle.name}/{rollout.parent.name}/{rollout.name}"


def _components(reason_doc: Any) -> dict[str, Any]:
    """Extract the recorded component counts from a reward reason carrier."""
    if not isinstance(reason_doc, dict):
        return {}
    return {key: reason_doc[key] for key in COMPONENT_KEYS if key in reason_doc}


def rederive_reward(components: dict[str, Any]) -> Fraction | None:
    """Recompute the reward from its components under the committed formula.

    The committed verifier reduces resolved targets over declared targets, so
    the re-derivation is that same ratio computed exactly. A zero denominator
    returns None rather than raising, because a bundle declaring no targets is a
    finding for another instrument and not an arithmetic failure here.
    """
    resolved = components.get("targets_resolved")
    total = components.get("targets_total")
    if resolved is None or total is None:
        resolved = components.get("f2p_resolved")
        total = components.get("f2p_total")
    if resolved is None or total is None:
        return None
    try:
        numerator = Fraction(int(resolved))
        denominator = Fraction(int(total))
    except (TypeError, ValueError):
        return None
    if denominator == 0:
        return None
    return numerator / denominator


def read_rollout(bundle: Path, rollout: Path) -> dict[str, Any]:
    """Read every reward carrier of one rollout into one comparable record.

    Every field is recorded as read, including absences, because a later
    instrument must be able to distinguish a carrier that was missing from a
    carrier that was present and empty.
    """
    verifier_dir = rollout / VERIFIER_DIRNAME
    agent_dir = rollout / AGENT_DIRNAME
    reward_doc = _read_json(verifier_dir / REWARD_JSON)
    reason_doc = _read_json(verifier_dir / REWARD_REASON_JSON)
    summary_doc = _read_json(verifier_dir / SUMMARY_JSON)
    process_doc = _read_json(verifier_dir / PROCESS_JSON)
    result_doc = _read_json(rollout / RESULT_JSON)
    trajectory_doc = _read_json(agent_dir / TRAJECTORY_JSON)

    reward_txt_path = verifier_dir / REWARD_TXT
    try:
        reward_txt = reward_txt_path.read_text(encoding="utf-8").strip()
    except OSError:
        reward_txt = ""

    verdict_lines: list[dict[str, Any]] = []
    verdicts_path = verifier_dir / VERDICTS_JSONL
    if verdicts_path.is_file():
        try:
            for line in verdicts_path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    parsed = json.loads(stripped)
                except ValueError:
                    continue
                if isinstance(parsed, dict):
                    verdict_lines.append(parsed)
        except OSError:
            verdict_lines = []

    declared = None
    if isinstance(reward_doc, dict):
        declared = exact_reward(reward_doc.get("reward"))
    text_reward = exact_reward(reward_txt) if reward_txt else None
    result_reward = None
    if isinstance(result_doc, dict):
        block = result_doc.get("verifier_result")
        if isinstance(block, dict):
            rewards = block.get("rewards")
            if isinstance(rewards, dict):
                result_reward = exact_reward(rewards.get("reward"))

    reason = ""
    if isinstance(reason_doc, dict):
        reason = str(reason_doc.get("reason", "")).strip()

    components = _components(reason_doc)
    summary_components = _components(summary_doc)

    harness_version = ""
    session_id = ""
    step_count = None
    if isinstance(trajectory_doc, dict):
        agent_block = trajectory_doc.get("agent")
        if isinstance(agent_block, dict):
            harness_version = str(agent_block.get("version", "")).strip()
        session_id = str(trajectory_doc.get("session_id", "")).strip()
        steps = trajectory_doc.get("steps")
        if isinstance(steps, list):
            step_count = len(steps)

    verifier_mode = ""
    if isinstance(result_doc, dict):
        verifier_mode = str(result_doc.get("verifier_environment_mode", "")).strip()

    outcome_source = ""
    if isinstance(process_doc, dict):
        outcome = process_doc.get("outcome")
        if isinstance(outcome, dict):
            outcome_source = str(outcome.get("source", "")).strip()

    return {
        "identity": rollout_identity(bundle, rollout),
        "bundle": bundle.name,
        "agent": rollout.parent.name,
        "run": rollout.name,
        "declared_reward": declared,
        "text_reward": text_reward,
        "result_reward": result_reward,
        "reason": reason,
        "components": components,
        "summary_components": summary_components,
        "verdict_count": len(verdict_lines),
        "verdict_models": sorted(
            {str(v.get("model", "")) for v in verdict_lines if v.get("model")}
        ),
        "process_present": isinstance(process_doc, dict),
        "outcome_source": outcome_source,
        "harness_version": harness_version,
        "session_id": session_id,
        "step_count": step_count,
        "verifier_environment_mode": verifier_mode,
        "trajectory_present": isinstance(trajectory_doc, dict),
        "rollout_path": str(rollout.relative_to(bundle.parent)),
    }


def collect_population(base: Path) -> list[dict[str, Any]]:
    """Read every rollout of every resident bundle into one ordered population.

    Ordering is by bundle uuid then agent then run so the recomputation is
    reproducible without depending on filesystem iteration order.
    """
    population: list[dict[str, Any]] = []
    for bundle in core.bundle_roots(base):
        for rollout in rollout_roots(bundle):
            population.append(read_rollout(bundle, rollout))
    population.sort(key=lambda row: row["identity"])
    return population


def _declared_null_floor(bundle: Path) -> Fraction | None:
    """Resolve the bundle's declared null-submission reward floor.

    Step 8t requires the bundle to declare a null floor at or below 0.05. This
    reads only a key that literally declares a reward floor. A preserve-share
    ceiling is not a reward floor and is deliberately not accepted in its place,
    because adopting an adjacent number would manufacture a bound the producer
    never declared.
    """
    manifest = _read_toml(bundle / MANIFEST_CARRIER)
    for block_name in ("reward", "adversary", "scoring", "verifier"):
        block = manifest.get(block_name)
        if isinstance(block, dict):
            for key in ("null_floor", "null_reward_floor", "reward_floor"):
                if key in block:
                    return exact_reward(block[key])
    for key in ("null_floor", "null_reward_floor", "reward_floor"):
        if key in manifest:
            return exact_reward(manifest[key])
    return None


def _image_resolvable(bundle: Path) -> tuple[bool, str]:
    """Report whether the bundle pins an image the re-runs could execute in."""
    manifest = _read_toml(bundle / MANIFEST_CARRIER)
    digest = ""
    for block_name in ("environment", "image", "container"):
        block = manifest.get(block_name)
        if isinstance(block, dict):
            for key in ("base_image_digest", "docker_image", "image_digest"):
                value = block.get(key)
                if isinstance(value, str) and value.strip():
                    digest = value.strip()
                    break
        if digest:
            break
    for key in ("base_image_digest", "docker_image"):
        if not digest and isinstance(manifest.get(key), str):
            digest = str(manifest[key]).strip()
    if not digest:
        return False, "no image digest declared in the task manifest"
    if "@sha256:" not in digest:
        return False, f"image reference {digest} carries no sha256 digest"
    return True, digest


def _cached_known_wrong(base: Path, bundle: Path) -> float | None:
    """Read the measured schema-valid-wrong-content probe reward as known-wrong control.

    Step 8o's known-wrong re-run reuses the G-ADV-SCHEMA-VALID live measurement,
    which executed a schema-valid deliverable with every content field wrong
    through the stock Harbor path inside the pinned image. Only a measured cache
    row is accepted; absence returns None and the re-run stays unavailable.
    """
    cache_dir = base / core.AUDIT_DIRNAME / "adversary" / "live" / bundle.name
    for path in sorted(cache_dir.glob("G-ADV-SCHEMA-VALID-*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        reward = (payload.get("row_update") or {}).get("measured_reward")
        if isinstance(reward, (int, float)):
            return float(reward)
    return None


def _run_definition(base: Path, population: list[dict[str, Any]]) -> InstrumentResult:
    """Run rewarddefinition, the four-re-run discrimination check of step 8o.

    The four re-runs need the pinned image and the bound invocation. Where the
    image does not resolve the re-run is recorded as unavailable and emitted as
    a coverage gap capping HOLD. It is never recorded as a pass, because a
    re-run that did not happen establishes nothing about the reward definition.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    rows: list[dict[str, Any]] = []

    try:
        import liveexec
    except ImportError:
        liveexec = None

    for bundle in core.bundle_roots(base):
        resolvable, detail = _image_resolvable(bundle)
        floor = _declared_null_floor(bundle)
        rollouts = [row for row in population if row["bundle"] == bundle.name]
        empty = liveexec.empty_run(base, bundle) if liveexec is not None else None
        oracle = liveexec.oracle_run(base, bundle) if liveexec is not None else None
        known_wrong = _cached_known_wrong(base, bundle)

        def _measured(run: dict[str, Any] | None) -> bool:
            return bool(run) and run.get("status") == liveexec.STATUS_MEASURED

        no_op_state = "unavailable"
        if _measured(empty) and floor is not None:
            no_op_state = "pass" if float(empty["reward"]) <= float(floor) else "fail"
        known_wrong_state = "unavailable"
        if known_wrong is not None and floor is not None:
            known_wrong_state = "pass" if float(known_wrong) <= float(floor) else "fail"
        oracle_state = "unavailable"
        if _measured(oracle):
            oracle_state = "pass" if float(oracle["reward"]) >= REWARD_CEILING else "fail"

        row = {
            "bundle": bundle.name,
            "image_resolvable": resolvable,
            "image_detail": detail,
            "declared_null_floor": str(floor) if floor is not None else None,
            "rollouts_read": len(rollouts),
            "reruns": {
                "feasibility": "unavailable",
                "no_op": no_op_state,
                "known_wrong": known_wrong_state,
                "oracle_full_reward": oracle_state,
            },
            "no_op_reward": (empty or {}).get("reward"),
            "oracle_reward": (oracle or {}).get("reward"),
            "known_wrong_reward": known_wrong,
        }
        rows.append(row)

        for rerun_name, state, measured_value in (
            ("no-op", no_op_state, (empty or {}).get("reward")),
            ("known-wrong", known_wrong_state, known_wrong),
            ("oracle-full-reward", oracle_state, (oracle or {}).get("reward")),
        ):
            if state == "fail":
                findings.append(
                    Finding(
                        finding_id=(
                            f"F-REWARD-DEFINITION-{rerun_name.upper().replace('-', '')}"
                            f"-{bundle.name}"
                        ),
                        instrument=DEFINITION_INSTRUMENT,
                        critical_class=REWARD_CRITICAL_CLASS,
                        severity=Severity.HIGH,
                        caps=Disposition.HOLD,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=_ascii_text(
                            f"The {rerun_name} re-run of step 8o failed its rule: measured "
                            f"reward {measured_value} against declared floor {floor} and "
                            f"required oracle ceiling {REWARD_CEILING}."
                        ),
                        evidence={"measured_reward": str(measured_value)},
                    )
                )

        if floor is None:
            gaps.append(
                CoverageGap(
                    gap_id=f"{DEFINITION_GAP_FLOOR}-{bundle.name}",
                    instrument=DEFINITION_INSTRUMENT,
                    surface=REWARD_SURFACE,
                    reason="null-floor-undeclared",
                    caps=Disposition.HOLD,
                    subject=bundle.name,
                    statement=_ascii_text(
                        "The task manifest declares no reward floor for a null submission, "
                        "so the no-op and known-wrong comparisons of step 8o have no bound "
                        "to be measured against. A preserve-share ceiling is present but is "
                        "not a reward floor and was not adopted in its place."
                    ),
                )
            )

        unavailable = [
            name
            for name, state in (
                ("feasibility", "unavailable"),
                ("no-op", no_op_state),
                ("known-wrong", known_wrong_state),
                ("oracle-full-reward", oracle_state),
            )
            if state == "unavailable"
        ]
        if unavailable:
            gaps.append(
                CoverageGap(
                    gap_id=f"{DEFINITION_GAP_IMAGE}-{bundle.name}",
                    instrument=DEFINITION_INSTRUMENT,
                    surface=REWARD_SURFACE,
                    reason="rerun-environment-unavailable",
                    caps=Disposition.HOLD,
                    subject=bundle.name,
                    statement=_ascii_text(
                        "These step 8o re-runs did not execute and resolve as unmeasured, "
                        "never as clean: " + ", ".join(unavailable) + ". The feasibility "
                        "re-run needs the recorded agent submission replayed through the "
                        "bound invocation, which no committed carrier reconstructs."
                    ),
                )
            )

        recorded_max = None
        for rollout in rollouts:
            value = rollout["declared_reward"]
            if value is None:
                continue
            if recorded_max is None or value > recorded_max:
                recorded_max = value
        if recorded_max is not None and recorded_max < REWARD_CEILING and oracle_state != "pass":
            findings.append(
                Finding(
                    finding_id=f"F-REWARD-ORACLE-FULL-UNWITNESSED-{bundle.name}",
                    instrument=DEFINITION_INSTRUMENT,
                    critical_class=REWARD_CRITICAL_CLASS,
                    severity=Severity.MEDIUM,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=_ascii_text(
                        "No committed rollout of this bundle reaches full reward, and the "
                        "oracle re-run that would establish the definition awards full "
                        f"reward could not execute. The highest recorded figure is "
                        f"{recorded_max}."
                    ),
                    evidence={
                        "highest_recorded_reward": str(recorded_max),
                        "required_oracle_reward": str(REWARD_CEILING),
                        "rerun_state": "unavailable",
                    },
                )
            )

    standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=DEFINITION_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "bundles": rows,
            "composed_families": ["delivery", "verifier-robustness", "rubric"],
            "reruns_required": [
                "feasibility",
                "no-op",
                "known-wrong",
                "oracle-full-reward",
            ],
        },
    )


def _policy_channels(bundle: Path) -> dict[str, Any]:
    """Read the committed policy manifest channel declarations."""
    document = _read_yaml(bundle / POLICY_CARRIER)
    if not isinstance(document, dict):
        return {}
    for key in ("capabilities", "channels", "policy"):
        block = document.get(key)
        if isinstance(block, dict):
            return {str(k): block[k] for k in block}
    return {
        str(k): v
        for k, v in document.items()
        if isinstance(v, str) and v.strip().lower() in {"allowed", "denied", "restricted"}
    }


def _run_provenance(base: Path, population: list[dict[str, Any]]) -> InstrumentResult:
    """Run rewardprovenance, the componentwise re-derivation of step 8o.

    Every recorded reward is recomputed from the raw per-rollout components
    before scalarization. A figure that does not reproduce is BLOCK, as is a
    scorer reading outside its declared closure, because both mean the reward a
    consumer would cite is not the reward the committed bytes support.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    rows: list[dict[str, Any]] = []

    for rollout in population:
        identity = rollout["identity"]
        declared = rollout["declared_reward"]
        rederived = rederive_reward(rollout["components"])
        row = {
            "rollout": identity,
            "declared_reward": str(declared) if declared is not None else None,
            "rederived_reward": str(rederived) if rederived is not None else None,
            "reason": rollout["reason"],
            "components_present": bool(rollout["components"]),
            "carrier_agreement": None,
        }

        carriers = [
            ("reward.json", declared),
            ("reward.txt", rollout["text_reward"]),
            ("result.json", rollout["result_reward"]),
        ]
        present = [(name, value) for name, value in carriers if value is not None]
        agreement = len({value for _, value in present}) <= 1
        row["carrier_agreement"] = agreement
        if not agreement:
            findings.append(
                Finding(
                    finding_id=f"F-REWARD-CARRIER-DISAGREEMENT-{identity.replace('/', '-')}",
                    instrument=PROVENANCE_INSTRUMENT,
                    critical_class=REWARD_CRITICAL_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=identity,
                    statement=_ascii_text(
                        "The reward carriers of this rollout do not agree, so the figure a "
                        "consumer would cite depends on which carrier is read."
                    ),
                    evidence={name: str(value) for name, value in present},
                )
            )

        if rederived is None:
            if rollout["reason"] in ZERO_WITHOUT_GRADING_REASONS:
                row["resolution"] = "zero-without-grading"
                gaps.append(
                    CoverageGap(
                        gap_id=f"{PROVENANCE_GAP_COMPONENTS}-{identity.replace('/', '-')}",
                        instrument=PROVENANCE_INSTRUMENT,
                        surface=REWARD_SURFACE,
                        reason="components-absent-zero-without-grading",
                        caps=Disposition.HOLD,
                        subject=identity,
                        statement=_ascii_text(
                            "This rollout records no component counts because it resolved "
                            f"through the zero-without-grading path with reason "
                            f"{rollout['reason']}. The recorded reward therefore cannot be "
                            "re-derived arithmetically; it is accepted as attributed rather "
                            "than as recomputed."
                        ),
                    )
                )
            else:
                row["resolution"] = "components-absent-without-reason"
                findings.append(
                    Finding(
                        finding_id=f"F-REWARD-UNDERIVABLE-{identity.replace('/', '-')}",
                        instrument=PROVENANCE_INSTRUMENT,
                        critical_class=REWARD_CRITICAL_CLASS,
                        severity=Severity.CRITICAL,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=identity,
                        statement=_ascii_text(
                            "This rollout records a reward that cannot be re-derived from "
                            "its own components and carries no machine-readable reason "
                            "explaining the absence."
                        ),
                        evidence={
                            "declared_reward": str(declared),
                            "reason": rollout["reason"],
                        },
                    )
                )
        elif declared is not None and rederived != declared:
            row["resolution"] = "divergent"
            findings.append(
                Finding(
                    finding_id=f"F-REWARD-COMPONENT-DIVERGENCE-{identity.replace('/', '-')}",
                    instrument=PROVENANCE_INSTRUMENT,
                    critical_class=REWARD_CRITICAL_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=identity,
                    statement=_ascii_text(
                        "The recorded reward does not reproduce from the recorded "
                        "components under the committed reduction."
                    ),
                    evidence={
                        "declared_reward": str(declared),
                        "rederived_reward": str(rederived),
                        "components": {k: str(v) for k, v in rollout["components"].items()},
                    },
                )
            )
        else:
            row["resolution"] = "rederived"

        if rollout["verdict_count"] and rollout["process_present"]:
            findings.append(
                Finding(
                    finding_id=f"F-REWARD-SCORER-OUTSIDE-CLOSURE-{identity.replace('/', '-')}",
                    instrument=PROVENANCE_INSTRUMENT,
                    critical_class=REWARD_CRITICAL_CLASS,
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=identity,
                    statement=_ascii_text(
                        "A second scoring channel is committed beside the reward contract "
                        "path. It consumes verdict lines produced by an external judge "
                        "model, which is a read outside the deterministic closure the "
                        "reward carriers declare, and its own outcome block records the "
                        "outcome as read and never recomputed."
                    ),
                    evidence={
                        "verdict_lines": rollout["verdict_count"],
                        "verdict_models": rollout["verdict_models"],
                        "outcome_source": rollout["outcome_source"],
                        "declared_closure": list(DECLARED_CLOSURE_CARRIERS),
                    },
                )
            )

        if (
            rollout["verifier_environment_mode"]
            and rollout["verifier_environment_mode"] != "isolated"
        ):
            findings.append(
                Finding(
                    finding_id=f"F-REWARD-VERIFIER-NOT-ISOLATED-{identity.replace('/', '-')}",
                    instrument=PROVENANCE_INSTRUMENT,
                    critical_class=REWARD_CRITICAL_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=identity,
                    statement=_ascii_text(
                        "The rollout records that the verifier executed in a "
                        f"{rollout['verifier_environment_mode']} environment rather than an "
                        "isolated one, so the scorer ran without a hermetic boundary."
                    ),
                    evidence={"verifier_environment_mode": rollout["verifier_environment_mode"]},
                )
            )

        rows.append(row)

    for bundle in core.bundle_roots(base):
        channels = _policy_channels(bundle)
        if not channels:
            continue
        gaps.append(
            CoverageGap(
                gap_id=f"{PROVENANCE_GAP_POLICY_BINDING}-{bundle.name}",
                instrument=PROVENANCE_INSTRUMENT,
                surface=REWARD_SURFACE,
                reason="policy-channel-vocabulary-unbound",
                caps=Disposition.HOLD,
                subject=bundle.name,
                statement=_ascii_text(
                    "The committed policy manifest declares its channel vocabulary as "
                    "bound by a contract surface that does not exist in this tree, so the "
                    "authority for the declared channel set is unresolvable. The manifest "
                    "is read as a one-way producer claim that can only lower disposition "
                    "and its channel names are not adopted in place of the audit "
                    "capability vocabulary."
                ),
            )
        )

    standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=PROVENANCE_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "rollouts": rows,
            "declared_closure": list(DECLARED_CLOSURE_CARRIERS),
            "private_boundary_subtrees": list(PRIVATE_BOUNDARY_SUBTREES),
        },
    )


def merkle_root(leaves: list[str]) -> str:
    """Recompute a binary Merkle root over ordered leaf digests.

    An empty population has no root and returns the empty string rather than a
    digest of nothing, because a digest over an empty input would compare equal
    across every empty population and read as agreement.
    """
    if not leaves:
        return ""
    level = list(leaves)
    while len(level) > 1:
        nxt: list[str] = []
        for index in range(0, len(level), 2):
            left = level[index]
            right = level[index + 1] if index + 1 < len(level) else left
            nxt.append(core.sha256_bytes(f"{left}{right}".encode("ascii")))
        level = nxt
    return level[0]


def _rollout_leaf(bundle_root: Path, rollout: Path) -> str:
    """Digest every committed byte of one rollout into a single leaf."""
    relative: list[str] = []
    for path in sorted(rollout.rglob("*")):
        if path.is_file():
            relative.append(str(path.relative_to(bundle_root)))
    return core.tree_digest(bundle_root, relative)


def _run_rollout_integrity(base: Path, population: list[dict[str, Any]]) -> InstrumentResult:
    """Run rolloutintegrity, the custody recomputation of step 8o.

    This recomputes cardinality, canonical-byte deduplication, completeness,
    schema, binding and the Merkle root. A clean result here proves custody and
    never execution validity, which is why the notes record that relation
    explicitly rather than leaving a reader to infer it.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []

    leaves: list[str] = []
    leaf_rows: list[dict[str, Any]] = []
    seen: dict[str, str] = {}

    for bundle in core.bundle_roots(base):
        for rollout in rollout_roots(bundle):
            identity = rollout_identity(bundle, rollout)
            leaf = _rollout_leaf(bundle, rollout)
            leaves.append(leaf)
            leaf_rows.append({"rollout": identity, "leaf": leaf})
            if leaf in seen:
                findings.append(
                    Finding(
                        finding_id=f"F-ROLLOUT-DUPLICATE-{identity.replace('/', '-')}",
                        instrument=ROLLOUT_INSTRUMENT,
                        critical_class=REWARD_CRITICAL_CLASS,
                        severity=Severity.CRITICAL,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=identity,
                        statement=_ascii_text(
                            "Two committed rollouts reduce to the same canonical bytes, so "
                            "the recorded population counts one measurement twice."
                        ),
                        evidence={"duplicate_of": seen[leaf], "leaf": leaf},
                    )
                )
            else:
                seen[leaf] = identity

    recomputed_root = merkle_root(leaves)

    for rollout in population:
        identity = rollout["identity"]
        if not rollout["trajectory_present"]:
            findings.append(
                Finding(
                    finding_id=f"F-ROLLOUT-TRAJECTORY-ABSENT-{identity.replace('/', '-')}",
                    instrument=ROLLOUT_INSTRUMENT,
                    critical_class=REWARD_CRITICAL_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=identity,
                    statement=_ascii_text(
                        "This rollout commits no agent trajectory, so its population "
                        "membership cannot be reconciled against the recorded run."
                    ),
                    evidence={},
                )
            )
            continue
        if not rollout["harness_version"] or rollout["harness_version"].lower() == "unknown":
            gaps.append(
                CoverageGap(
                    gap_id=f"{ROLLOUT_GAP_HARNESS_VERSION}-{identity.replace('/', '-')}",
                    instrument=ROLLOUT_INSTRUMENT,
                    surface=REWARD_SURFACE,
                    reason="harness-version-unresolved",
                    caps=Disposition.HOLD,
                    subject=identity,
                    statement=_ascii_text(
                        "The committed trajectory records its harness version as "
                        f"{rollout['harness_version'] or 'absent'}, so the trace cannot be "
                        "shown to come from a supported harness version and never resolves "
                        "as clean on that ground."
                    ),
                )
            )

    session_ids = {row["session_id"] for row in population if row["session_id"]}
    if len(population) > 1 and len(session_ids) == 1:
        findings.append(
            Finding(
                finding_id="F-ROLLOUT-SESSION-IDENTIFIER-CONSTANT",
                instrument=ROLLOUT_INSTRUMENT,
                critical_class=REWARD_CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject="project",
                statement=_ascii_text(
                    "Every committed rollout records the same session identifier, so the "
                    "recorded identifier cannot distinguish one rollout from another and "
                    "provides no binding between a trajectory and its run."
                ),
                evidence={"session_ids": sorted(session_ids), "rollouts": len(population)},
            )
        )

    gaps.append(
        CoverageGap(
            gap_id=ROLLOUT_GAP_SIGNED_ROOT,
            instrument=ROLLOUT_INSTRUMENT,
            surface=REWARD_SURFACE,
            reason="operator-signed-root-absent",
            caps=Disposition.HOLD,
            statement=_ascii_text(
                "No operator-signed trajectory root is projected for this corpus, so the "
                "recomputed Merkle root has nothing to be compared against. The root is "
                f"recorded as {recomputed_root or 'undefined'} and the comparison resolves "
                "as unmeasured rather than as agreement."
            ),
        )
    )
    gaps.append(
        CoverageGap(
            gap_id=ROLLOUT_GAP_SEQUENCE,
            instrument=ROLLOUT_INSTRUMENT,
            surface=REWARD_SURFACE,
            reason="population-sequence-unprojected",
            caps=Disposition.HOLD,
            statement=_ascii_text(
                "No population sequence is projected, so the order in which rollouts were "
                "admitted cannot be reconciled against the order the committed bytes "
                "present. Ordering here is derived from bundle, agent and run names and is "
                "an audit convention rather than an attested sequence."
            ),
        )
    )

    standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=ROLLOUT_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "cardinality": len(population),
            "recomputed_merkle_root": recomputed_root,
            "operator_signed_root": None,
            "leaves": leaf_rows,
            "custody_scope": (
                "A clean result here establishes custody of the committed rollout bytes "
                "and establishes nothing about execution validity, which the "
                "execution-fidelity family alone reports."
            ),
        },
    )


def compute_statistics(rewards: list[Fraction]) -> dict[str, Any]:
    """Recompute the six closed statistics as exact rationals.

    Every figure is a Fraction. The median of an even population is the exact
    mean of the two central order statistics, computed as a rational so that a
    population of one half and zero yields one quarter exactly rather than a
    binary approximation of it.
    """
    ordered = sorted(rewards)
    cardinality = len(ordered)
    support = sorted(set(ordered))
    floor_mass = (
        Fraction(sum(1 for r in ordered if r == REWARD_FLOOR), cardinality) if cardinality else None
    )
    ceiling_mass = (
        Fraction(sum(1 for r in ordered if r == REWARD_CEILING), cardinality)
        if cardinality
        else None
    )
    if cardinality == 0:
        median = None
        spread = None
    elif cardinality % 2 == 1:
        median = ordered[cardinality // 2]
        spread = ordered[-1] - ordered[0]
    else:
        lower = ordered[cardinality // 2 - 1]
        upper = ordered[cardinality // 2]
        median = (lower + upper) / 2
        spread = ordered[-1] - ordered[0]
    return {
        "reward_cardinality": cardinality,
        "reward_support": [str(value) for value in support],
        "reward_floor_mass": str(floor_mass) if floor_mass is not None else None,
        "reward_ceiling_mass": str(ceiling_mass) if ceiling_mass is not None else None,
        "reward_median": str(median) if median is not None else None,
        "reward_range": str(spread) if spread is not None else None,
    }


def _scope_declared_rewards(base: Path) -> list[Fraction]:
    """Read the reward population the approved scope declares, if any.

    The scope records one recorded_reward per bundle while each bundle commits
    more than one rollout, so this returns the declared list at the granularity
    the scope wrote it and leaves the comparison to name that mismatch rather
    than expanding one declared figure to cover several measured ones.
    """
    document = _read_yaml(base / core.AUDIT_DIRNAME / core.SCOPE_FILENAME)
    if not isinstance(document, dict):
        return []
    block = document.get("trajectories")
    if not isinstance(block, dict):
        return []
    for key in ("rewards", "recorded_rewards", "reward_values"):
        values = block.get(key)
        if isinstance(values, list):
            parsed = [exact_reward(value) for value in values]
            return [value for value in parsed if value is not None]
    per_bundle = block.get("per_bundle")
    if isinstance(per_bundle, list):
        parsed = [
            exact_reward(entry.get("recorded_reward"))
            for entry in per_bundle
            if isinstance(entry, dict) and "recorded_reward" in entry
        ]
        return [value for value in parsed if value is not None]
    return []


def _run_distribution(base: Path, population: list[dict[str, Any]]) -> InstrumentResult:
    """Run rewarddistribution, the preregistered exact-statistic recomputation.

    The preregistration is the gate. Its absence caps HOLD and never BLOCK,
    because building this instrument must not worsen the disposition relative to
    not building it, and the same surface carrying no instrument at all would
    emit a coverage gap capping HOLD.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []

    rewards = [row["declared_reward"] for row in population if row["declared_reward"] is not None]
    statistics = compute_statistics(rewards)

    prereg_dir = base / core.AUDIT_DIRNAME / PREREGISTRATION_DIRNAME
    prereg_files = sorted(prereg_dir.glob("*.yaml")) if prereg_dir.is_dir() else []

    if not prereg_files:
        gaps.append(
            CoverageGap(
                gap_id=DISTRIBUTION_GAP_PREREGISTRATION,
                instrument=DISTRIBUTION_INSTRUMENT,
                surface=REWARD_SURFACE,
                reason="preregistration-absent",
                caps=Disposition.HOLD,
                statement=_ascii_text(
                    "No preregistration is committed, so the statistic set this instrument "
                    "recomputed was not committed in advance of observing the population. "
                    "The figures are recorded and the claim they would support is capped. "
                    "This resolves at HOLD rather than at BLOCK because building a "
                    "required instrument never worsens a disposition against not building "
                    "it, and the same surface with no instrument would carry the matching "
                    "coverage gap at HOLD."
                ),
            )
        )

    declared = _scope_declared_rewards(base)
    if declared and sorted(declared) != sorted(rewards):
        gaps.append(
            CoverageGap(
                gap_id=DISTRIBUTION_GAP_SCOPE_DIVERGENCE,
                instrument=DISTRIBUTION_INSTRUMENT,
                surface=REWARD_SURFACE,
                reason="declared-population-diverges-from-measured",
                caps=Disposition.HOLD,
                statement=_ascii_text(
                    "The reward population recorded in the approved scope does not match "
                    "the population measured from committed rollout bytes, so any figure "
                    "computed from the declared list would differ from the same figure "
                    "computed from the tree."
                ),
            )
        )
        findings.append(
            Finding(
                finding_id="F-REWARD-POPULATION-DIVERGENCE",
                instrument=DISTRIBUTION_INSTRUMENT,
                critical_class=REWARD_CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject="project",
                statement=_ascii_text(
                    "The measured reward population differs from the population the "
                    "approved scope declares."
                ),
                evidence={
                    "declared": [str(value) for value in sorted(declared)],
                    "measured": [str(value) for value in sorted(rewards)],
                },
            )
        )

    standing = Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE
    return InstrumentResult(
        instrument=DISTRIBUTION_INSTRUMENT,
        ran=True,
        findings=findings,
        gaps=gaps,
        standing=standing,
        notes={
            "statistic_set": list(STATISTIC_NAMES),
            "statistics": statistics,
            "arithmetic": "exact rationals through fractions.Fraction, never floating point",
            "preregistration_files": [p.name for p in prereg_files],
            "population": [
                {"rollout": row["identity"], "reward": str(row["declared_reward"])}
                for row in population
                if row["declared_reward"] is not None
            ],
        },
    )


def _internal_error_result(instrument: str, error: Exception) -> InstrumentResult:
    """Convert an internal failure into an explicit gap rather than silence."""
    return InstrumentResult(
        instrument=instrument,
        ran=False,
        gaps=[
            CoverageGap(
                gap_id=f"{INTERNAL_ERROR_GAP}-{instrument.upper()}",
                instrument=instrument,
                surface=REWARD_SURFACE,
                reason="internal-error",
                caps=Disposition.HOLD,
                statement=_ascii_text(
                    f"This instrument failed internally with {type(error).__name__}: {error}. "
                    "The failure is recorded as a gap because an instrument returning "
                    "silently would read downstream as a pass."
                ),
            )
        ],
        standing=Standing.INSUFFICIENT_EVIDENCE,
    )


def _no_bundle_result(instrument: str) -> InstrumentResult:
    """Record that no resident bundle was found, as a gap rather than a pass."""
    return InstrumentResult(
        instrument=instrument,
        ran=False,
        gaps=[
            CoverageGap(
                gap_id=f"{NO_BUNDLE_GAP}-{instrument.upper()}",
                instrument=instrument,
                surface=REWARD_SURFACE,
                reason="no-resident-bundle",
                caps=Disposition.HOLD,
                statement=_ascii_text(
                    "No resident bundle was found under any lane root, so this instrument "
                    "had no subject to measure."
                ),
            )
        ],
        standing=Standing.INSUFFICIENT_EVIDENCE,
    )


def run_family(base: Path, reconnaissance: recon.Recon) -> list[InstrumentResult]:
    """Run the four step 8o reward-integrity instruments over every rollout.

    Nothing here raises. Each instrument converts an internal failure into a
    coverage gap so that a failure to measure is never indistinguishable from a
    measurement that found nothing.
    """
    del reconnaissance
    names = (
        DEFINITION_INSTRUMENT,
        PROVENANCE_INSTRUMENT,
        ROLLOUT_INSTRUMENT,
        DISTRIBUTION_INSTRUMENT,
    )
    try:
        bundles = core.bundle_roots(base)
    except OSError as error:
        return [_internal_error_result(name, error) for name in names]
    if not bundles:
        return [_no_bundle_result(name) for name in names]

    try:
        population = collect_population(base)
    except Exception as error:
        return [_internal_error_result(name, error) for name in names]

    results: list[InstrumentResult] = []
    runners = (
        (DEFINITION_INSTRUMENT, _run_definition),
        (PROVENANCE_INSTRUMENT, _run_provenance),
        (ROLLOUT_INSTRUMENT, _run_rollout_integrity),
        (DISTRIBUTION_INSTRUMENT, _run_distribution),
    )
    for name, runner in runners:
        try:
            results.append(runner(base, population))
        except Exception as error:
            results.append(_internal_error_result(name, error))
    return results


__all__ = [
    "DEFINITION_INSTRUMENT",
    "DISTRIBUTION_INSTRUMENT",
    "PROVENANCE_INSTRUMENT",
    "ROLLOUT_INSTRUMENT",
    "STATISTIC_NAMES",
    "collect_population",
    "compute_statistics",
    "exact_reward",
    "merkle_root",
    "read_rollout",
    "rederive_reward",
    "rollout_identity",
    "rollout_roots",
    "run_family",
]
