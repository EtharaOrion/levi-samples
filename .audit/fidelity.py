"""Contract step 8u: the G-FID execution-fidelity instrument family, four instruments.

Step 8u builds these four grounding instruments in the hermetic pinned sandbox
whenever ``scope.trajectories.present`` is true. That key is true at this root,
so the family is required rather than optional and this module gates on it
explicitly. The rationale lives here rather than in the contract because the
contract is prompt-only, so the harness itself has to carry the audit evidence.

G-FID-CONFIG re-derives the harness-config binding from committed bytes and
compares it against the attested effective configuration. The binding is
``trajectories/*/run_1/config.json`` and ``lock.json``; the attestation is the
``config`` block ``result.json`` records as what actually ran. Drift or absence
caps at HOLD. A configuration that is unapproved or inadequate for the declared
horizon caps at HOLD EVEN WHEN it is pinned, signed and reproducible, which is
why approval and adequacy are evaluated as their own conditions and not folded
into the drift comparison.

G-FID-TRACE runs the registered family adapters over the committed rollout
bytes and emits a three-valued outcome per rollout across eight signal classes,
recorded as the ``fidelity_coverage`` predicate. The eight classes are defined
below and every one of them is grounded in bytes this tree actually commits,
rather than in a vocabulary borrowed from a harness this root does not hold:

``solver_identity``
    The model behind the rollout, reconciled across config.json, lock.json,
    result.json config and agent_info, verifier/process.json, and the
    trajectories directory name. A rollout whose solver cannot be named is a
    rollout whose measurement cannot be attributed.
``task_binding``
    The rollout bound to this bundle, reconciled across lock.json task name and
    digest, config.json task path, result.json task_checksum and
    process.json task_uuid. An unbound rollout is a number about some other
    task.
``horizon_conformance``
    Realized turns against the declared ``max_iterations`` and realized agent
    wall clock against the declared ``[agent].timeout_sec``. An approved
    timeout or turn cap that fired exactly as declared is CONFORMING behaviour
    and is never a violation; that is encoded directly, because a cap doing
    what it was approved to do is the system working.
``tool_channel_integrity``
    The agent's declared tool definitions and whether every agent step carries
    the tool calls the trajectory schema says it carries. A solver whose tool
    channel is not legible was not observably exposed to the task.
``context_handling``
    The token accounting in ``final_metrics`` and whether any step observation
    carries a context-limit error. A solver truncated mid-task is a solver the
    measurement made look worse than it was.
``submission_capture``
    Whether ``verifier/final.diff`` exists and is non-empty and whether
    ``artifacts/manifest.json`` records its transfer as having succeeded.
``scoring_completeness``
    Whether the verifier produced its full record set: reward.json,
    reward_reason.json, summary.json, target-stdout.md and preserve-stdout.md.
    A missing preserve log is the difference between a measured regression
    channel and an inert one.
``termination_integrity``
    Whether ``exception_info`` is null and the solver terminated through an
    explicit finish call rather than by falling off the end.

G-FID-TRACE then derives the trial status as exactly one of ``conforming``,
``nonconforming`` or ``indeterminate``, and REFUSES when the operator's own
declaration disagrees with the derived status. An observed violation in the
SUPPRESSING direction, meaning one that would lower a measured pass rate, caps
at HOLD. Insufficient evidence is a CoverageGap capping at HOLD and is never a
pass.

G-FID-POPULATION reconciles the realized groups against the precommitted roster
at the fixed group count and NEVER lowers that count to fit what arrived. Step
8u is explicit that a population that cannot be proven is BLOCK, because an
unprovable population is no measurement rather than a weak one. This module
searches for a roster and reports where it looked; if none exists it emits the
BLOCK and encodes the author-lane string ``BLOCK:INVALID_PILOT`` with no
suppression reason.

G-FID-HANDOFF verifies the identity of the final submission that reached the
scorer against the submission the solver produced, by comparing
``trajectories/*/run_1/verifier/final.diff`` against the last diff the agent
tree records in a tool observation. An unverifiable handoff caps at HOLD.

Hold reason selection is an ordered list and not a dictionary lookup, because
step 8u requires the FIRST applicable reason and an earlier match must exclude
every later one. A mapping has no order to exclude by.

Ledger and strip requirement. Each instrument appends its per-task outcome to
``.audit/fidelity.yaml``, the private grounded fidelity ledger, which step 8u
strips from every projection BY NAME and which never reaches the author.
Writing goes through ``evidence.append_rows`` so the schema stays
single-sourced. Nothing here writes outside ``.audit/``.

Control reconciliation. This family's outcome is the evidence that the sixth
mandatory core control named ``execution_fidelity`` reconciles against in the
externally governed release policy. This contract EMITS that evidence and NEVER
marks the control satisfied itself, so no row this module writes carries a
satisfied flag and no code path sets one.

Every instrument is pure Bucket D. A clean result never raises a disposition.
"""

from __future__ import annotations

import json
import re
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

import core
import evidence as evidence_mod
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

FAMILY = "G-FID"

CRITICAL_CLASS = "execution-fidelity"

CONFIG = "G-FID-CONFIG"
TRACE = "G-FID-TRACE"
POPULATION = "G-FID-POPULATION"
HANDOFF = "G-FID-HANDOFF"

CORE_CONTROL = "execution_fidelity"

FIDELITY_SCHEMA = "crucible.fidelity/v1"

CONFORMING = "conforming"
NONCONFORMING = "nonconforming"
INDETERMINATE = "indeterminate"

TRIAL_CONFORMANCE_PREDICATE = "trinity.trial-conformance/v1"
COVERAGE_PREDICATE = "fidelity_coverage"

INVALID_PILOT = "BLOCK:INVALID_PILOT"

HOLD_REASON_PRECEDENCE: tuple[str, ...] = (
    "config-unpinned",
    "config-drift",
    "config-inadequate",
    "handoff-unverified",
    "context-uncovered",
    "fidelity-unverified",
)

SIGNAL_CLASSES: tuple[str, ...] = (
    "solver_identity",
    "task_binding",
    "horizon_conformance",
    "tool_channel_integrity",
    "context_handling",
    "submission_capture",
    "scoring_completeness",
    "termination_integrity",
)

SUPPRESSING_CLASSES: frozenset[str] = frozenset(
    {
        "horizon_conformance",
        "context_handling",
        "submission_capture",
        "scoring_completeness",
    }
)

SUPPRESSING_REWARD_REASONS: frozenset[str] = frozenset(
    {
        "build-failed-after-patches",
        "declared-target-ambiguous",
        "declared-targets-absent-from-output",
        "declared-targets-partially-absent",
        "log-and-exit-status-disagree",
        "preserve-set-did-not-execute",
        "preserve-set-underexecuted",
        "runner-did-not-complete",
        "runner-exception",
        "submission-baseline-unresolved",
        "submission-belongs-to-another-repository",
        "submission-diff-unavailable",
        "test-patch-did-not-apply",
        "verifier-did-not-complete",
    }
)

REQUIRED_VERIFIER_RECORDS: tuple[str, ...] = (
    "final.diff",
    "preserve-stdout.md",
    "reward.json",
    "reward_reason.json",
    "summary.json",
    "target-stdout.md",
)

CONTEXT_LIMIT_MARKERS: tuple[str, ...] = (
    "ContextWindowExceeded",
    "context window exceeded",
    "context_length_exceeded",
    "prompt is too long",
)

