"""Contract step 8f: the G-VER verifier-robustness instrument family.

This module discharges the seven verifier-robustness probes the scope file
mandates under key ``verifier_robustness`` and lists in ``required_instruments``
as ``G-VER`` with ``probe_count: 7``. The rationale lives here rather than in
the contract because the contract is prompt-only, so the harness itself has to
carry the audit evidence for why each probe is shaped the way it is.

Every probe is pure Bucket D. A clean result never raises a disposition and is
never evidence that the verifier is robust; it is only evidence that this
particular probe found nothing. Phase 1 item 4 makes an absent, unprojected or
unresolvable required input a coverage gap capping at HOLD rather than a silent
pass, so each probe below splits itself into the half that is derivable from
committed bytes and the half that needs a resource this root does not hold, runs
the first, and records the second as a named gap.

Two resources are unavailable here and are named in the gaps rather than worked
around. The bundle base images are tag-only with empty digests and none of the
three resolve in the local daemon, and pulling them would cross the firewall
that Phase 1 item 4 forbids reaching across. Git execution is outside this
lane's permitted tool set, so the patch-apply paths cannot be exercised even
though the daemon is up.

The parser under test is imported from the bundle's own
``tests/harness_core.py`` and called directly. Reimplementing it here would hide
the exact defect these probes exist to find, because a reimplementation would
inherit this module's assumptions rather than the committed parser's behaviour.
The reward reduction is recomputed locally, which is a different thing: the
reduction is the arithmetic at ``run_tests.py`` line 504 over the imported
parser's output, not a second copy of the parser.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import core
import recon
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

FAMILY = "G-VER"

STABILITY = "G-VER-STABILITY"
INVARIANCE = "G-VER-INVARIANCE"
REPLAY = "G-VER-REPLAY"
BASELINE = "G-VER-BASELINE"
FLAKINESS = "G-VER-FLAKINESS"
ATTRIBUTION = "G-VER-ATTRIBUTION"
APPLY_PARITY = "G-VER-APPLY-PARITY"

HARNESS_CORE_RELATIVE = "tests/harness_core.py"
RUN_TESTS_RELATIVE = "tests/run_tests.py"
CONFIG_RELATIVE = "tests/config.json"
TARGET_LOG_NAME = "target-stdout.md"
PRESERVE_LOG_NAME = "preserve-stdout.md"
REWARD_NAME = "reward.json"
REWARD_REASON_NAME = "reward_reason.json"

PRESERVE_COVERAGE_FLOOR = 60

HARNESS_DERIVED_REPLAY_TRIALS = 3

ZERO_REASON_VOCABULARY = frozenset(
    {
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
        "preserve-set-did-not-execute",
        "preserve-set-underexecuted",
        "runner-exception",
        "verifier-did-not-complete",
        "no-target-resolved",
        "preserve-set-regression",
    }
)

DECLARED_APPLY_PATHS = (
    {
        "path": "candidate_submission",
        "exact": True,
        "fallback": "none",
        "failure_reason_string": "",
        "location": f"{RUN_TESTS_RELATIVE} lines 273 to 274",
    },
    {
        "path": "verifier_test_patch",
        "exact": True,
        "fallback": "mirrored-deletions-exclude-list",
        "failure_reason_string": "test-patch-did-not-apply",
        "location": f"{RUN_TESTS_RELATIVE} line 336 with failure at lines 338 to 341",
    },
)


def _register() -> None:
    """Register the seven G-VER instruments under the Phase 1 item 4 schema.

    Every declaration carries all twelve fields. ``disposition_cap_on_absence``
    is HOLD for the probes whose absence leaves a surface unmeasured and BLOCK
    for the replay probe, because a deterministic parser defect is invisible to
    every other probe in this family and losing it would leave the family
    reporting clean over an unexamined parser.
    """
    common: dict[str, Any] = {
        "category": Category.VERIFIER_ROBUSTNESS,
        "ecosystems": ("rust", "python"),
        "bucket": Bucket.D,
        "database_pin": "committed-bundle-bytes",
    }
    declarations = (
        (
            STABILITY,
            "python3",
            900.0,
            ("committed reference solution", "bundle container image"),
            "score-variance-across-regrades",
            EvidenceClass.EXECUTION_REPLAY,
            Disposition.HOLD,
            "Re-grades the committed reference solution and retains score variance.",
        ),
        (
            INVARIANCE,
            "python3",
            600.0,
            ("committed runner logs", "committed parser"),
            "parser-invariance-under-bound-perturbations",
            EvidenceClass.EXECUTION_REPLAY,
            Disposition.HOLD,
            "Replays the bound perturbation set through the committed parser.",
        ),
        (
            REPLAY,
            "python3",
            600.0,
            ("committed runner logs", "committed reward records"),
            "recomputed-versus-reported-score",
            EvidenceClass.EXECUTION_REPLAY,
            Disposition.BLOCK,
            "Reconciles every recomputed score against its reported score.",
        ),
        (
            BASELINE,
            "python3",
            900.0,
            ("unmodified base tree", "bundle container image"),
            "preserve-and-non-target-green-at-base",
            EvidenceClass.EXECUTION_REPLAY,
            Disposition.HOLD,
            "Grades the unmodified base and retains a pre-existing failure.",
        ),
        (
            FLAKINESS,
            "python3",
            1800.0,
            ("graded target set", "bundle container image"),
            "per-target-verdict-stability",
            EvidenceClass.EXECUTION_REPLAY,
            Disposition.HOLD,
            "Repeats every graded target and retains a flapping target.",
        ),
        (
            ATTRIBUTION,
            "python3",
            300.0,
            ("committed reward records",),
            "machine-readable-zero-attribution",
            EvidenceClass.SET_RELATION,
            Disposition.HOLD,
            "Requires every zero score to carry a machine-readable reason.",
        ),
        (
            APPLY_PARITY,
            "git",
            600.0,
            ("enumerated patch-apply paths", "git execution"),
            "apply-path-score-parity",
            EvidenceClass.EXECUTION_REPLAY,
            Disposition.HOLD,
            "Scores one submission through every enumerated patch-apply path.",
        ),
    )
    for (
        name,
        binary,
        timeout,
        conditions,
        capability,
        evidence_class,
        cap_on_absence,
        note,
    ) in declarations:
        if name in REGISTRY:
            continue
        REGISTRY.register(
            Instrument(
                name=name,
                binary=binary,
                timeout_seconds=timeout,
                required_conditions=conditions,
                critical_capability=capability,
                evidence_class=evidence_class,
                requires_parser=True,
                requires_raw_artifact=True,
                disposition_cap_on_absence=cap_on_absence,
                notes=note,
                fixture_ids=(),
                **common,
            )
        )


_register()


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


def _load_committed_parser(bundle: Path) -> tuple[Any | None, str]:
    """Import the bundle's own tests/harness_core.py and return the module.

    Step 8f requires replaying through the committed parser rather than through
    a reimplementation, so this import is load-bearing: the module object it
    returns is the same code the graded run executes. The module name is keyed
    on the bundle uuid so three byte-identical copies cannot collide in
    sys.modules and silently make one bundle's result stand in for another's.

    Bytecode writing is suppressed for the duration because the import would
    otherwise drop a __pycache__ directory inside the bundle, and this harness
    writes nothing outside .audit.
    """
    source = bundle / HARNESS_CORE_RELATIVE
    if not source.is_file():
        return None, f"{HARNESS_CORE_RELATIVE} is absent"
    module_name = f"crucible_harness_core_{bundle.name.replace('-', '_')}"
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(module_name, source)
        if spec is None or spec.loader is None:
            return None, "import spec could not be built"
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except (OSError, SyntaxError, ImportError, ValueError, TypeError) as error:
        return None, f"{type(error).__name__}: {error}"
    finally:
        sys.dont_write_bytecode = previous
    return module, ""


def _bundle_parser(module: Any, config: dict) -> tuple[Callable[[str], dict] | None, str]:
    """Select the parse function the bundle's config names, via its PARSERS dict."""
    key = str(config.get("parser") or "")
    parsers = getattr(module, "PARSERS", None)
    if not isinstance(parsers, dict):
        return None, "harness_core exposes no PARSERS mapping"
    parser = parsers.get(key)
    if parser is None:
        return None, f"parser key {key!r} is absent from PARSERS"
    return parser, key