CONFIG_BINDING_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("agent_name", "agent.name", "agent.name"),
    ("agent_model", "agent.model_name", "agent.model_name"),
    ("agent_kwargs", "agent.kwargs", "agent.kwargs"),
    ("agent_skills", "agent.skills", "agent.skills"),
    ("agent_mcp_servers", "agent.mcp_servers", "agent.mcp_servers"),
    ("environment_type", "environment.type", "environment.type"),
    ("environment_kwargs", "environment.kwargs", "environment.kwargs"),
    ("environment_force_build", "environment.force_build", "environment.force_build"),
    ("verifier_disable", "verifier.disable", "verifier.disable"),
    ("timeout_multiplier", "timeout_multiplier", "timeout_multiplier"),
    ("install_only", "install_only", "install_only"),
)

APPROVAL_SEARCH_PATHS: tuple[str, ...] = (
    ".audit/attestations/execution",
    ".audit/scope.yaml harness_config block",
    "trajectories/<agent>/run_1/lock.json signature fields",
    "trajectories/<agent>/run_1/config.json approval fields",
    "task.toml [agent] and [verifier] approval fields",
)

ROSTER_SEARCH_PATHS: tuple[str, ...] = (
    ".audit/scope.yaml trajectories.rollout_population",
    ".audit/scope.yaml required_instruments G-FID population_hazard",
    ".audit/scope.yaml coverage_gaps D-FID-POPULATION-UNPROVABLE",
    "<bundle>/task.toml",
    "<bundle>/trajectories/<agent>/run_1/config.json",
    "<bundle>/trajectories/<agent>/run_1/lock.json",
    "/Users/macbookpro/levi/.memory/crucible_view.yaml",
)

ROSTER_KEYS: tuple[str, ...] = (
    "precommitted_roster",
    "roster",
    "fixed_group_count",
    "group_count",
    "groups",
    "cohort_roster",
    "population_roster",
)

DIFF_HEADER = re.compile(r"^diff --git a/(?P<a>.+?) b/(?P<b>.+)$", re.MULTILINE)

WITNESS_DIFF_HEADER = re.compile(r"diff --git a/(?P<a>\S+) b/(?P<b>\S+)")


def _register() -> None:
    """Declare the four step 8u instruments under the Phase 1 item 4 schema.

    ``disposition_cap_on_absence`` is HOLD for three of the four, matching the
    scope file's ``disposition_cap_on_absence: HOLD`` for the G-FID family, and
    BLOCK for G-FID-POPULATION, because step 8u makes an unprovable population
    BLOCK and an absent population instrument would leave the single most
    consequential condition in this audit unmeasured.
    """
    common: dict[str, Any] = {
        "category": Category.FIDELITY,
        "ecosystems": ("rust", "python"),
        "bucket": Bucket.D,
        "database_pin": "committed-rollout-bytes",
        "binary": "",
        "requires_parser": False,
        "requires_raw_artifact": False,
    }
    declarations = (
        (
            CONFIG,
            300.0,
            ("committed rollout config and lock", "attested effective configuration"),
            "harness-config-binding-versus-attested-effective-configuration",
            EvidenceClass.RECOMPUTED_DIGEST,
            Disposition.HOLD,
            "Drift, absence, unapproved or inadequate configuration each cap at HOLD.",
        ),
        (
            TRACE,
            600.0,
            ("committed rollout bytes", "operator status declaration"),
            "three-valued-fidelity-coverage-across-eight-signal-classes",
            EvidenceClass.SET_RELATION,
            Disposition.HOLD,
            "Refuses when the operator declaration disagrees with the derived status.",
        ),
        (
            POPULATION,
            300.0,
            ("precommitted roster", "fixed group count"),
            "realized-groups-reconciled-at-the-fixed-group-count",
            EvidenceClass.SET_RELATION,
            Disposition.BLOCK,
            "A population that cannot be proven is BLOCK and never a lowered count.",
        ),
        (
            HANDOFF,
            300.0,
            ("committed final.diff", "agent-side final state"),
            "final-submission-identity-at-the-scorer",
            EvidenceClass.RECOMPUTED_DIGEST,
            Disposition.HOLD,
            "An unverifiable handoff caps at HOLD.",
        ),
    )
    for name, timeout, conditions, capability, evidence_class, cap_on_absence, note in declarations:
        if name in REGISTRY:
            continue
        REGISTRY.register(
            Instrument(
                name=name,
                timeout_seconds=timeout,
                required_conditions=conditions,
                critical_capability=capability,
                evidence_class=evidence_class,
                disposition_cap_on_absence=cap_on_absence,
                notes=note,
                fixture_ids=(),
                **common,
            )
        )


_register()


def select_hold_reason(conditions: set[str]) -> str:
    """Return the first applicable HOLD reason, letting an earlier match exclude later ones.

    Step 8u fixes this order exactly and requires the first match to win, so
    this is an ordered tuple scan rather than a dictionary lookup. A mapping
    would have no order for an earlier match to exclude a later one by, and the
    precedence would then depend on insertion order somewhere else.
    """
    for reason in HOLD_REASON_PRECEDENCE:
        if reason in conditions:
            return reason
    return ""


def _relative(path: Path, base: Path) -> str:
    """Render a path relative to the verification root when it sits under it."""
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def _read_json(path: Path) -> Any | None:
    """Load a committed JSON document, returning None rather than raising."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _read_text(path: Path) -> str | None:
    """Read committed bytes as text, returning None rather than raising."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _read_toml(path: Path) -> dict[str, Any]:
    """Load a committed TOML manifest, failing closed to an empty mapping."""
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def _dotted(payload: Any, path: str) -> Any:
    """Resolve a dotted key path through nested mappings, returning None when absent."""
    current = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def rollouts(bundle: Path) -> list[tuple[str, Path]]:
    """Every committed rollout of one bundle as (label, run directory)."""
    root = bundle / "trajectories"
    if not root.is_dir():
        return []
    found: list[tuple[str, Path]] = []
    for agent in sorted(root.iterdir()):
        if not agent.is_dir():
            continue
        for run in sorted(agent.iterdir()):
            if run.is_dir():
                found.append((f"{agent.name}/{run.name}", run))
    return found


def _model_parts(raw: Any) -> tuple[str, str]:
    """Split a model identity into provider and bare model under every committed spelling.

    The carriers spell one solver three ways: ``config.json`` and ``lock.json``
    write ``zai/glm-5.3``, ``process.json`` and the trajectories directory
    write ``zai__glm-5.3`` because a slash cannot appear in a path segment, and
    ``result.json`` ``agent_info.model_info`` writes the bare ``glm-5.3`` with
    the provider carried in its own null-valued field. Those are the same
    solver, so the bare model is compared always and the provider only across
    the carriers that actually state one. Folding them together instead would
    report a disagreement on every rollout and manufacture a finding out of a
    naming convention.
    """
    token = core.normalize_text(str(raw or "").replace("__", "/"))
    if not token:
        return "", ""
    provider, _, model = token.rpartition("/")
    return provider, model


def _elapsed_seconds(block: Any) -> float | None:
    """Wall clock of a started_at and finished_at pair, or None when unparseable."""
    if not isinstance(block, dict):
        return None
    started, finished = block.get("started_at"), block.get("finished_at")
    if not isinstance(started, str) or not isinstance(finished, str):
        return None
    try:
        begin = datetime.fromisoformat(started.replace("Z", "+00:00"))
        end = datetime.fromisoformat(finished.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (end - begin).total_seconds()


def _signal_solver_identity(run: Path, label: str, documents: dict[str, Any]) -> dict[str, Any]:
    """Reconcile the solver identity across every committed carrier that names it."""
    observed = {
        "config.json": _dotted(documents["config"], "agent.model_name"),
        "lock.json": _dotted(documents["lock"], "agent.model_name"),
        "result.json config": _dotted(documents["result"], "config.agent.model_name"),
        "result.json agent_info": _dotted(documents["result"], "agent_info.model_info.name"),
        "process.json": _dotted(documents["process"], "model"),
        "directory": label.split("/")[0],
    }
    present = {key: value for key, value in observed.items() if value}
    if len(present) < 2:
        return _signal(INDETERMINATE, "fewer than two carriers name a solver", observed)
    parts = {key: _model_parts(value) for key, value in present.items()}
    models = {model for _, model in parts.values()}
    providers = {provider for provider, _ in parts.values() if provider}
    if len(models) != 1:
        return _signal(NONCONFORMING, "carriers disagree on the model identity", observed)
    if len(providers) > 1:
        return _signal(NONCONFORMING, "carriers disagree on the model provider", observed)
    return _signal(CONFORMING, "every carrier names the same solver", observed)


def _signal_task_binding(bundle: Path, documents: dict[str, Any]) -> dict[str, Any]:
    """Reconcile the rollout's binding to this bundle across every carrier."""
    observed = {
        "lock task name": _dotted(documents["lock"], "task.name"),
        "process task_uuid": _dotted(documents["process"], "task_uuid"),
        "config task path": str(_dotted(documents["config"], "task.path") or "").rsplit("/", 1)[-1],
        "result task_checksum": _dotted(documents["result"], "task_checksum"),
    }
    named = [
        observed["lock task name"],
        observed["process task_uuid"],
        observed["config task path"],
    ]
    stated = [value for value in named if value]
    if not stated:
        return _signal(INDETERMINATE, "no carrier binds this rollout to a task", observed)
    if any(value != bundle.name for value in stated):
        return _signal(NONCONFORMING, "a carrier binds this rollout to another task", observed)
    if not observed["result task_checksum"]:
        return _signal(INDETERMINATE, "no task checksum is recorded", observed)
    return _signal(CONFORMING, "every carrier binds this rollout to this bundle", observed)


def _signal_horizon(bundle: Path, documents: dict[str, Any]) -> dict[str, Any]:
    """Compare realized turns and wall clock against the declared caps.

    An approved timeout or turn cap that fired exactly as declared is
    CONFORMING behaviour and is never a violation. A cap doing what it was
    approved to do is the system working, so equality resolves to conforming
    here explicitly rather than falling through to a boundary comparison that
    would read it as an overrun.
    """
    manifest = _read_toml(bundle / "task.toml")
    declared_turns = _dotted(documents["lock"], "agent.kwargs.max_iterations")
    declared_seconds = _dotted(manifest, "agent.timeout_sec")
    realized_turns = len(_dotted(documents["trajectory"], "steps") or [])
    realized_seconds = _elapsed_seconds(_dotted(documents["result"], "agent_execution"))
    observed = {
        "declared_max_iterations": declared_turns,
        "realized_steps": realized_turns,
        "declared_timeout_sec": declared_seconds,
        "realized_agent_seconds": realized_seconds,
    }
    if declared_turns is None or declared_seconds is None:
        return _signal(
            INDETERMINATE, "no declared turn cap or timeout to compare against", observed
        )
    if realized_seconds is None or not realized_turns:
        return _signal(INDETERMINATE, "no realized turn count or wall clock is recorded", observed)
    if realized_turns == int(declared_turns):
        return _signal(CONFORMING, "the declared turn cap fired exactly as declared", observed)
    if realized_turns > int(declared_turns):
        return _signal(NONCONFORMING, "realized turns exceed the declared cap", observed)
    if realized_seconds > float(declared_seconds):
        return _signal(NONCONFORMING, "realized wall clock exceeds the declared timeout", observed)
    return _signal(
        CONFORMING, "realized turns and wall clock are inside the declared caps", observed
    )


def _signal_tool_channel(documents: dict[str, Any]) -> dict[str, Any]:
    """Check that the tool channel the solver drove the task through is legible."""
    definitions = _dotted(documents["trajectory"], "agent.tool_definitions")
    steps = _dotted(documents["trajectory"], "steps") or []
    agent_steps = [
        step for step in steps if isinstance(step, dict) and step.get("source") == "agent"
    ]
    without_calls = [step.get("step_id") for step in agent_steps if "tool_calls" not in step]
    observed = {
        "tool_definitions": len(definitions) if isinstance(definitions, list) else None,
        "agent_steps": len(agent_steps),
        "agent_steps_without_tool_calls": len(without_calls),
    }
    if not isinstance(definitions, list) or not agent_steps:
        return _signal(
            INDETERMINATE, "no tool definitions or no agent steps are recorded", observed
        )
    if not definitions:
        return _signal(NONCONFORMING, "the agent declares no tool definitions", observed)
    if without_calls:
        return _signal(NONCONFORMING, "an agent step carries no tool call record", observed)
    return _signal(CONFORMING, "every agent step carries its tool call record", observed)


def _signal_context(documents: dict[str, Any]) -> dict[str, Any]:
    """Look for token accounting and for any context-limit error in the observations."""
    metrics = _dotted(documents["trajectory"], "final_metrics")
    steps = _dotted(documents["trajectory"], "steps") or []
    hits: list[Any] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        blob = _observation_text(step)
        for marker in CONTEXT_LIMIT_MARKERS:
            if marker in blob:
                hits.append({"step_id": step.get("step_id"), "marker": marker})
                break
    observed = {
        "final_metrics_present": isinstance(metrics, dict) and bool(metrics),
        "context_limit_events": hits[:5],
        "context_limit_event_count": len(hits),
    }
    if hits:
        return _signal(NONCONFORMING, "a context-limit error appears in the observations", observed)
    if not observed["final_metrics_present"]:
        return _signal(INDETERMINATE, "no token accounting is recorded for this rollout", observed)
    return _signal(
        CONFORMING, "token accounting is recorded and no context-limit error appears", observed
    )


def _signal_submission_capture(run: Path, documents: dict[str, Any]) -> dict[str, Any]:
    """Check the final submission was captured and that its declared transfer succeeded."""
    final_diff = run / "verifier" / "final.diff"
    manifest = documents["manifest"]
    statuses = {}
    if isinstance(manifest, list):
        for entry in manifest:
            if isinstance(entry, dict):
                statuses[str(entry.get("destination", "")).rsplit("/", 1)[-1]] = entry.get("status")
    observed = {
        "final_diff_present": final_diff.is_file(),
        "final_diff_bytes": final_diff.stat().st_size if final_diff.is_file() else 0,
        "manifest_statuses": statuses,
    }
    if not manifest:
        return _signal(INDETERMINATE, "no artifact manifest records the transfer", observed)
    if not observed["final_diff_present"] or not observed["final_diff_bytes"]:
        return _signal(NONCONFORMING, "no non-empty final submission was captured", observed)
    failed = sorted(name for name, status in statuses.items() if status not in ("ok", "copied"))
    if failed:
        return _signal(
            NONCONFORMING,
            f"the declared artifact transfer failed for {len(failed)} record(s): {failed[0]}",
            observed,
        )
    return _signal(CONFORMING, "the final submission was captured and transferred", observed)


def _signal_scoring_completeness(run: Path) -> dict[str, Any]:
    """Check the verifier produced its full record set for this rollout."""
    directory = run / "verifier"
    present = sorted(entry.name for entry in directory.iterdir()) if directory.is_dir() else []
    missing = [name for name in REQUIRED_VERIFIER_RECORDS if name not in present]
    observed = {"present": present, "missing": missing}
    if not present:
        return _signal(INDETERMINATE, "no verifier directory is committed", observed)
    if missing:
        return _signal(
            NONCONFORMING,
            f"the verifier record set is incomplete, missing {', '.join(missing)}",
            observed,
        )
    return _signal(CONFORMING, "the verifier produced its full record set", observed)


def _signal_termination(documents: dict[str, Any]) -> dict[str, Any]:
    """Check the solver terminated cleanly and through an explicit finish."""
    exception = _dotted(documents["result"], "exception_info")
    steps = _dotted(documents["trajectory"], "steps") or []
    finished = False
    for step in reversed(steps):
        if not isinstance(step, dict):
            continue
        for call in step.get("tool_calls") or []:
            if isinstance(call, dict) and call.get("function_name") == "finish":
                finished = True
                break
        if finished:
            break
    observed = {"exception_info": exception, "explicit_finish": finished}
    if exception:
        return _signal(NONCONFORMING, "the trial recorded an exception", observed)
    if not steps:
        return _signal(INDETERMINATE, "no steps are recorded for this rollout", observed)
    if not finished:
        return _signal(INDETERMINATE, "no explicit finish call is recorded", observed)
    return _signal(CONFORMING, "the solver terminated cleanly through an explicit finish", observed)


def _observation_text(step: Any) -> str:
    """Recover the real observation text a trajectory step recorded.

    The committed trajectories store ``observation`` as a mapping carrying a
    ``results`` list whose entries hold the tool output under ``content``, not
    as a string. Coercing the mapping with ``str`` yields a repr in which every
    newline is the two characters backslash and n, so a line-anchored pattern
    matches nothing and any scan over it reports an empty result for every
    rollout. That failure mode is silent and reads exactly like an honest
    negative, so the content is walked and joined here instead.
    """
    observation = step.get("observation") if isinstance(step, dict) else None
    if isinstance(observation, str):
        return observation
    if not isinstance(observation, dict):
        return ""
    chunks: list[str] = []
    for entry in observation.get("results") or []:
        if isinstance(entry, dict) and isinstance(entry.get("content"), str):
            chunks.append(entry["content"])
    for value in observation.values():
        if isinstance(value, str):
            chunks.append(value)
    return "\n".join(chunks)


def _signal(outcome: str, statement: str, observed: dict[str, Any]) -> dict[str, Any]:
    """Shape one three-valued signal-class outcome."""
    return {"outcome": outcome, "statement": statement, "observed": observed}


def _documents(run: Path) -> dict[str, Any]:
    """Load every committed carrier one rollout's fidelity is derived from."""
    return {
        "config": _read_json(run / "config.json"),
        "lock": _read_json(run / "lock.json"),
        "result": _read_json(run / "result.json"),
        "process": _read_json(run / "verifier" / "process.json"),
        "trajectory": _read_json(run / "agent" / "trajectory.json"),
        "manifest": _read_json(run / "artifacts" / "manifest.json"),
        "reward_reason": _read_json(run / "verifier" / "reward_reason.json"),
    }


def fidelity_coverage(bundle: Path, label: str, run: Path) -> dict[str, dict[str, Any]]:
    """Emit the three-valued fidelity_coverage predicate across the eight signal classes.

    This is the registered family adapter step 8u requires, run over the
    committed rollout bytes. Every class returns conforming, nonconforming or
    indeterminate; nothing returns a boolean, because a two-valued outcome
    would have to fold insufficient evidence into one of the other two and step
    8u forbids insufficient evidence ever reading as a pass.
    """
    documents = _documents(run)
    return {
        "solver_identity": _signal_solver_identity(run, label, documents),
        "task_binding": _signal_task_binding(bundle, documents),
        "horizon_conformance": _signal_horizon(bundle, documents),
        "tool_channel_integrity": _signal_tool_channel(documents),
        "context_handling": _signal_context(documents),
        "submission_capture": _signal_submission_capture(run, documents),
        "scoring_completeness": _signal_scoring_completeness(run),
        "termination_integrity": _signal_termination(documents),
    }


def derive_trial_status(coverage: dict[str, dict[str, Any]]) -> str:
    """Derive the trial status as exactly one of conforming, nonconforming, indeterminate.

    Nonconforming dominates because one demonstrated violation is a violation
    whatever else held. Indeterminate dominates conforming because a class that
    could not be evidenced is not a class that passed, which is the whole point
    of step 8u's three-valued requirement.
    """
    outcomes = {row["outcome"] for row in coverage.values()}
    if NONCONFORMING in outcomes:
        return NONCONFORMING
    if INDETERMINATE in outcomes:
        return INDETERMINATE
    return CONFORMING


def operator_status(run: Path) -> dict[str, Any]:
    """Read the operator's own declaration of how this rollout went.

    The operator declares ``status`` in verifier/process.json and declares an
    exception or its absence in result.json. ``scored`` with no exception is
    the operator asserting the trial conformed; anything else is read as the
    operator declining to assert it.
    """
    process = _read_json(run / "verifier" / "process.json")
    result = _read_json(run / "result.json")
    declared = str(_dotted(process, "status") or "")
    exception = _dotted(result, "exception_info")
    if not declared:
        return {"declared_token": "", "declared_status": INDETERMINATE, "exception": exception}
    if declared == "scored" and not exception:
        return {"declared_token": declared, "declared_status": CONFORMING, "exception": exception}
    return {"declared_token": declared, "declared_status": NONCONFORMING, "exception": exception}


def suppressing_violations(coverage: dict[str, dict[str, Any]], run: Path) -> list[dict[str, Any]]:
    """List violations in the direction that would lower a measured pass rate.

    Step 8u caps an observed violation in the suppressing direction at HOLD,
    and class 17 carries no exemption for a finding that would lower a measured
    pass rate. Suppression is measured in the direction that makes a task look
    harder, so a lost submission, an incomplete verifier record set, a
    truncated context and a cap that cut the solver short all qualify, and so
    does a committed zero whose reason names a grading failure rather than a
    solver failure.
    """
    found: list[dict[str, Any]] = []
    for name in sorted(SUPPRESSING_CLASSES):
        row = coverage.get(name)
        if row and row["outcome"] == NONCONFORMING:
            found.append({"signal_class": name, "statement": row["statement"]})
    reason = _read_json(run / "verifier" / "reward_reason.json")
    token = str(_dotted(reason, "reason") or "")
    if token in SUPPRESSING_REWARD_REASONS:
        found.append(
            {
                "signal_class": "reward_reason",
                "statement": (
                    f"the committed reward reason {token!r} attributes a zero to a grading "
                    "failure rather than to the solver, which lowers the measured pass rate"
                ),
            }
        )
    return found


def config_binding(run: Path) -> dict[str, Any]:
    """Re-derive the harness-config binding and compare it to the attested effective config.

    The binding is what the committed ``config.json`` and ``lock.json`` say was
    requested; the attestation is the ``config`` block ``result.json`` records
    as what ran. Comparing them is the whole instrument: a binding nobody can
    check against what ran is a declaration, not a configuration.
    """
    committed = _read_json(run / "lock.json")
    requested = _read_json(run / "config.json")
    attested = _dotted(_read_json(run / "result.json"), "config")
    if not isinstance(committed, dict) or not isinstance(attested, dict):
        return {
            "resolved": False,
            "reason": "the committed lock or the attested effective configuration is absent",
            "drift": [],
            "binding_digest": "",
            "attested_digest": "",
        }
    drift: list[dict[str, Any]] = []
    for label, committed_path, attested_path in CONFIG_BINDING_FIELDS:
        left = _dotted(committed, committed_path)
        right = _dotted(attested, attested_path)
        if left != right:
            drift.append({"field": label, "binding": left, "attested": right})
    return {
        "resolved": True,
        "reason": "",
        "drift": drift,
        "requested_present": isinstance(requested, dict),
        "binding_digest": core.canonical_digest(committed),
        "attested_digest": core.canonical_digest(attested),
    }


def config_approval(bundle: Path, run: Path) -> dict[str, Any]:
    """Search for an approval and an adequacy approval for the declared horizon.

    Step 8u caps at HOLD when a configuration is unapproved, and separately
    when it is inadequate for the declared horizon or carries no adequacy
    approval, EVEN WHEN it is pinned, signed and reproducible. Those are two
    conditions, so they are searched for and reported separately rather than
    collapsed into one boolean.
    """
    manifest = _read_toml(bundle / "task.toml")
    lock = _read_json(run / "lock.json")
    approval_fields = ("approved_by", "approval", "signature", "signed_by", "attestation")
    approved = any(field in (lock or {}) for field in approval_fields)
    approved = approved or any(
        field in (manifest.get("agent") or {}) or field in (manifest.get("verifier") or {})
        for field in approval_fields
    )
    adequacy_fields = ("horizon_adequacy", "adequacy_approval", "horizon_approved_by")
    adequate = any(
        field in (manifest.get("metadata") or {}) or field in (manifest.get("agent") or {})
        for field in adequacy_fields
    )
    return {
        "approved": approved,
        "adequacy_approved": adequate,
        "searched": list(APPROVAL_SEARCH_PATHS),
        "declared_horizon_turns": _dotted(lock, "agent.kwargs.max_iterations"),
        "declared_horizon_seconds": _dotted(manifest, "agent.timeout_sec"),
    }


def handoff_identity(run: Path) -> dict[str, Any]:
    """Compare the submission that reached the scorer with the one the solver produced.

    The scorer's copy is ``verifier/final.diff``. The solver's copy is the last
    diff the agent tree records in a tool observation, which is the only
    agent-side witness of the final workspace this format commits. Comparing
    the path sets rather than the bytes is deliberate: the observation is a
    truncated terminal capture, so a byte comparison would report drift for
    every rollout and prove nothing, while a path-set comparison detects a
    submission swapped for another submission.

    The witness header pattern is unanchored where the scorer-side pattern is
    line-anchored, because the observation carries terminal control sequences
    ahead of the first column and an anchored match would read a present
    witness as an absent one.
    """
    final_diff = _read_text(run / "verifier" / "final.diff")
    trajectory = _read_json(run / "agent" / "trajectory.json")
    steps = _dotted(trajectory, "steps") or []
    witness = ""
    witness_step: Any = None
    for step in steps:
        if not isinstance(step, dict):
            continue
        blob = _observation_text(step)
        if "diff --git " in blob:
            witness, witness_step = blob, step.get("step_id")
    scorer_paths = sorted({match.group("b") for match in DIFF_HEADER.finditer(final_diff or "")})
    witness_paths = sorted({match.group("b") for match in WITNESS_DIFF_HEADER.finditer(witness)})
    if final_diff is None:
        return {
            "verified": False,
            "reason": "no final.diff reached the scorer",
            "scorer_paths": 0,
            "witness_paths": 0,
            "witness_step": witness_step,
        }
    if not witness_paths:
        return {
            "verified": False,
            "reason": (
                "the agent tree records no diff of its final state, so the submission that "
                "reached the scorer has no agent-side counterpart to be compared against"
            ),
            "scorer_paths": len(scorer_paths),
            "witness_paths": 0,
            "witness_step": witness_step,
        }
    overlap = set(scorer_paths) & set(witness_paths)
    if not overlap:
        return {
            "verified": False,
            "reason": "the scorer's submission and the agent's final state share no path",
            "scorer_paths": len(scorer_paths),
            "witness_paths": len(witness_paths),
            "witness_step": witness_step,
        }
    return {
        "verified": True,
        "reason": "",
        "scorer_paths": len(scorer_paths),
        "witness_paths": len(witness_paths),
        "shared_paths": len(overlap),
        "witness_step": witness_step,
        "final_diff_sha256": core.sha256_bytes((final_diff or "").encode("utf-8")),
    }


def roster_search(base: Path, bundles: list[Path]) -> dict[str, Any]:
    """Search exhaustively for a precommitted roster and a fixed group count.

    Step 8u reconciles realized groups against the precommitted roster at the
    fixed group count and never lowers that count to fit what arrived. This
    function is the search that decides whether such a roster exists. It
    reports every place it looked, so a reader can tell the difference between
    a roster that is absent and a roster this harness failed to find.
    """
    looked: list[dict[str, Any]] = []
    found: list[dict[str, Any]] = []
    scope = recon.load_scope(base)
    trajectories = scope.get("trajectories") or {}
    population = trajectories.get("rollout_population") or {}
    looked.append(
        {
            "where": ".audit/scope.yaml trajectories.rollout_population",
            "keys": sorted(population),
            "roster_key_present": any(key in population for key in ROSTER_KEYS),
        }
    )
    for key in ROSTER_KEYS:
        if key in population:
            found.append({"where": "scope.yaml rollout_population", "key": key})
    for gap in scope.get("coverage_gaps") or []:
        if isinstance(gap, dict) and gap.get("id") == "D-FID-POPULATION-UNPROVABLE":
            looked.append(
                {
                    "where": ".audit/scope.yaml coverage_gaps D-FID-POPULATION-UNPROVABLE",
                    "caps": gap.get("caps"),
                    "closable_by": gap.get("closable_by"),
                    "closable_by_this_run": gap.get("closable_by_this_run"),
                }
            )
    for bundle in bundles:
        manifest = _read_toml(bundle / "task.toml")
        blocks = {**(manifest.get("metadata") or {}), **(manifest.get("span_provenance") or {})}
        looked.append(
            {
                "where": f"{bundle.name}/task.toml",
                "roster_key_present": any(key in blocks for key in ROSTER_KEYS),
            }
        )
        for key in ROSTER_KEYS:
            if key in blocks:
                found.append({"where": f"{bundle.name}/task.toml", "key": key})
        for label, run in rollouts(bundle):
            for name in ("config.json", "lock.json"):
                document = _read_json(run / name)
                keys = sorted(document) if isinstance(document, dict) else []
                looked.append(
                    {
                        "where": f"{bundle.name}/trajectories/{label}/{name}",
                        "roster_key_present": any(key in keys for key in ROSTER_KEYS),
                    }
                )
                for key in ROSTER_KEYS:
                    if key in keys:
                        found.append(
                            {"where": f"{bundle.name}/trajectories/{label}/{name}", "key": key}
                        )
    view = _crucible_view(base)
    looked.append(
        {
            "where": "/Users/macbookpro/levi/.memory/crucible_view.yaml",
            "present": bool(view),
            "roster_key_present": any(key in (view or {}) for key in ROSTER_KEYS),
            "cohort_registry_issuer": _view_registry_state(view),
        }
    )
    for key in ROSTER_KEYS:
        if key in (view or {}):
            found.append({"where": "crucible_view.yaml", "key": key})
    realized = {
        bundle.name: sorted({label.split("/")[0] for label, _ in rollouts(bundle)})
        for bundle in bundles
    }
    return {
        "roster_found": bool(found),
        "found": found,
        "searched": looked,
        "search_path_vocabulary": list(ROSTER_SEARCH_PATHS),
        "realized_groups": realized,
        "realized_group_count": {name: len(groups) for name, groups in realized.items()},
    }


def _crucible_view(base: Path) -> dict[str, Any] | None:
    """Load the CRUCIBLE_VIEW projection, returning None when it is absent."""
    candidates = [
        base.parent / ".memory" / "crucible_view.yaml",
        base / ".memory" / "crucible_view.yaml",
    ]
    for candidate in candidates:
        if candidate.is_file():
            try:
                import yaml

                loaded = yaml.safe_load(candidate.read_text(encoding="utf-8"))
            except (OSError, ValueError, ImportError):
                return None
            return loaded if isinstance(loaded, dict) else None
    return None


def _view_registry_state(view: dict[str, Any] | None) -> str:
    """Report what the projection says about the authority that would issue a roster."""
    if not view:
        return "projection absent"
    for entry in view.get("trust_roots") or view.get("escalation_flags") or []:
        if isinstance(entry, dict) and "cohort_registry_issuer" in (
            entry.get("authorized_roles") or []
        ):
            return f"status={entry.get('status')} identity={entry.get('identity')}"
    return "no cohort_registry_issuer row resolved in the projection"


def run_config(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-FID-CONFIG: re-derive the harness-config binding and compare it to the attestation.

    Drift or absence caps at HOLD. An unapproved configuration and one with no
    adequacy approval for the declared horizon each cap at HOLD as well, and
    they do so even when the configuration is pinned, signed and reproducible,
    so they are retained as their own findings rather than being read off the
    drift comparison.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    rows: list[dict[str, Any]] = []
    ran = False
    for bundle in bundles:
        for label, run in rollouts(bundle):
            binding = config_binding(run)
            approval = config_approval(bundle, run)
            conditions: set[str] = set()
            if not binding["resolved"]:
                gaps.append(
                    CoverageGap(
                        gap_id=f"D-FID-CONFIG-UNRESOLVED-{bundle.name}-{label.replace('/', '-')}",
                        instrument=CONFIG,
                        surface=_relative(run, base),
                        reason="config-binding-unresolved",
                        caps=Disposition.HOLD,
                        statement=(
                            "The harness-config binding could not be re-derived for this "
                            f"rollout: {binding['reason']}. An unresolvable binding is recorded "
                            "as unmeasured rather than as agreement."
                        ),
                        subject=bundle.name,
                    )
                )
                continue
            ran = True
            if not approval["approved"]:
                conditions.add("config-unpinned")
            if binding["drift"]:
                conditions.add("config-drift")
            if not approval["adequacy_approved"]:
                conditions.add("config-inadequate")
            reason = select_hold_reason(conditions)
            row = {
                "bundle": bundle.name,
                "rollout": label,
                "instrument": CONFIG,
                "drift_fields": [entry["field"] for entry in binding["drift"]],
                "binding_digest": binding["binding_digest"],
                "attested_digest": binding["attested_digest"],
                "approved": approval["approved"],
                "adequacy_approved": approval["adequacy_approved"],
                "hold_reason": reason,
            }
            rows.append(row)
            if binding["drift"]:
                findings.append(
                    Finding(
                        finding_id=f"FID-CONFIG-DRIFT-{bundle.name}-{label.replace('/', '-')}",
                        instrument=CONFIG,
                        critical_class=CRITICAL_CLASS,
                        severity=Severity.HIGH,
                        caps=Disposition.HOLD,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=(
                            "The attested effective configuration contradicts the binding the "
                            f"committed bytes declare for rollout {label}. Drifted fields: "
                            f"{', '.join(entry['field'] for entry in binding['drift'])}."
                        ),
                        evidence=dict(row, drift=binding["drift"]),
                    )
                )
            if not approval["approved"]:
                findings.append(
                    Finding(
                        finding_id=f"FID-CONFIG-UNAPPROVED-{bundle.name}-{label.replace('/', '-')}",
                        instrument=CONFIG,
                        critical_class=CRITICAL_CLASS,
                        severity=Severity.HIGH,
                        caps=Disposition.HOLD,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=(
                            f"The harness configuration for rollout {label} carries no approval "
                            "record anywhere in the committed bytes, so it is unbound rather "
                            "than merely undocumented. Searched: "
                            f"{'; '.join(approval['searched'])}. Step 8u selects the first "
                            "applicable HOLD reason, which here is config-unpinned."
                        ),
                        evidence=dict(row, approval=approval),
                    )
                )
            if not approval["adequacy_approved"]:
                findings.append(
                    Finding(
                        finding_id=f"FID-CONFIG-INADEQUATE-{bundle.name}-{label.replace('/', '-')}",
                        instrument=CONFIG,
                        critical_class=CRITICAL_CLASS,
                        severity=Severity.MEDIUM,
                        caps=Disposition.HOLD,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=(
                            "No adequacy approval exists for the declared horizon of rollout "
                            f"{label}, which declares {approval['declared_horizon_turns']} turns "
                            f"and {approval['declared_horizon_seconds']} seconds. Step 8u caps a "
                            "configuration with no adequacy approval at HOLD even when it is "
                            "pinned, signed and reproducible, and caps it independently of "
                            "configuration approval."
                        ),
                        evidence=dict(row, approval=approval),
                    )
                )
    return InstrumentResult(
        instrument=CONFIG,
        ran=ran,
        findings=findings,
        gaps=gaps,
        standing=Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE,
        notes={"rows": rows, "contract_step": "8u", "core_control_evidence_for": CORE_CONTROL},
    )


def run_trace(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-FID-TRACE: emit fidelity_coverage per rollout and derive the trial status.

    Refuses when the operator's declaration disagrees with the derived status.
    A suppressing violation caps at HOLD. Insufficient evidence is a coverage
    gap capping at HOLD and is never a pass, so an indeterminate class produces
    a gap rather than being rounded to conforming.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    rows: list[dict[str, Any]] = []
    ran = False
    for bundle in bundles:
        for label, run in rollouts(bundle):
            coverage = fidelity_coverage(bundle, label, run)
            derived = derive_trial_status(coverage)
            operator = operator_status(run)
            suppressing = suppressing_violations(coverage, run)
            indeterminate = sorted(
                name for name, row in coverage.items() if row["outcome"] == INDETERMINATE
            )
            ran = True
            tag = label.replace("/", "-")
            row = {
                "bundle": bundle.name,
                "rollout": label,
                "instrument": TRACE,
                "predicate": COVERAGE_PREDICATE,
                "conformance_predicate": TRIAL_CONFORMANCE_PREDICATE,
                "fidelity_coverage": {name: entry["outcome"] for name, entry in coverage.items()},
                "derived_status": derived,
                "operator_declared_status": operator["declared_status"],
                "operator_declared_token": operator["declared_token"],
                "indeterminate_classes": indeterminate,
                "suppressing_violations": suppressing,
                "hold_reason": "",
            }
            conditions: set[str] = set()
            if suppressing:
                conditions.add("fidelity-unverified")
            if operator["declared_status"] != derived:
                conditions.add("fidelity-unverified")
            if "context_handling" in indeterminate:
                conditions.add("context-uncovered")
            row["hold_reason"] = select_hold_reason(conditions)
            rows.append(row)
            if suppressing:
                findings.append(
                    Finding(
                        finding_id=f"FID-TRACE-SUPPRESSING-{bundle.name}-{tag}",
                        instrument=TRACE,
                        critical_class=CRITICAL_CLASS,
                        severity=Severity.HIGH,
                        caps=Disposition.HOLD,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=(
                            f"Rollout {label} carries {len(suppressing)} observed violation(s) in "
                            "the suppressing direction, meaning in the direction that lowers a "
                            "measured pass rate and makes this task look harder than it is. "
                            f"First: {suppressing[0]['signal_class']}, "
                            f"{suppressing[0]['statement']}. Class 17 carries no exemption for a "
                            "finding that would lower a measured pass rate."
                        ),
                        evidence=dict(row, coverage=coverage),
                    )
                )
            if operator["declared_status"] != derived:
                findings.append(
                    Finding(
                        finding_id=f"FID-TRACE-STATUS-DISAGREEMENT-{bundle.name}-{tag}",
                        instrument=TRACE,
                        critical_class=CRITICAL_CLASS,
                        severity=Severity.HIGH,
                        caps=Disposition.HOLD,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=(
                            f"The operator declares rollout {label} as "
                            f"{operator['declared_status']} through the token "
                            f"{operator['declared_token']!r}, and the derived trial status under "
                            f"{TRIAL_CONFORMANCE_PREDICATE} is {derived}. Step 8u requires a "
                            "refusal when the operator's declaration disagrees with the derived "
                            "status, so this instrument refuses rather than adopting either."
                        ),
                        evidence=dict(row, coverage=coverage),
                    )
                )
            if indeterminate:
                gaps.append(
                    CoverageGap(
                        gap_id=f"D-FID-COVERAGE-INSUFFICIENT-{bundle.name}-{tag}",
                        instrument=TRACE,
                        surface=_relative(run, base),
                        reason="fidelity-coverage-insufficient-evidence",
                        caps=Disposition.HOLD,
                        statement=(
                            f"Rollout {label} leaves {len(indeterminate)} of "
                            f"{len(SIGNAL_CLASSES)} signal classes indeterminate: "
                            f"{', '.join(indeterminate)}. Step 8u makes insufficient evidence a "
                            "coverage gap capping at HOLD and never a pass, so these classes are "
                            "recorded as unevidenced rather than rounded to conforming."
                        ),
                        subject=bundle.name,
                    )
                )
    return InstrumentResult(
        instrument=TRACE,
        ran=ran,
        findings=findings,
        gaps=gaps,
        standing=Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE,
        notes={
            "rows": rows,
            "signal_classes": list(SIGNAL_CLASSES),
            "contract_step": "8u",
            "core_control_evidence_for": CORE_CONTROL,
        },
    )


def run_population(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-FID-POPULATION: reconcile realized groups against the precommitted roster.

    The group count is never lowered to fit what arrived. If no precommitted
    roster and no fixed group count can be resolved, the population cannot be
    proven, and step 8u makes an unprovable population BLOCK because an
    unprovable population is no measurement rather than a weak one. The
    author-lane consequence string is encoded in the finding statement, with no
    suppression reason, exactly as step 8u requires.
    """
    search = roster_search(base, bundles)
    rows: list[dict[str, Any]] = []
    findings: list[Finding] = []
    for name, groups in sorted(search["realized_groups"].items()):
        rows.append(
            {
                "bundle": name,
                "instrument": POPULATION,
                "realized_groups": groups,
                "realized_group_count": len(groups),
                "precommitted_roster": None,
                "fixed_group_count": None,
                "reconciled": False,
                "hold_reason": "",
            }
        )
    if search["roster_found"]:
        return InstrumentResult(
            instrument=POPULATION,
            ran=True,
            findings=[],
            gaps=[
                CoverageGap(
                    gap_id="D-FID-POPULATION-ROSTER-UNRECONCILED",
                    instrument=POPULATION,
                    surface="trajectories",
                    reason="roster-resolved-but-reconciliation-unimplemented",
                    caps=Disposition.HOLD,
                    statement=(
                        "A roster key was resolved where this tree previously carried none, so "
                        "the realized groups were not reconciled against it by this run and the "
                        f"surface is recorded as unmeasured. Found: {search['found']}."
                    ),
                )
            ],
            standing=Standing.INSUFFICIENT_EVIDENCE,
            notes={"rows": rows, "roster_search": search, "contract_step": "8u"},
        )
    findings.append(
        Finding(
            finding_id="FID-POPULATION-UNPROVABLE",
            instrument=POPULATION,
            critical_class=CRITICAL_CLASS,
            severity=Severity.CRITICAL,
            caps=Disposition.BLOCK,
            bucket=Bucket.D,
            subject="project",
            statement=(
                "No precommitted roster and no fixed group count exists anywhere in this tree, "
                "so the realized population cannot be proven and the group count has no "
                "counterpart to reconcile against. The realized population is "
                f"{search['realized_group_count']}, which this instrument records as what "
                "arrived and never adopts as the fixed count, because lowering the count to fit "
                "what arrived is the exact substitution step 8u forbids. Step 8u states that a "
                "population that cannot be proven is BLOCK, because an unprovable population is "
                "no measurement rather than a weak one. The auditor therefore emits BLOCK and "
                f"the author lane records {INVALID_PILOT} with no suppression reason. Searched: "
                f"{'; '.join(ROSTER_SEARCH_PATHS)}."
            ),
            evidence={
                "roster_search": search,
                "author_lane_record": INVALID_PILOT,
                "suppression_reason": None,
                "scope_gap_id": "D-FID-POPULATION-UNPROVABLE",
            },
        )
    )
    return InstrumentResult(
        instrument=POPULATION,
        ran=True,
        findings=findings,
        gaps=[],
        standing=Standing.OBSERVED_VIOLATION,
        notes={
            "rows": rows,
            "roster_search": search,
            "author_lane_record": INVALID_PILOT,
            "contract_step": "8u",
            "core_control_evidence_for": CORE_CONTROL,
        },
    )


def run_handoff(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-FID-HANDOFF: verify the final submission's identity at the scorer.

    An unverifiable handoff caps at HOLD. The committed artifact manifest is
    read alongside the diff comparison because a manifest recording the
    transfer as failed means the copy in the tree did not arrive by the
    declared path, and a submission whose route to the scorer is unrecorded is
    a submission whose identity there is unverified.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    rows: list[dict[str, Any]] = []
    ran = False
    for bundle in bundles:
        for label, run in rollouts(bundle):
            identity = handoff_identity(run)
            manifest = _read_json(run / "artifacts" / "manifest.json")
            statuses = {}
            if isinstance(manifest, list):
                for entry in manifest:
                    if isinstance(entry, dict):
                        key = str(entry.get("destination", "")).rsplit("/", 1)[-1]
                        statuses[key] = entry.get("status")
            transfer_failed = sorted(
                name for name, status in statuses.items() if status not in ("ok", "copied")
            )
            ran = True
            tag = label.replace("/", "-")
            verified = identity["verified"] and not transfer_failed
            row = {
                "bundle": bundle.name,
                "rollout": label,
                "instrument": HANDOFF,
                "verified": verified,
                "diff_comparison": identity,
                "failed_transfers": transfer_failed,
                "hold_reason": "" if verified else select_hold_reason({"handoff-unverified"}),
            }
            rows.append(row)
            if verified:
                continue
            detail = identity["reason"] or (
                f"the declared artifact transfer failed for {len(transfer_failed)} record(s): "
                f"{', '.join(transfer_failed)}"
            )
            findings.append(
                Finding(
                    finding_id=f"FID-HANDOFF-UNVERIFIED-{bundle.name}-{tag}",
                    instrument=HANDOFF,
                    critical_class=CRITICAL_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        f"The identity of the final submission that reached the scorer for "
                        f"rollout {label} cannot be verified against the submission the solver "
                        f"produced: {detail}. Step 8u caps an unverifiable handoff at HOLD, and "
                        "the first applicable reason under its ordered precedence is "
                        "handoff-unverified."
                    ),
                    evidence=row,
                )
            )
    if not rows:
        gaps.append(
            CoverageGap(
                gap_id="D-FID-HANDOFF-NO-ROLLOUT",
                instrument=HANDOFF,
                surface="trajectories",
                reason="no-committed-rollout",
                caps=Disposition.HOLD,
                statement=(
                    "No committed rollout was found, so there was no submission handoff to "
                    "verify and the surface is recorded as unmeasured."
                ),
            )
        )
    return InstrumentResult(
        instrument=HANDOFF,
        ran=ran,
        findings=findings,
        gaps=gaps,
        standing=Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE,
        notes={"rows": rows, "contract_step": "8u", "core_control_evidence_for": CORE_CONTROL},
    )


def append_ledger(base: Path, results: list[InstrumentResult]) -> Path | None:
    """Append every per-task outcome to .audit/fidelity.yaml, the private ledger.

    Step 8u requires each instrument to append its per-task outcome to this
    file, which is stripped from every projection by name and never reaches the
    author. Writing goes through evidence.append_rows so the ledger schema
    stays single-sourced. No row carries a satisfied flag: this contract emits
    the evidence the ``execution_fidelity`` core control reconciles against and
    never marks that control satisfied itself.
    """
    rows: list[dict[str, Any]] = []
    for result in results:
        for row in result.notes.get("rows", []):
            rows.append(
                dict(
                    row,
                    disposition_cap=result.disposition.token,
                    standing=result.standing.value,
                    core_control_evidence_for=CORE_CONTROL,
                )
            )
    if not rows:
        return None
    target = base / core.AUDIT_DIRNAME / core.FIDELITY_FILENAME
    return evidence_mod.append_rows(target, rows, FIDELITY_SCHEMA)


def _guard(name: str, runner: Any, base: Path, bundles: list[Path]) -> InstrumentResult:
    """Run one instrument and convert any unexpected failure into a coverage gap.

    run_family must never raise, and an instrument that crashed must never read
    as a clean result, so a crash becomes an explicit gap naming the exception.
    """
    try:
        return runner(base, bundles)
    except Exception as error:
        return InstrumentResult(
            instrument=name,
            ran=False,
            gaps=[
                CoverageGap(
                    gap_id=f"D-FID-INSTRUMENT-CRASHED-{name}",
                    instrument=name,
                    surface="harness_code",
                    reason="instrument-raised",
                    caps=Disposition.HOLD,
                    statement=(
                        f"The instrument {name} raised {type(error).__name__} and produced no "
                        f"determination: {error}"
                    ),
                )
            ],
        )


def _ungated(reason: str) -> list[InstrumentResult]:
    """Return one gap-carrying result per instrument when the family does not apply."""
    return [
        InstrumentResult(
            instrument=name,
            ran=False,
            gaps=[
                CoverageGap(
                    gap_id=f"D-FID-FAMILY-UNGATED-{name}",
                    instrument=name,
                    surface="trajectories",
                    reason="trajectories-surface-absent",
                    caps=Disposition.HOLD,
                    statement=(
                        "Step 8u gates this family on scope.trajectories.present being true and "
                        f"that condition does not hold here: {reason}. A present trajectories "
                        "surface with no live instrument would itself be a coverage gap capping "
                        "at HOLD, so the absence is recorded rather than passed over."
                    ),
                )
            ],
        )
        for name in (CONFIG, TRACE, POPULATION, HANDOFF)
    ]


def run_family(base: Path, reconnaissance: recon.Recon) -> list[InstrumentResult]:
    """Run the four G-FID instruments and return one result each.

    Never raises. An instrument that fails unexpectedly becomes a result
    carrying an explaining coverage gap, because InstrumentResult treats
    ``ran`` false with no gap as BLOCK and a family that raised would abort the
    whole run rather than record what it could not measure.
    """
    try:
        scope = recon.load_scope(base)
    except (OSError, ValueError):
        scope = {}
    trajectories = scope.get("trajectories") or {}
    if not trajectories.get("present"):
        return _ungated("scope.yaml does not declare trajectories.present true")
    bundles = core.bundle_roots(base)
    results = [
        _guard(CONFIG, run_config, base, bundles),
        _guard(TRACE, run_trace, base, bundles),
        _guard(POPULATION, run_population, base, bundles),
        _guard(HANDOFF, run_handoff, base, bundles),
    ]
    try:
        ledger = append_ledger(base, results)
    except (OSError, ValueError) as error:
        results[0].gaps.append(
            CoverageGap(
                gap_id="D-FID-LEDGER-UNWRITABLE",
                instrument=CONFIG,
                surface=f"{core.AUDIT_DIRNAME}/{core.FIDELITY_FILENAME}",
                reason="fidelity-ledger-unwritable",
                caps=Disposition.HOLD,
                statement=(
                    "The private fidelity ledger could not be written, so the per-task outcomes "
                    f"step 8u requires it to accumulate are not recorded: {error}"
                ),
            )
        )
        ledger = None
    results[0].notes["ledger_path"] = str(ledger) if ledger else ""
    results[0].notes["ledger_stripped_from_projections_by_name"] = True
    results[0].notes["recon_root"] = str(reconnaissance.root)
    results[0].notes["hold_reason_precedence"] = list(HOLD_REASON_PRECEDENCE)
    return results


__all__ = [
    "CONFIG",
    "CONFORMING",
    "CORE_CONTROL",
    "FAMILY",
    "HANDOFF",
    "HOLD_REASON_PRECEDENCE",
    "INDETERMINATE",
    "INVALID_PILOT",
    "NONCONFORMING",
    "POPULATION",
    "SIGNAL_CLASSES",
    "TRACE",
    "append_ledger",
    "config_approval",
    "config_binding",
    "derive_trial_status",
    "fidelity_coverage",
    "handoff_identity",
    "operator_status",
    "roster_search",
    "rollouts",
    "run_config",
    "run_family",
    "run_handoff",
    "run_population",
    "run_trace",
    "select_hold_reason",
    "suppressing_violations",
]