def _perturb_line_order(text: str) -> str:
    """Bound class line_order: reverse every line, preserving membership."""
    return "\n".join(reversed(text.splitlines()))


def _perturb_indentation(text: str) -> str:
    """Bound class section_indentation_or_nesting: pad every line."""
    return "\n".join("    " + line for line in text.splitlines())


def _perturb_dialect_prefix(text: str) -> str:
    """Bound class dialect_or_suite_name_prefixes, the strongest probe.

    Every marker check in both parsers in force is an anchored prefix test
    applied after strip, so one uniform leading token models a compose service
    prefix or a bracketed suite tag and exercises that anchor directly.
    """
    return "\n".join("svc-1  | " + line for line in text.splitlines())


def _perturb_ordinal_counter(text: str) -> str:
    """Bound class ordinal_suffixes: append a percentage progress group."""
    return "\n".join(
        f"{line} [ {index % 100:>2d}%]" for index, line in enumerate(text.splitlines())
    )


def _perturb_timestamp(text: str) -> str:
    """Bound class timestamps: prepend an ISO instant to every line."""
    return "\n".join("2026-09-23T08:00:00Z " + line for line in text.splitlines())


def _perturb_interleaved(text: str) -> str:
    """Bound class interleaved_output: model relocation plus parallel splicing.

    run() at run_tests.py lines 134 to 146 returns stdout concatenated with
    stderr, so stderr is relocated after all stdout instead of interleaved
    chronologically. The rust bundle's graded command is bare cargo test with no
    --test-threads=1, so genuine byte-level interleaving from parallel workers
    is reachable as well. This models both at once by relocating a slice and
    splicing a worker line into the middle of a retained line.
    """
    lines = text.splitlines()
    if len(lines) < 4:
        return text
    midpoint = len(lines) // 2
    head = lines[:midpoint]
    tail = lines[midpoint:]
    if head:
        pivot = head[-1]
        cut = max(1, len(pivot) // 2)
        head[-1] = pivot[:cut] + "warning: worker 2 emitted a line here" + pivot[cut:]
    return "\n".join(head + tail)


BOUND_PERTURBATIONS: tuple[tuple[str, Callable[[str], str]], ...] = (
    ("line_order", _perturb_line_order),
    ("section_indentation_or_nesting", _perturb_indentation),
    ("dialect_or_suite_name_prefixes", _perturb_dialect_prefix),
    ("ordinal_suffixes", _perturb_ordinal_counter),
    ("timestamps", _perturb_timestamp),
    ("interleaved_output", _perturb_interleaved),
)


def _declared_sets(config: dict) -> dict[str, list[str]]:
    """The declared target and preserve identifier sets from committed config."""
    return {
        "f2p": list(config.get("f2p_tests") or []),
        "preserve": list(config.get("p2p_tests") or []),
        "n2p": list(config.get("n2p_tests") or []),
        "s2p": list(config.get("s2p_tests") or []),
    }


def _recompute_reward(
    module: Any,
    config: dict,
    target_outcomes: dict[str, str],
    preserve_outcomes: dict[str, str],
) -> dict[str, Any]:
    """Recompute the reward reduction over the committed parser's own output.

    This mirrors the arithmetic at run_tests.py line 504 and the preserve veto
    at lines 499 to 502, consuming outcome dictionaries the committed parser
    produced. It reimplements the reduction, never the parser, because the
    reduction is what has to be reconciled against the reported score while the
    parser is the thing under test.
    """
    declared = _declared_sets(config)
    f2p = declared["f2p"]
    extra = declared["n2p"] + declared["s2p"]
    resolved, ambiguous, missing = module.resolve_declared(f2p, target_outcomes)
    preserve = declared["preserve"]
    preserve_resolved, _, preserve_missing = module.resolve_declared(preserve, preserve_outcomes)
    hit = [target for target in f2p if resolved.get(target) == "PASS"]
    extra_resolved = module.resolve_declared(extra, target_outcomes)[0] if extra else {}
    extra_hit = [target for target in extra if extra_resolved.get(target) == "PASS"]
    broken = [target for target in preserve if preserve_resolved.get(target) == "FAIL"]
    denominator = float(len(f2p) + len(extra))
    coverage = (
        100.0 * (len(preserve) - len(preserve_missing)) / float(len(preserve))
        if preserve
        else 100.0
    )
    if not f2p:
        return {"reward": 0.0, "reason": "empty-fail-to-pass-set", "coverage_percent": coverage}
    if ambiguous:
        return {"reward": 0.0, "reason": "declared-target-ambiguous", "coverage_percent": coverage}
    if missing and len(missing) == len(f2p):
        return {
            "reward": 0.0,
            "reason": "declared-targets-absent-from-output",
            "coverage_percent": coverage,
        }
    if missing:
        return {
            "reward": 0.0,
            "reason": "declared-targets-partially-absent",
            "coverage_percent": coverage,
        }
    if preserve and coverage < PRESERVE_COVERAGE_FLOOR:
        return {
            "reward": 0.0,
            "reason": "preserve-set-underexecuted",
            "coverage_percent": coverage,
        }
    if broken:
        return {"reward": 0.0, "reason": "preserve-set-regression", "coverage_percent": coverage}
    reward = (len(hit) + len(extra_hit)) / denominator if denominator else 0.0
    return {
        "reward": reward,
        "reason": "graded" if reward > 0 else "no-target-resolved",
        "coverage_percent": coverage,
        "f2p_resolved": len(hit),
        "f2p_total": len(f2p),
        "preserve_broken": len(broken),
    }


def _membership_resolution(module: Any, declared: list[str], parsed: dict[str, str]) -> dict:
    """Split target resolution into exact membership and suffix fallback.

    Step 8f retains target matching by anything other than set membership over
    normalized test names. resolve_declared at harness_core.py lines 457 to 500
    tries exact match first and then a suffix match over ID_SEPARATORS, so the
    fallback is measurable as the set of targets that resolved without the
    declared identifier ever appearing as a parsed key.
    """
    resolved, ambiguous, missing = module.resolve_declared(declared, parsed)
    normalized_parsed = {core.normalize_text(key) for key in parsed}
    exact = [target for target in declared if target in parsed]
    normalized_hits = [
        target for target in declared if core.normalize_text(target) in normalized_parsed
    ]
    fallback = sorted(set(resolved) - set(exact))
    return {
        "resolved": len(resolved),
        "ambiguous": len(ambiguous),
        "missing": len(missing),
        "exact_membership": len(exact),
        "normalized_membership": len(normalized_hits),
        "suffix_fallback_targets": fallback,
    }


def _trajectory_runs(bundle: Path) -> Iterator[tuple[str, Path]]:
    """Yield every committed rollout's verifier directory as (label, path)."""
    root = bundle / "trajectories"
    if not root.is_dir():
        return
    for model in sorted(root.iterdir()):
        if not model.is_dir():
            continue
        for run in sorted(model.iterdir()):
            if not run.is_dir():
                continue
            verifier_dir = run / "verifier"
            if verifier_dir.is_dir():
                yield f"{model.name}/{run.name}", verifier_dir


def _image_reference(bundle: Path) -> str:
    """The FROM reference of the bundle's committed tests/Dockerfile."""
    text = _read_text(bundle / "tests" / "Dockerfile")
    if text is None:
        return ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("FROM "):
            return stripped[len("FROM ") :].strip()
    return ""


def _image_state(bundle: Path) -> tuple[dict, RawArtifact | None]:
    """Resolve whether the bundle's base image is digest-pinned and local.

    The inspect call queries the local daemon only. It never pulls, because
    Phase 1 item 4 refuses an absent input rather than reaching across the
    firewall for it.
    """
    reference = _image_reference(bundle)
    if not reference:
        return {"reference": "", "digest_pinned": False, "present": False}, None
    artifact = core.run_capture(
        ["docker", "image", "inspect", reference],
        artifact_id=f"docker-inspect-{bundle.name}",
        timeout=60.0,
    )
    return (
        {
            "reference": reference,
            "digest_pinned": "@sha256:" in reference,
            "present": artifact.exit_code == 0,
            "blocked_reason": artifact.blocked_reason,
        },
        artifact,
    )


def _image_gap(instrument: str, states: list[dict], surface: str) -> CoverageGap:
    """A gap naming exactly which image was unavailable and why.

    Emitted only for references that do not resolve in the local daemon. A
    resolved image is recorded in the instrument notes instead, because a gap
    whose statement asserts unavailability over a present image would be false
    evidence.
    """
    named = ", ".join(
        f"{state['reference']} (digest_pinned={state['digest_pinned']}, local={state['present']})"
        for state in states
    )
    return CoverageGap(
        gap_id=f"D-VER-IMAGE-UNAVAILABLE-{instrument.rsplit('-', 1)[-1]}",
        instrument=instrument,
        surface=surface,
        reason="bundle-base-image-unavailable-offline",
        caps=Disposition.HOLD,
        statement=(
            "Container re-grading did not run for the named reference(s) because they do not "
            "resolve in the local daemon, and acquiring one would cross the firewall that "
            "Phase 1 item 4 forbids reaching across. Unavailable: "
            f"{named}. The byte-derivable half of this probe ran and is reported separately."
        ),
    )


def _trials_gap(instrument: str, knob: str) -> CoverageGap:
    """A gap for a trial count the approved scope does not project."""
    return CoverageGap(
        gap_id=f"D-VER-TRIALS-UNPROJECTED-{instrument.rsplit('-', 1)[-1]}",
        instrument=instrument,
        surface="verifier_robustness",
        reason="trial-count-unprojected",
        caps=Disposition.HOLD,
        statement=(
            f"The approved scope binds no {knob} under key verifier_robustness, so the repetition "
            "count this probe must run at is unprojected. The harness refuses to invent one, and "
            f"the derivable replay below runs at a harness-chosen {HARNESS_DERIVED_REPLAY_TRIALS} "
            "repetitions that carry no authority as the bound count."
        ),
    )


def _bound_trials(base: Path, knob: str) -> int | None:
    """Read a trial count the approved scope binds under verifier_robustness.

    Contract step 8f names stability_trials and flakiness_trials as scope-bound
    parameters. The operator change request of 2026-09-24 bound both counts and
    the binding rode through the Phase 0.5 re-approval of the scope digest, so
    a positive integer read here is an approved projection rather than a
    harness invention. Anything absent, non-integer, or non-positive resolves
    to None and the caller falls back to the unprojected-count gap.
    """
    projected = recon.load_scope(base).get("verifier_robustness")
    if not isinstance(projected, dict):
        return None
    raw = projected.get(knob)
    if isinstance(raw, bool) or not isinstance(raw, int) or raw <= 0:
        return None
    return raw


def _live_empty_measurement(base: Path, bundle: Path) -> dict | None:
    """Read the cached live empty-submission grading for a bundle, if measured.

    Contract step 8f G-VER-BASELINE requires grading the unmodified base inside
    the pinned image. The shared live runner in liveexec.py executed exactly
    that submission through the stock Harbor path and cached the componentwise
    reward record; this helper surfaces those measured components. It returns
    None whenever the runner is absent or the run did not resolve to a measured
    outcome, so an unmeasured base never masquerades as a clean one.
    """
    try:
        import liveexec
    except ImportError:
        return None
    result = liveexec.empty_run(base, bundle)
    if result.get("status") != liveexec.STATUS_MEASURED:
        return None
    components = result.get("components") or {}
    return {
        "reward": result.get("reward"),
        "reason": result.get("reason"),
        "preserve_broken": components.get("preserve_broken"),
        "preserve_matched": components.get("preserve_matched"),
        "preserve_total": components.get("preserve_total"),
        "targets_resolved": components.get("targets_resolved"),
    }


def _bundle_context(bundle: Path) -> tuple[dict | None, Any | None, Callable | None, str]:
    """Load the committed config, committed parser module, and parse function."""
    config = _read_json(bundle / CONFIG_RELATIVE)
    if not isinstance(config, dict):
        return None, None, None, f"{CONFIG_RELATIVE} absent or unparseable"
    module, error = _load_committed_parser(bundle)
    if module is None:
        return config, None, None, error
    parser, detail = _bundle_parser(module, config)
    if parser is None:
        return config, module, None, detail
    return config, module, parser, ""


def _run_stability(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-VER-STABILITY: re-grade the reference solution and retain score variance.

    The re-grade itself needs the bundle image, which this root cannot obtain
    without crossing the firewall, so that half is a named gap. The half that is
    derivable from committed bytes is whether the committed parser and the
    reward reduction are themselves deterministic: a parser that returned a
    different outcome map on a second pass over identical bytes would produce
    score variance no container could explain away.
    """
    bound_stability = _bound_trials(base, "stability_trials")
    stability_trials = bound_stability or HARNESS_DERIVED_REPLAY_TRIALS
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    artifacts: list[RawArtifact] = []
    states: list[dict] = []
    notes: dict[str, Any] = {"bundles": {}}
    ran = False
    for bundle in bundles:
        state, artifact = _image_state(bundle)
        states.append(state)
        if artifact is not None:
            artifacts.append(artifact)
        config, module, parser, error = _bundle_context(bundle)
        if config is None or module is None or parser is None:
            gaps.append(
                CoverageGap(
                    gap_id=f"D-VER-PARSER-UNLOADABLE-{bundle.name}",
                    instrument=STABILITY,
                    surface=_relative(bundle / HARNESS_CORE_RELATIVE, base),
                    reason="committed-parser-unloadable",
                    caps=Disposition.HOLD,
                    statement=(
                        "The committed parser could not be imported, so no derivable half of this "
                        f"probe ran for this bundle: {error}"
                    ),
                    subject=bundle.name,
                )
            )
            continue
        rows: list[float] = []
        for label, verifier_dir in _trajectory_runs(bundle):
            target = _read_text(verifier_dir / TARGET_LOG_NAME)
            preserve = _read_text(verifier_dir / PRESERVE_LOG_NAME)
            if target is None or preserve is None:
                continue
            scores = set()
            for _ in range(stability_trials):
                recomputed = _recompute_reward(module, config, parser(target), parser(preserve))
                scores.add(round(float(recomputed["reward"]), 12))
            ran = True
            rows.extend(scores)
            if len(scores) > 1:
                findings.append(
                    Finding(
                        finding_id=f"VER-STABILITY-VARIANCE-{bundle.name}-{label}",
                        instrument=STABILITY,
                        critical_class="verifier-robustness",
                        severity=Severity.HIGH,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=(
                            "Replaying one committed log through the committed parser produced "
                            f"more than one score across {stability_trials} "
                            f"repetitions: {sorted(scores)}. A grader whose score moves over "
                            "identical input bytes cannot be re-derived."
                        ),
                        evidence={
                            "bundle": bundle.name,
                            "rollout": label,
                            "scores": sorted(scores),
                            "log": _relative(verifier_dir / TARGET_LOG_NAME, base),
                        },
                    )
                )
        notes["bundles"][bundle.name] = {"derivable_scores": sorted(set(rows))}
    absent = [state for state in states if not state.get("present")]
    if absent:
        gaps.append(_image_gap(STABILITY, absent, "reference_solution_regrade"))
    else:
        notes["image_states"] = states
    if bound_stability is None:
        gaps.append(_trials_gap(STABILITY, "stability_trials"))
    else:
        notes["bound_stability_trials"] = bound_stability
    return InstrumentResult(
        instrument=STABILITY,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=artifacts,
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes=notes,
    )


def _run_invariance(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-VER-INVARIANCE: replay the bound perturbation set through the committed parser.

    Fully derivable from committed bytes. Each of the six bound perturbation
    classes is applied to the recorded runner logs, and the variant is replayed
    through the parse function the bundle's config names, reached through the
    committed PARSERS dict rather than by calling a parse function by name. Two
    outcomes are retained: a score that moves under a perturbation, and target
    resolution that depends on anything other than set membership over
    normalized test names.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    notes: dict[str, Any] = {"variants": []}
    ran = False
    for bundle in bundles:
        config, module, parser, error = _bundle_context(bundle)
        if config is None or module is None or parser is None:
            gaps.append(
                CoverageGap(
                    gap_id=f"D-VER-PARSER-UNLOADABLE-INVARIANCE-{bundle.name}",
                    instrument=INVARIANCE,
                    surface=_relative(bundle / HARNESS_CORE_RELATIVE, base),
                    reason="committed-parser-unloadable",
                    caps=Disposition.HOLD,
                    statement=f"The committed parser could not be imported: {error}",
                    subject=bundle.name,
                )
            )
            continue
        declared = _declared_sets(config)
        for label, verifier_dir in _trajectory_runs(bundle):
            target = _read_text(verifier_dir / TARGET_LOG_NAME)
            preserve = _read_text(verifier_dir / PRESERVE_LOG_NAME)
            if target is None or preserve is None:
                gaps.append(
                    CoverageGap(
                        gap_id=f"D-VER-LOG-UNPROJECTED-{bundle.name}-{label.replace('/', '-')}",
                        instrument=INVARIANCE,
                        surface=_relative(verifier_dir, base),
                        reason="recorded-runner-log-absent",
                        caps=Disposition.HOLD,
                        statement=(
                            "A recorded runner log is absent from this rollout, so the bound "
                            "perturbation set could not be replayed over it. The harness refuses "
                            "to fetch it and records the surface as unmeasured."
                        ),
                        subject=bundle.name,
                    )
                )
                continue
            ran = True
            baseline_outcomes = parser(target)
            baseline_reward = _recompute_reward(module, config, baseline_outcomes, parser(preserve))
            baseline_resolution = _membership_resolution(module, declared["f2p"], baseline_outcomes)
            if baseline_resolution["suffix_fallback_targets"]:
                findings.append(
                    Finding(
                        finding_id=f"VER-INVARIANCE-NONMEMBERSHIP-{bundle.name}-{label}",
                        instrument=INVARIANCE,
                        critical_class="verifier-robustness",
                        severity=Severity.HIGH,
                        caps=Disposition.HOLD,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=(
                            "Target resolution does not reduce to set membership over normalized "
                            "test names. resolve_declared at harness_core.py lines 457 to 500 "
                            "credited "
                            f"{len(baseline_resolution['suffix_fallback_targets'])} declared "
                            "target(s) through its suffix fallback over ID_SEPARATORS at line 436 "
                            "rather than through an exact parsed key, so a target can be credited "
                            "to a test whose identifier the declaration never names."
                        ),
                        evidence={
                            "bundle": bundle.name,
                            "rollout": label,
                            "fallback_targets": baseline_resolution["suffix_fallback_targets"][:8],
                            "exact_membership": baseline_resolution["exact_membership"],
                            "resolved": baseline_resolution["resolved"],
                            "locus": f"{HARNESS_CORE_RELATIVE} lines 457 to 500",
                        },
                    )
                )
            for class_name, transform in BOUND_PERTURBATIONS:
                variant_outcomes = parser(transform(target))
                variant_reward = _recompute_reward(
                    module, config, variant_outcomes, parser(transform(preserve))
                )
                variant_resolution = _membership_resolution(
                    module, declared["f2p"], variant_outcomes
                )
                moved = round(float(variant_reward["reward"]), 12) != round(
                    float(baseline_reward["reward"]), 12
                )
                reason_moved = variant_reward["reason"] != baseline_reward["reason"]
                fallback_targets = variant_resolution["suffix_fallback_targets"]
                row = {
                    "bundle": bundle.name,
                    "rollout": label,
                    "perturbation": class_name,
                    "baseline_reward": baseline_reward["reward"],
                    "variant_reward": variant_reward["reward"],
                    "baseline_keys": len(baseline_outcomes),
                    "variant_keys": len(variant_outcomes),
                    "score_moved": moved,
                    "reason_moved": reason_moved,
                    "suffix_fallback_targets": len(fallback_targets),
                }
                notes["variants"].append(row)
                if fallback_targets and not baseline_resolution["suffix_fallback_targets"]:
                    findings.append(
                        Finding(
                            finding_id=(
                                f"VER-INVARIANCE-NONMEMBERSHIP-{bundle.name}-{label}-{class_name}"
                            ),
                            instrument=INVARIANCE,
                            critical_class="verifier-robustness",
                            severity=Severity.HIGH,
                            caps=Disposition.BLOCK,
                            bucket=Bucket.D,
                            subject=bundle.name,
                            statement=(
                                f"Under the bound perturbation class {class_name} the declared "
                                "targets no longer appear as parsed keys, and resolve_declared "
                                f"credited {len(fallback_targets)} of them through its suffix "
                                "fallback over ID_SEPARATORS at harness_core.py line 436 instead. "
                                "The score survives only because target resolution is not set "
                                "membership over normalized test names, so a credited target is "
                                "matched to a parsed identifier the declaration never names."
                            ),
                            evidence=dict(
                                row,
                                fallback_sample=fallback_targets[:8],
                                baseline_exact_membership=baseline_resolution["exact_membership"],
                                variant_exact_membership=variant_resolution["exact_membership"],
                                locus=f"{HARNESS_CORE_RELATIVE} lines 457 to 500",
                                log=_relative(verifier_dir / TARGET_LOG_NAME, base),
                            ),
                        )
                    )
                if moved or reason_moved:
                    findings.append(
                        Finding(
                            finding_id=(
                                f"VER-INVARIANCE-OUTCOME-MOVED-{bundle.name}-{label}-{class_name}"
                            ),
                            instrument=INVARIANCE,
                            critical_class="verifier-robustness",
                            severity=Severity.CRITICAL,
                            caps=Disposition.BLOCK,
                            bucket=Bucket.D,
                            subject=bundle.name,
                            statement=(
                                f"The bound perturbation class {class_name} moved the graded "
                                "outcome over a log whose test results are unchanged. The score "
                                f"went from {baseline_reward['reward']} to "
                                f"{variant_reward['reward']}, the reduction reason from "
                                f"{baseline_reward['reason']} to {variant_reward['reason']}, and "
                                f"the parsed outcome map from {len(baseline_outcomes)} to "
                                f"{len(variant_outcomes)} identifiers. A cosmetic change to runner "
                                "output re-grades a submission whose behaviour did not change. A "
                                "coincident score is not robustness when the reward contract's own "
                                "machine-readable attribution moved with it."
                            ),
                            evidence=dict(
                                row,
                                baseline_reason=baseline_reward["reason"],
                                variant_reason=variant_reward["reason"],
                                parser=str(config.get("parser")),
                                log=_relative(verifier_dir / TARGET_LOG_NAME, base),
                                locus=f"{HARNESS_CORE_RELATIVE} PARSERS at line 405",
                            ),
                        )
                    )
    return InstrumentResult(
        instrument=INVARIANCE,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=[],
        standing=Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE,
        notes=notes,
    )


def _run_replay(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-VER-REPLAY: reconcile every recomputed score against its reported score.

    Mandatory because a deterministic parser defect is invisible to a
    reference-solution re-run: the re-run would reproduce the same wrong number
    every time and read as stable. Divergence between the score recomputed from
    the committed log and the score recorded in reward.json is retained.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    notes: dict[str, Any] = {"rows": []}
    ran = False
    for bundle in bundles:
        config, module, parser, error = _bundle_context(bundle)
        if config is None or module is None or parser is None:
            gaps.append(
                CoverageGap(
                    gap_id=f"D-VER-PARSER-UNLOADABLE-REPLAY-{bundle.name}",
                    instrument=REPLAY,
                    surface=_relative(bundle / HARNESS_CORE_RELATIVE, base),
                    reason="committed-parser-unloadable",
                    caps=Disposition.HOLD,
                    statement=f"The committed parser could not be imported: {error}",
                    subject=bundle.name,
                )
            )
            continue
        for label, verifier_dir in _trajectory_runs(bundle):
            reported = _read_json(verifier_dir / REWARD_NAME)
            target = _read_text(verifier_dir / TARGET_LOG_NAME)
            preserve = _read_text(verifier_dir / PRESERVE_LOG_NAME)
            if not isinstance(reported, dict) or target is None or preserve is None:
                gaps.append(
                    CoverageGap(
                        gap_id=f"D-VER-SCORE-UNPROJECTED-{bundle.name}-{label.replace('/', '-')}",
                        instrument=REPLAY,
                        surface=_relative(verifier_dir, base),
                        reason="reported-score-or-log-absent",
                        caps=Disposition.HOLD,
                        statement=(
                            "A reported score or a recorded runner log is absent from this "
                            "rollout, so no reconciliation was possible. The harness refuses to "
                            "fetch either and records the surface as unmeasured."
                        ),
                        subject=bundle.name,
                    )
                )
                continue
            ran = True
            recomputed = _recompute_reward(module, config, parser(target), parser(preserve))
            reported_value = float(reported.get("reward", -1.0))
            recomputed_value = float(recomputed["reward"])
            diverged = round(reported_value, 9) != round(recomputed_value, 9)
            row = {
                "bundle": bundle.name,
                "rollout": label,
                "reported": reported_value,
                "recomputed": recomputed_value,
                "recomputed_reason": recomputed["reason"],
                "diverged": diverged,
            }
            notes["rows"].append(row)
            if diverged:
                findings.append(
                    Finding(
                        finding_id=f"VER-REPLAY-DIVERGENCE-{bundle.name}-{label}",
                        instrument=REPLAY,
                        critical_class="verifier-robustness",
                        severity=Severity.CRITICAL,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=(
                            "Replaying the committed runner log through the committed parser "
                            f"recomputed {recomputed_value} while the rollout reports "
                            f"{reported_value}. The reported score is not re-derivable from the "
                            "bytes the bundle commits."
                        ),
                        evidence=dict(
                            row,
                            reward_record=_relative(verifier_dir / REWARD_NAME, base),
                            log=_relative(verifier_dir / TARGET_LOG_NAME, base),
                        ),
                    )
                )
    return InstrumentResult(
        instrument=REPLAY,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=[],
        standing=Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE,
        notes=notes,
    )


def _run_baseline(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-VER-BASELINE: require every preserve and non-target test green at base.

    Grading the unmodified base needs the bundle image, so that half is a named
    gap. The derivable half reads the baseline measurement the bundle itself
    commits in tests/config.json under preserve_baseline_stats and retains a
    preserve target recorded failing at base.

    This probe deliberately asserts nothing about the fail-to-pass set. Whether
    the intentional target set is red before repair belongs to G-CON-EMPTY, and
    asserting it here would let one instrument's clean result stand in for
    another's unrun one.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    artifacts: list[RawArtifact] = []
    states: list[dict] = []
    notes: dict[str, Any] = {"bundles": {}}
    ran = False
    for bundle in bundles:
        state, artifact = _image_state(bundle)
        states.append(state)
        if artifact is not None:
            artifacts.append(artifact)
        config = _read_json(bundle / CONFIG_RELATIVE)
        if not isinstance(config, dict):
            gaps.append(
                CoverageGap(
                    gap_id=f"D-VER-BASELINE-CONFIG-ABSENT-{bundle.name}",
                    instrument=BASELINE,
                    surface=_relative(bundle / CONFIG_RELATIVE, base),
                    reason="committed-config-absent",
                    caps=Disposition.HOLD,
                    statement="tests/config.json is absent or unparseable for this bundle.",
                    subject=bundle.name,
                )
            )
            continue
        stats = config.get("preserve_baseline_stats")
        if not isinstance(stats, dict):
            gaps.append(
                CoverageGap(
                    gap_id=f"D-VER-BASELINE-UNPROJECTED-{bundle.name}",
                    instrument=BASELINE,
                    surface=_relative(bundle / CONFIG_RELATIVE, base),
                    reason="baseline-measurement-unprojected",
                    caps=Disposition.HOLD,
                    statement=(
                        "The bundle commits no preserve_baseline_stats block, so no baseline "
                        "measurement is derivable from committed bytes and the container half is "
                        "unavailable, leaving the base state entirely unmeasured."
                    ),
                    subject=bundle.name,
                )
            )
            continue
        ran = True
        empty = stats.get("empty") if isinstance(stats.get("empty"), dict) else {}
        failing = int(empty.get("failing", 0) or 0)
        ambiguous = int(empty.get("ambiguous", 0) or 0)
        declared_count = int(empty.get("declared", 0) or 0)
        observed = int(empty.get("observed", 0) or 0)
        dropped = list(config.get("preserve_dropped_at_base") or [])
        notes["bundles"][bundle.name] = {
            "declared": declared_count,
            "observed": observed,
            "failing": failing,
            "ambiguous": ambiguous,
            "dropped_at_base": len(dropped),
        }
        live = _live_empty_measurement(base, bundle)
        if live is not None:
            notes["bundles"][bundle.name]["live_empty"] = live
            live_broken = int(live.get("preserve_broken", 0) or 0)
            if live_broken:
                findings.append(
                    Finding(
                        finding_id=f"VER-BASELINE-LIVE-PRESERVE-BROKEN-{bundle.name}",
                        instrument=BASELINE,
                        critical_class="verifier-robustness",
                        severity=Severity.HIGH,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=(
                            f"Grading the unmodified base inside the pinned image left {live_broken} "
                            "preserve target(s) failing, so the base is not green before repair "
                            "under live execution."
                        ),
                        evidence={"bundle": bundle.name, "live_empty": live},
                    )
                )
        if failing:
            findings.append(
                Finding(
                    finding_id=f"VER-BASELINE-PREEXISTING-FAILURE-{bundle.name}",
                    instrument=BASELINE,
                    critical_class="verifier-robustness",
                    severity=Severity.HIGH,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        f"The bundle's own baseline measurement records {failing} preserve "
                        "target(s) failing on the unmodified base, so the preserve set is not "
                        "green before repair and a regression veto cannot distinguish a "
                        "submission's damage from damage that was already there."
                    ),
                    evidence={
                        "bundle": bundle.name,
                        "failing": failing,
                        "declared": declared_count,
                        "source": _relative(bundle / CONFIG_RELATIVE, base),
                    },
                )
            )
        if dropped:
            findings.append(
                Finding(
                    finding_id=f"VER-BASELINE-DROPPED-AT-BASE-{bundle.name}",
                    instrument=BASELINE,
                    critical_class="verifier-robustness",
                    severity=Severity.MEDIUM,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        f"{len(dropped)} declared preserve target(s) do not execute on the "
                        "unmodified base and were dropped from the preserve set, so those "
                        "non-target tests are unobserved at base rather than observed green."
                    ),
                    evidence={
                        "bundle": bundle.name,
                        "dropped_count": len(dropped),
                        "dropped_sample": dropped[:8],
                        "source": _relative(bundle / CONFIG_RELATIVE, base),
                    },
                )
            )
    absent = [state for state in states if not state.get("present")]
    if absent:
        gaps.append(_image_gap(BASELINE, absent, "unmodified_base_regrade"))
    else:
        notes["image_states"] = states
    return InstrumentResult(
        instrument=BASELINE,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=artifacts,
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes=notes,
    )


def _run_flakiness(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-VER-FLAKINESS: repeat every graded target and retain a flapping target.

    Repetition inside the graded container is unavailable here, so that half is
    a named gap. The derivable half detects a target whose verdict already
    flaps inside one committed log. Both parsers in force collapse a repeated
    identifier by position, parse_rust by last write at lines 319 to 329 and
    parse_pytest by setdefault at line 154, so parsing a log forwards and with
    its lines reversed yields different verdicts exactly when one identifier
    was reported with two different outcomes in the same run.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    artifacts: list[RawArtifact] = []
    states: list[dict] = []
    notes: dict[str, Any] = {"rows": []}
    ran = False
    for bundle in bundles:
        state, artifact = _image_state(bundle)
        states.append(state)
        if artifact is not None:
            artifacts.append(artifact)
        config, module, parser, error = _bundle_context(bundle)
        if config is None or module is None or parser is None:
            gaps.append(
                CoverageGap(
                    gap_id=f"D-VER-PARSER-UNLOADABLE-FLAKINESS-{bundle.name}",
                    instrument=FLAKINESS,
                    surface=_relative(bundle / HARNESS_CORE_RELATIVE, base),
                    reason="committed-parser-unloadable",
                    caps=Disposition.HOLD,
                    statement=f"The committed parser could not be imported: {error}",
                    subject=bundle.name,
                )
            )
            continue
        declared = set(_declared_sets(config)["f2p"])
        for label, verifier_dir in _trajectory_runs(bundle):
            target = _read_text(verifier_dir / TARGET_LOG_NAME)
            if target is None:
                continue
            ran = True
            forward = parser(target)
            reversed_pass = parser(_perturb_line_order(target))
            conflicts = sorted(
                key
                for key in forward
                if key in reversed_pass and forward[key] != reversed_pass[key]
            )
            graded_conflicts = sorted(set(conflicts) & declared)
            notes["rows"].append(
                {
                    "bundle": bundle.name,
                    "rollout": label,
                    "conflicting_identifiers": len(conflicts),
                    "graded_conflicts": len(graded_conflicts),
                }
            )
            if graded_conflicts:
                findings.append(
                    Finding(
                        finding_id=f"VER-FLAKINESS-FLAPPING-TARGET-{bundle.name}-{label}",
                        instrument=FLAKINESS,
                        critical_class="verifier-robustness",
                        severity=Severity.HIGH,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=(
                            f"{len(graded_conflicts)} graded target(s) are reported with two "
                            "different verdicts inside a single committed runner log, so the "
                            "recorded verdict depends on which occurrence the parser collapsed "
                            "onto rather than on the test's behaviour."
                        ),
                        evidence={
                            "bundle": bundle.name,
                            "rollout": label,
                            "targets": graded_conflicts[:8],
                            "log": _relative(verifier_dir / TARGET_LOG_NAME, base),
                        },
                    )
                )
    absent = [state for state in states if not state.get("present")]
    if absent:
        gaps.append(_image_gap(FLAKINESS, absent, "graded_target_repetition"))
    elif states:
        notes["image_states"] = states
    bound_flakiness = _bound_trials(base, "flakiness_trials")
    if bound_flakiness is None:
        gaps.append(_trials_gap(FLAKINESS, "flakiness_trials"))
    else:
        notes["bound_flakiness_trials"] = bound_flakiness
    return InstrumentResult(
        instrument=FLAKINESS,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=artifacts,
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes=notes,
    )


def _run_attribution(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-VER-ATTRIBUTION: every zero score carries a machine-readable reason.

    Fully derivable from committed bytes. Each rollout's reward record is read
    alongside its reason record, a zero without a reason drawn from the
    verifier's own reason vocabulary is retained, and the reported score is
    reconciled against the recorded target counts so a reason that contradicts
    its own counts cannot pass as attribution.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    notes: dict[str, Any] = {"rows": []}
    ran = False
    for bundle in bundles:
        for label, verifier_dir in _trajectory_runs(bundle):
            reported = _read_json(verifier_dir / REWARD_NAME)
            reason_doc = _read_json(verifier_dir / REWARD_REASON_NAME)
            if not isinstance(reported, dict):
                gaps.append(
                    CoverageGap(
                        gap_id=f"D-VER-REWARD-ABSENT-{bundle.name}-{label.replace('/', '-')}",
                        instrument=ATTRIBUTION,
                        surface=_relative(verifier_dir, base),
                        reason="reward-record-absent",
                        caps=Disposition.HOLD,
                        statement=(
                            "This rollout commits no readable reward.json, so its score carries "
                            "no attribution this harness can read."
                        ),
                        subject=bundle.name,
                    )
                )
                continue
            ran = True
            value = float(reported.get("reward", -1.0))
            reason = ""
            if isinstance(reason_doc, dict):
                reason = str(reason_doc.get("reason") or "")
            machine_readable = reason in ZERO_REASON_VOCABULARY
            row = {
                "bundle": bundle.name,
                "rollout": label,
                "reward": value,
                "reason": reason,
                "machine_readable": machine_readable,
            }
            notes["rows"].append(row)
            if value == 0.0 and not machine_readable:
                findings.append(
                    Finding(
                        finding_id=f"VER-ATTRIBUTION-UNATTRIBUTED-ZERO-{bundle.name}-{label}",
                        instrument=ATTRIBUTION,
                        critical_class="verifier-robustness",
                        severity=Severity.HIGH,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=(
                            "A zero score carries no machine-readable reason from the verifier's "
                            f"own vocabulary. Recorded reason: {reason!r}. A zero that cannot be "
                            "attributed is indistinguishable from a grader that never ran."
                        ),
                        evidence=dict(
                            row, record=_relative(verifier_dir / REWARD_REASON_NAME, base)
                        ),
                    )
                )
            if isinstance(reason_doc, dict) and "f2p_total" in reason_doc:
                total = float(reason_doc.get("f2p_total") or 0.0)
                resolved = float(reason_doc.get("f2p_resolved") or 0.0)
                expected = resolved / total if total else 0.0
                if reason == "graded" and round(expected, 9) != round(value, 9):
                    findings.append(
                        Finding(
                            finding_id=f"VER-ATTRIBUTION-COUNT-MISMATCH-{bundle.name}-{label}",
                            instrument=ATTRIBUTION,
                            critical_class="verifier-robustness",
                            severity=Severity.HIGH,
                            caps=Disposition.BLOCK,
                            bucket=Bucket.D,
                            subject=bundle.name,
                            statement=(
                                f"The reported score {value} does not reconcile against the "
                                f"recorded target counts {resolved:.0f} of {total:.0f}, which "
                                f"imply {expected}."
                            ),
                            evidence=dict(row, implied=expected, resolved=resolved, total=total),
                        )
                    )
    return InstrumentResult(
        instrument=ATTRIBUTION,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=[],
        standing=Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE,
        notes=notes,
    )


def _run_apply_parity(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-VER-APPLY-PARITY: score one submission through every patch-apply path.

    Scoring through each path requires invoking git apply inside the graded
    image. Git execution is outside this lane's permitted tool set and no base
    image resolves locally, so the execution half is a named gap rather than a
    silently skipped check.

    The derivable half enumerates the apply paths the committed runner actually
    carries and checks the property that makes divergence detectable at all:
    each path's failure must be distinguishable by its own reason string, and a
    path that admits a fallback must not share a reason string with the exact
    path, otherwise a fallback score and an exact score could never be told
    apart after the fact.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    notes: dict[str, Any] = {"paths": list(DECLARED_APPLY_PATHS), "bundles": {}}
    ran = False
    for bundle in bundles:
        runner = _read_text(bundle / RUN_TESTS_RELATIVE)
        if runner is None:
            gaps.append(
                CoverageGap(
                    gap_id=f"D-VER-RUNNER-ABSENT-{bundle.name}",
                    instrument=APPLY_PARITY,
                    surface=_relative(bundle / RUN_TESTS_RELATIVE, base),
                    reason="committed-runner-absent",
                    caps=Disposition.HOLD,
                    statement="tests/run_tests.py is absent, so no apply path is enumerable.",
                    subject=bundle.name,
                )
            )
            continue
        ran = True
        observed = {
            "git_apply_present": "git apply --whitespace=nowarn" in runner,
            "three_way_present": "--3way" in runner,
            "mirrored_exclude_present": "--exclude=" in runner,
            "test_patch_reason_present": '"test-patch-did-not-apply"' in runner
            or "test-patch-did-not-apply" in runner,
            "candidate_apply_present": "git apply" in runner and "test_patch_path" not in runner,
        }
        notes["bundles"][bundle.name] = observed
        reasons = [
            declared["failure_reason_string"]
            for declared in DECLARED_APPLY_PATHS
            if declared["failure_reason_string"]
        ]
        if len(reasons) != len(set(reasons)):
            findings.append(
                Finding(
                    finding_id=f"VER-APPLY-PARITY-REASON-COLLISION-{bundle.name}",
                    instrument=APPLY_PARITY,
                    critical_class="verifier-robustness",
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        "Two enumerated patch-apply paths share one failure reason string, so a "
                        "score produced through a fallback path cannot be distinguished from a "
                        "score produced through the exact path."
                    ),
                    evidence={"bundle": bundle.name, "reasons": reasons},
                )
            )
        if observed["three_way_present"]:
            findings.append(
                Finding(
                    finding_id=f"VER-APPLY-PARITY-UNDECLARED-FALLBACK-{bundle.name}",
                    instrument=APPLY_PARITY,
                    critical_class="verifier-robustness",
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        "The committed runner carries a three-way apply fallback that the scope "
                        "enumeration does not declare, so an apply path exists whose score parity "
                        "against the exact path was never enumerated."
                    ),
                    evidence={"bundle": bundle.name, "observed": observed},
                )
            )
    gaps.append(
        CoverageGap(
            gap_id="D-VER-APPLY-EXECUTION-UNAVAILABLE",
            instrument=APPLY_PARITY,
            surface="patch_apply_paths",
            reason="apply-path-execution-unavailable",
            caps=Disposition.HOLD,
            statement=(
                "No submission was scored through the enumerated patch-apply paths. Exercising "
                "them requires invoking git apply inside the graded image, and git execution is "
                "outside this lane's permitted tool set while no bundle base image resolves in "
                "the local daemon. Acquiring an image would cross the firewall Phase 1 item 4 "
                "forbids reaching across. Only the enumeration and reason-distinguishability half "
                "ran, so exact-versus-fallback score parity itself remains unmeasured."
            ),
        )
    )
    return InstrumentResult(
        instrument=APPLY_PARITY,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=[],
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes=notes,
    )


def run_family(base: Path, reconnaissance: recon.Recon) -> list[InstrumentResult]:
    """Run the seven G-VER instruments and return one result each.

    Never raises. An instrument that fails unexpectedly is converted into a
    result carrying an explaining coverage gap, because InstrumentResult treats
    ``ran`` false with no gap as BLOCK and a family that raised would abort the
    whole run rather than record what it could not measure.
    """
    bundles = core.bundle_roots(base)
    results: list[InstrumentResult] = []
    probes: tuple[tuple[str, Callable[[Path, list[Path]], InstrumentResult]], ...] = (
        (STABILITY, _run_stability),
        (INVARIANCE, _run_invariance),
        (REPLAY, _run_replay),
        (BASELINE, _run_baseline),
        (FLAKINESS, _run_flakiness),
        (ATTRIBUTION, _run_attribution),
        (APPLY_PARITY, _run_apply_parity),
    )
    if not bundles:
        for name, _ in probes:
            results.append(
                InstrumentResult(
                    instrument=name,
                    ran=False,
                    gaps=[
                        CoverageGap(
                            gap_id=f"D-VER-NO-BUNDLE-{name.rsplit('-', 1)[-1]}",
                            instrument=name,
                            surface="bundles",
                            reason="no-resident-bundle",
                            caps=Disposition.HOLD,
                            statement=(
                                "No resident bundle carrying a task.toml was found under any lane "
                                "root, so this probe had no verifier surface to measure."
                            ),
                        )
                    ],
                )
            )
        return results
    for name, probe in probes:
        try:
            results.append(probe(base, bundles))
        except Exception as error:
            results.append(
                InstrumentResult(
                    instrument=name,
                    ran=False,
                    gaps=[
                        CoverageGap(
                            gap_id=f"D-VER-PROBE-FAILED-{name.rsplit('-', 1)[-1]}",
                            instrument=name,
                            surface="harness_code",
                            reason="probe-raised",
                            caps=Disposition.HOLD,
                            statement=(
                                "This probe raised before reaching a determination, so it "
                                "produced no evidence and is recorded as unmeasured rather than "
                                f"clean: {type(error).__name__}: {error}"
                            ),
                        )
                    ],
                    notes={"recon_root": str(reconnaissance.root)},
                )
            )
    return results


__all__ = [
    "APPLY_PARITY",
    "ATTRIBUTION",
    "BASELINE",
    "BOUND_PERTURBATIONS",
    "FAMILY",
    "FLAKINESS",
    "INVARIANCE",
    "REPLAY",
    "STABILITY",
    "run_family",
]
