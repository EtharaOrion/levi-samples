"""Contract step 8t: the G-ADV adversary-probe family, eight probes.

Step 8t builds this family against every committed bundle carrying a ``tests/``
tree, in the pinned image through the stock Harbor path the delivery block
binds and never through a vendor wrapper. The rationale lives here rather than
in the contract because the contract is prompt-only, so the harness itself has
to carry the audit evidence for why each probe is shaped the way it is.

The eight probes are a null submission, a negated gold answer, a bare list of
every identifier and line number drawn from the private truth, the oracle
deliverable set written with every service stubbed, an oracle-free workspace
carrying a planted test-collection hook, per-deliverable garbage written beside
the oracle, a schema-valid deliverable with every content field wrong, and a
fabricated trajectory carrying every rubric string.

The scoring rules are strict and are encoded verbatim. The null probe must
score exactly zero. The bundle must declare a null floor at or below 0.05 that
equals the measured null reward within 0.005. Every other probe must score at
or below that floor, except the per-deliverable probe, which must lose at least
the deliverable's declared discrimination weight. Any probe scoring above its
rule caps at BLOCK.

The container problem, and what this module does about it rather than around
it. Step 8t requires the pinned image, and no pinned image resolves at this
verification root. Bundles 6bf0c918 and 873914cf carry an empty
``base_image_digest`` field, nothing can be pulled because Phase 1 item 4
refuses to reach across the firewall, and the sanitized images named by
``[environment].docker_image`` are not present in the local daemon. Step 8t
also states that an unrunnable probe is BLOCK rather than a coverage gap. Those
two facts together would let a lazy implementation record eight silent gaps, so
this module splits the family by derivability instead, and the split is data in
``.audit/adversary/transforms.yaml`` rather than a judgement buried in code.

A probe is derivable without a container under exactly two conditions. Under
``byte_refusal`` the committed runner decides the reward before any test
command executes, on the submission artifact bytes alone: the verifier-tree
guard at run_tests.py lines 318 to 323 is such a decision, and so is the empty
fail-to-pass refusal at line 197. Under ``closure_invariant`` the probe's
carrier lies outside the static read closure of run_tests.py and the workspace
the graded command reads is byte-identical to the unmodified base, so the
runner log is the base log, which the committed
``preserve_baseline_stats.empty`` block measures for the preserve half and the
fail-to-pass declaration fixes for the target half. In both cases the reward is
then measured by importing the bundle's OWN ``tests/harness_core.py`` parse
function, running it over a runner log synthesized in that parser's own
dialect, and reducing the parsed outcomes through the arithmetic at
run_tests.py line 504. The parser is never reimplemented; a reimplementation
would inherit this module's assumptions rather than the committed parser's
behaviour, which is precisely the defect these probes exist to find.

Every other probe changes bytes the graded command reads, so its reward is a
function of test outcomes only an execution inside the pinned image can
produce. For each of those this module emits a retained Finding, not a coverage
gap, recording the probe as UNRUNNABLE with the contract's stated consequence
of BLOCK, and naming the specific bundle, the specific unavailable image field,
and the offline constraint. No score is invented for them. The contract's BLOCK
is never silently downgraded to a HOLD.

A separate and load-bearing absence: no bundle in this tree declares a null
floor at all. The nearest numeric is ``preserve_baseline_stats.ceiling``, which
is 0.05 in all three bundles but governs the share of the preserve set allowed
to be failing at base, a different quantity entirely. The comparison the rule
demands therefore cannot be made, and that absence is itself retained.

Directory and strip requirement. The transform tables, the generators and the
nonces live under ``.audit/adversary/``. Step 8t strips that directory from
every projection by name and it never reaches the author. A probe whose nonce
the author can read is a probe the author can special-case, and a special-cased
probe measures nothing. Nothing in this module writes outside ``.audit/``.

Every probe is pure Bucket D. A clean result never raises a disposition and is
never evidence that the verifier is adversarially sound; it is only evidence
that this particular probe found nothing.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import tomllib
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
    RawArtifact,
    Severity,
    Standing,
)
from registry import REGISTRY, Category, EvidenceClass, Instrument

FAMILY = "G-ADV"

CRITICAL_CLASS = "adversarial-probe-discrimination"

NULL = "G-ADV-NULL"
NEGATED = "G-ADV-NEGATED"
IDENTIFIERS = "G-ADV-IDENTIFIERS"
STUBBED = "G-ADV-STUBBED"
COLLECTION_HOOK = "G-ADV-COLLECTION-HOOK"
PER_DELIVERABLE = "G-ADV-PER-DELIVERABLE"
SCHEMA_VALID = "G-ADV-SCHEMA-VALID"
FABRICATED = "G-ADV-FABRICATED-TRAJECTORY"

PROBE_ROW_KEY = "adversary_probe_rows"

PRIVATE_DIRNAME = "adversary"
TRANSFORMS_FILENAME = "transforms.yaml"
NONCES_FILENAME = "nonces.yaml"

PROBE_NAMES: dict[str, str] = {
    NULL: "null-submission",
    NEGATED: "negated-gold",
    IDENTIFIERS: "truth-identifier-list",
    STUBBED: "oracle-stubbed",
    COLLECTION_HOOK: "collection-hook",
    PER_DELIVERABLE: "per-deliverable-garbage",
    SCHEMA_VALID: "schema-valid-wrong-content",
    FABRICATED: "fabricated-trajectory",
}

PROBE_ORDER: tuple[str, ...] = (
    NULL,
    NEGATED,
    IDENTIFIERS,
    STUBBED,
    COLLECTION_HOOK,
    PER_DELIVERABLE,
    SCHEMA_VALID,
    FABRICATED,
)

HARNESS_CORE_RELATIVE = "tests/harness_core.py"
RUN_TESTS_RELATIVE = "tests/run_tests.py"
CONFIG_RELATIVE = "tests/config.json"
TEST_PATCH_RELATIVE = "tests/test.patch"
RUBRICS_RELATIVE = "tests/rubrics.json"
FIX_PATCH_RELATIVE = "solution/fix.patch"
BOUNDING_RELATIVE = "solution/bounding.json"
GROUNDING_RELATIVE = "solution/grounding.yaml"

NULL_FLOOR_CEILING = 0.05
NULL_FLOOR_TOLERANCE = 0.005
REWARD_PRECISION = 9

BYTE_REFUSAL = "byte_refusal"
CLOSURE_INVARIANT = "closure_invariant"
LIVE_EXECUTION = "live_execution"

STATUS_PASS = "pass"
STATUS_FAIL = "fail"
STATUS_UNRUNNABLE = "unrunnable"

DIFF_HEADER = re.compile(r"^diff --git a/(?P<a>.+?) b/(?P<b>.+)$")
HUNK_HEADER = re.compile(r"^@@ -(?P<old>\d+(?:,\d+)?) \+(?P<new>\d+(?:,\d+)?) @@(?P<tail>.*)$")

COLLECTION_HOOK_PATHS: dict[str, str] = {
    "pytest": "conftest.py",
    "unittest": "conftest.py",
    "rust": "tests/crucible_adv_hook.rs",
}


def _register() -> None:
    """Declare the eight step 8t probes under the Phase 1 item 4 twelve-field schema.

    ``disposition_cap_on_absence`` is BLOCK on every row rather than HOLD,
    because step 8t states that an unrunnable probe is BLOCK rather than a
    coverage gap. Declaring HOLD here would encode the downgrade this contract
    forbids into the registry itself, where it would outlive any one run.
    """
    common: dict[str, Any] = {
        "category": Category.ADVERSARY,
        "ecosystems": ("rust", "python"),
        "bucket": Bucket.D,
        "database_pin": "committed-bundle-bytes",
        "binary": "python3",
        "evidence_class": EvidenceClass.EXECUTION_REPLAY,
        "requires_parser": True,
        "requires_raw_artifact": True,
        "disposition_cap_on_absence": Disposition.BLOCK,
    }
    declarations = (
        (
            NULL,
            600.0,
            ("committed tests tree", "pinned bundle image"),
            "null-submission-scores-exactly-zero",
            "Scores an empty submission and requires exactly zero.",
        ),
        (
            NEGATED,
            600.0,
            ("committed reference solution", "pinned bundle image"),
            "negated-gold-scores-at-or-below-the-null-floor",
            "Scores the reverse of the committed oracle diff.",
        ),
        (
            IDENTIFIERS,
            600.0,
            ("committed private truth", "pinned bundle image"),
            "identifier-dump-scores-at-or-below-the-null-floor",
            "Scores a bare dump of every private identifier and line number.",
        ),
        (
            STUBBED,
            900.0,
            ("committed reference solution", "pinned bundle image"),
            "service-stubbed-oracle-scores-at-or-below-the-null-floor",
            "Scores the oracle deliverable set with every service stubbed.",
        ),
        (
            COLLECTION_HOOK,
            600.0,
            ("committed test patch", "pinned bundle image"),
            "planted-collection-hook-scores-at-or-below-the-null-floor",
            "Scores an oracle-free workspace carrying a test-collection hook.",
        ),
        (
            PER_DELIVERABLE,
            900.0,
            ("declared discrimination weight", "pinned bundle image"),
            "per-deliverable-garbage-loses-the-discrimination-weight",
            "Scores per-deliverable garbage written beside the oracle.",
        ),
        (
            SCHEMA_VALID,
            600.0,
            ("committed reference solution", "pinned bundle image"),
            "schema-valid-wrong-content-scores-at-or-below-the-null-floor",
            "Scores a schema-valid deliverable whose every content field is wrong.",
        ),
        (
            FABRICATED,
            600.0,
            ("committed rubric strings", "pinned bundle image"),
            "fabricated-trajectory-scores-at-or-below-the-null-floor",
            "Scores a fabricated trajectory carrying every rubric string.",
        ),
    )
    for name, timeout, conditions, capability, note in declarations:
        if name in REGISTRY:
            continue
        REGISTRY.register(
            Instrument(
                name=name,
                timeout_seconds=timeout,
                required_conditions=conditions,
                critical_capability=capability,
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


def _read_text(path: Path) -> str | None:
    """Read committed bytes as text, returning None rather than raising."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _read_json(path: Path) -> Any | None:
    """Load a committed JSON document, returning None rather than raising."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _read_yaml(path: Path) -> Any | None:
    """Load a committed YAML document, returning None rather than raising."""
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def _read_toml(path: Path) -> dict[str, Any]:
    """Load a committed TOML manifest, failing closed to an empty mapping."""
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def private_dir(base: Path) -> Path:
    """The step 8t private directory holding transform tables, generators and nonces.

    Named by a function rather than inlined so the strip list has one symbol to
    key on and so no caller can quietly reach a different directory.
    """
    return base / core.AUDIT_DIRNAME / PRIVATE_DIRNAME


def transform_table(base: Path) -> dict[str, Any]:
    """Load the probe transform table from the private directory.

    Returning an empty mapping rather than raising lets the caller record an
    absent table as a coverage gap, because a probe family running without its
    declared transforms would be measuring something other than what the table
    says it measures.
    """
    loaded = _read_yaml(private_dir(base) / TRANSFORMS_FILENAME)
    return loaded if isinstance(loaded, dict) else {}


def nonce_table(base: Path) -> dict[str, Any]:
    """Load the deterministic nonce derivation from the private directory."""
    loaded = _read_yaml(private_dir(base) / NONCES_FILENAME)
    return loaded if isinstance(loaded, dict) else {}


def probe_nonce(base: Path, probe: str, uuid: str) -> str:
    """Derive one probe nonce deterministically from the recorded seed.

    Deterministic rather than random because a probe artifact that differs
    between two runs of this harness cannot be reconciled against a recorded
    row, and an unreconcilable row is not evidence.
    """
    table = nonce_table(base)
    seed = str(table.get("seed") or "")
    width = int(table.get("truncation_hex_chars") or 16)
    payload = f"{seed}:{probe}:{uuid}".encode()
    return hashlib.sha256(payload).hexdigest()[:width]


def _load_committed_modules(bundle: Path) -> tuple[Any | None, Any | None, str]:
    """Import the bundle's own harness_core and run_tests and return both modules.

    Step 8t scores through the committed grading path, so both modules are the
    real committed code rather than a reimplementation. run_tests.py imports
    ``harness_core`` by bare name, so the bundle's own harness_core module is
    bound under that name for the duration of the exec and the previous binding
    is restored afterwards; three byte-identical copies would otherwise collide
    in sys.modules and let one bundle's parser stand in for another's.

    Bytecode writing is suppressed because the import would otherwise drop a
    __pycache__ directory inside the bundle, and this harness writes nothing
    outside .audit.
    """
    core_source = bundle / HARNESS_CORE_RELATIVE
    runner_source = bundle / RUN_TESTS_RELATIVE
    if not core_source.is_file():
        return None, None, f"{HARNESS_CORE_RELATIVE} is absent"
    if not runner_source.is_file():
        return None, None, f"{RUN_TESTS_RELATIVE} is absent"
    suffix = bundle.name.replace("-", "_")
    previous_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    sentinel = object()
    shadowed = sys.modules.get("harness_core", sentinel)
    try:
        harness = _exec_module(f"crucible_adv_harness_core_{suffix}", core_source)
        sys.modules["harness_core"] = harness
        runner = _exec_module(f"crucible_adv_run_tests_{suffix}", runner_source)
    except (OSError, SyntaxError, ImportError, ValueError, TypeError, KeyError) as error:
        return None, None, f"{type(error).__name__}: {error}"
    finally:
        if shadowed is sentinel:
            sys.modules.pop("harness_core", None)
        else:
            sys.modules["harness_core"] = shadowed
        sys.dont_write_bytecode = previous_bytecode
    return harness, runner, ""


def _exec_module(module_name: str, source: Path) -> Any:
    """Execute one committed source file as a uniquely named module object."""
    spec = importlib.util.spec_from_file_location(module_name, source)
    if spec is None or spec.loader is None:
        raise ImportError(f"import spec could not be built for {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def image_state(bundle: Path) -> dict[str, Any]:
    """Record exactly which pinned image this bundle names and whether it resolves.

    The inspect call queries the local daemon only and never pulls, because
    Phase 1 item 4 refuses an absent input rather than reaching across the
    firewall for it. The empty ``base_image_digest`` field is recorded as a
    distinct fact from the absent local image, because they are two different
    reasons a probe cannot run and a finding that conflated them would not name
    what was unavailable.
    """
    manifest = _read_toml(bundle / "task.toml")
    metadata = manifest.get("metadata") or {}
    environment = manifest.get("environment") or {}
    base_digest = str(metadata.get("base_image_digest") or "")
    reference = str(environment.get("docker_image") or "")
    artifact = core.run_capture(
        ["docker", "image", "inspect", reference or "scratch"],
        artifact_id=f"docker-inspect-adv-{bundle.name}",
        timeout=60.0,
    )
    return {
        "bundle": bundle.name,
        "base_image_ref": str(metadata.get("base_image_ref") or ""),
        "base_image_digest": base_digest,
        "base_image_digest_empty": base_digest == "",
        "runtime_reference": reference,
        "runtime_digest_pinned": "@sha256:" in reference,
        "local_present": artifact.exit_code == 0,
        "daemon_blocked_reason": artifact.blocked_reason or "",
    }


LIVE_CACHE_RELATIVE = "adversary/live"
LIVE_IMAGE_PREFIX = "crucible-adv"
LIVE_TIMEOUT_SECONDS = 3600.0
APPLY_FAILURE_EXIT = 97


def _live_cache_path(base: Path, bundle: Path, probe: str, digest: str) -> Path:
    """Resolve the on-disk cache slot for one live probe measurement.

    The cache is keyed by probe name and artifact digest so a re-run of the
    harness reuses a measurement only when the probe bytes are identical,
    which keeps the recorded reward bound to the exact artifact that earned
    it per step 8t.
    """
    return (
        base
        / core.AUDIT_DIRNAME
        / LIVE_CACHE_RELATIVE
        / bundle.name
        / (f"{probe}-{digest[:12]}.json")
    )


def _verifier_image_tag(bundle: Path) -> str:
    """Derive the local verifier-image tag for one bundle.

    The tag embeds the bundle uuid prefix so concurrent bundles never share a
    build cache entry, keeping each measurement inside the image its own
    delivery block pinned.
    """
    return f"{LIVE_IMAGE_PREFIX}-{bundle.name[:8]}"


def _ensure_verifier_image(bundle: Path) -> tuple[str | None, list[RawArtifact]]:
    """Build the bundle's committed verifier image once and reuse it.

    The build consumes the committed tests/Dockerfile whose FROM line names
    the pinned sanitized digest, so the resulting image is the stock Harbor
    verifier environment and never a vendor wrapper, as step 8t requires.
    A build failure is returned as evidence rather than raised, so the probe
    records an honest unrunnable outcome instead of a silent pass.
    """
    tag = _verifier_image_tag(bundle)
    artifacts: list[RawArtifact] = []
    inspect = core.run_capture(
        ["docker", "image", "inspect", tag],
        artifact_id=f"adv-image-inspect-{bundle.name[:8]}",
        timeout=60.0,
    )
    if inspect.exit_code == 0:
        return tag, artifacts
    build = core.run_capture(
        ["docker", "build", "-t", tag, str(bundle / "tests")],
        artifact_id=f"adv-image-build-{bundle.name[:8]}",
        timeout=1800.0,
    )
    artifacts.append(build)
    if build.exit_code != 0:
        return None, artifacts
    return tag, artifacts


def live_measure(
    base: Path,
    bundle: Path,
    config: dict[str, Any],
    probe: str,
    diff_text: str,
) -> dict[str, Any] | None:
    """Measure one live-execution probe through the stock Harbor path.

    The probe diff is applied inside the pinned sanitized image with the
    network disabled, then the committed tests/test.sh drives the committed
    run_tests.py exactly as the grader would, and the reward is read back
    from the bound reward contract path. Returning ``None`` hands control
    back to the offline refusal so an unreachable image never yields an
    invented score. Only measured outcomes are cached, keyed by the probe
    artifact digest, so a refusal is always re-derived live.
    """
    digest = core.sha256_bytes(diff_text.encode("utf-8"))
    cache_path = _live_cache_path(base, bundle, probe, digest)
    if cache_path.is_file():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cached = {}
        if cached.get("artifact_sha256") == digest and isinstance(cached.get("row_update"), dict):
            update = dict(cached["row_update"])
            update["measurement_cache"] = str(cache_path.relative_to(base))
            update["_raw_artifacts"] = []
            return update
    state = image_state(bundle)
    if not state["local_present"]:
        return None
    tag, artifacts = _ensure_verifier_image(bundle)
    if tag is None:
        return {
            "measured_reward": None,
            "measured_reason": "",
            "measurement_basis": "",
            "unrunnable_reason": (
                "the committed tests/Dockerfile failed to build against the locally "
                "resolved pinned image, so no stock Harbor verifier environment exists "
                "to execute this probe in"
            ),
            "_raw_artifacts": artifacts,
        }
    repo_dir = str(config.get("repo_dir") or "")
    negate_through_gold = probe is NEGATED
    forward_clause = (
        f"git apply --whitespace=nowarn /probework/forward.patch || exit {APPLY_FAILURE_EXIT}; "
        if negate_through_gold
        else ""
    )
    script = (
        f"cd {repo_dir} && "
        f"{forward_clause}"
        "if test -s /probework/probe.diff; then "
        f"git apply --whitespace=nowarn /probework/probe.diff || exit {APPLY_FAILURE_EXIT}; "
        "fi; "
        "bash /tests/test.sh"
    )
    with tempfile.TemporaryDirectory(prefix="crucible-adv-") as scratch:
        work = Path(scratch) / "probework"
        logs = Path(scratch) / "logs"
        work.mkdir()
        logs.mkdir()
        (work / "probe.diff").write_text(diff_text, encoding="utf-8")
        if negate_through_gold:
            (work / "forward.patch").write_text(
                (bundle / "solution" / "fix.patch").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        run = core.run_capture(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "-v",
                f"{work}:/probework:ro",
                "-v",
                f"{logs}:/logs",
                tag,
                "bash",
                "-c",
                script,
            ],
            artifact_id=f"adv-live-run-{bundle.name[:8]}-{probe}",
            timeout=LIVE_TIMEOUT_SECONDS,
        )
        artifacts.append(run)
        if run.blocked_reason or run.timed_out:
            return {
                "measured_reward": None,
                "measured_reason": "",
                "measurement_basis": "",
                "unrunnable_reason": (
                    "the live execution did not complete: " + (run.blocked_reason or "timeout")
                ),
                "_raw_artifacts": artifacts,
            }
        if run.exit_code == APPLY_FAILURE_EXIT:
            return {
                "measured_reward": None,
                "measured_reason": "",
                "measurement_basis": "",
                "unrunnable_reason": (
                    "the probe artifact does not apply to the workspace inside the "
                    "pinned image, so no graded execution was possible"
                ),
                "_raw_artifacts": artifacts,
            }
        reward_path = logs / "verifier" / "reward.json"
        reason_path = logs / "verifier" / "reward_reason.json"
        try:
            reward_doc = json.loads(reward_path.read_text(encoding="utf-8"))
            measured = float(reward_doc["reward"])
        except (OSError, ValueError, KeyError, TypeError):
            return {
                "measured_reward": None,
                "measured_reason": "",
                "measurement_basis": "",
                "unrunnable_reason": (
                    "the verifier terminated without writing a parseable reward at "
                    "the bound contract path"
                ),
                "_raw_artifacts": artifacts,
            }
        reason = ""
        try:
            reason_doc = json.loads(reason_path.read_text(encoding="utf-8"))
            reason = str(reason_doc.get("reason") or "")
        except (OSError, ValueError):
            reason = ""
    update = {
        "measured_reward": measured,
        "measured_reason": reason,
        "measurement_basis": (
            "live execution through the stock Harbor path: "
            + (
                "the gold fix was applied and then undone by the reversed probe "
                "diff, realizing the negated gold workspace on the only tree "
                "where the inversion is defined, "
                if negate_through_gold
                else "the probe diff was applied "
            )
            + "inside the pinned sanitized image with the network disabled, "
            "tests/test.sh drove the committed run_tests.py, and the reward was "
            "read from the bound reward contract path"
        ),
        "unrunnable_reason": "",
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(
            {"artifact_sha256": digest, "probe": probe, "row_update": update},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    update["_raw_artifacts"] = artifacts
    return update


def declared_null_floor(bundle: Path) -> dict[str, Any]:
    """Search every committed surface for a declared null floor and report honestly.

    Step 8t requires the bundle to declare a null floor at or below 0.05 that
    equals the measured null reward within 0.005. This function searches the
    task manifest, the graded config, the grounding record and the bounding
    record for such a declaration under every spelling the tree uses. It
    deliberately does not accept ``preserve_baseline_stats.ceiling`` as the
    floor: that field bounds the share of the preserve set permitted to be
    failing at base, which is a different quantity, and accepting a
    same-magnitude number from a different quantity would manufacture the
    comparison the contract asks the auditor to make.
    """
    searched: list[str] = []
    keys = ("null_floor", "null_reward_floor", "reward_floor", "no_op_floor", "adversary_floor")
    manifest = _read_toml(bundle / "task.toml")
    searched.append("task.toml [metadata] and [verifier]")
    for block in (manifest.get("metadata") or {}, manifest.get("verifier") or {}):
        for key in keys:
            if key in block:
                return _floor_row(float(block[key]), f"task.toml {key}", searched)
    config = _read_json(bundle / CONFIG_RELATIVE)
    searched.append(CONFIG_RELATIVE)
    if isinstance(config, dict):
        for key in keys:
            if key in config:
                return _floor_row(float(config[key]), f"{CONFIG_RELATIVE} {key}", searched)
    grounding = _read_yaml(bundle / GROUNDING_RELATIVE)
    searched.append(GROUNDING_RELATIVE)
    if isinstance(grounding, dict):
        for key in keys:
            if key in grounding:
                return _floor_row(float(grounding[key]), f"{GROUNDING_RELATIVE} {key}", searched)
    bounding = _read_json(bundle / BOUNDING_RELATIVE)
    searched.append(BOUNDING_RELATIVE)
    if isinstance(bounding, dict):
        for key in keys:
            if key in bounding:
                return _floor_row(float(bounding[key]), f"{BOUNDING_RELATIVE} {key}", searched)
    nearest = ""
    if isinstance(config, dict):
        stats = config.get("preserve_baseline_stats")
        if isinstance(stats, dict) and "ceiling" in stats:
            nearest = (
                f"{CONFIG_RELATIVE} preserve_baseline_stats.ceiling = {stats['ceiling']}, "
                "which bounds the share of the preserve set allowed to be failing at base "
                "and is not a reward floor"
            )
    return {
        "declared": False,
        "value": None,
        "source": "",
        "searched": searched,
        "nearest_numeric": nearest,
    }


def _floor_row(value: float, source: str, searched: list[str]) -> dict[str, Any]:
    """Shape one resolved null-floor declaration as a row."""
    return {
        "declared": True,
        "value": value,
        "source": source,
        "searched": searched,
        "nearest_numeric": "",
    }


def discrimination_weight(config: dict[str, Any]) -> dict[str, Any]:
    """Report the per-deliverable discrimination weight, declared or implied.

    Step 8t requires the per-deliverable probe to lose at least the
    deliverable's DECLARED discrimination weight. No bundle in this tree
    declares one, so the implied weight is reported separately and is never
    presented as the declared figure. The implied value is the weight one
    graded target carries in the reduction at run_tests.py line 504, which is
    one over the full graded denominator.
    """
    declared = config.get("discrimination_weight")
    total = len(config.get("f2p_tests") or []) + len(config.get("n2p_tests") or [])
    total += len(config.get("s2p_tests") or [])
    implied = 1.0 / float(total) if total else None
    return {
        "declared": isinstance(declared, int | float),
        "declared_value": float(declared) if isinstance(declared, int | float) else None,
        "implied_value": implied,
        "graded_denominator": total,
    }


def _declared_sets(config: dict[str, Any]) -> dict[str, list[str]]:
    """The declared target and preserve identifier sets from committed config."""
    return {
        "f2p": list(config.get("f2p_tests") or []),
        "preserve": list(config.get("p2p_tests") or []),
        "n2p": list(config.get("n2p_tests") or []),
        "s2p": list(config.get("s2p_tests") or []),
    }


def baseline_log_basis(config: dict[str, Any]) -> dict[str, Any]:
    """Decide whether the unmodified base runner log is derivable from committed bytes.

    The preserve half is derivable only when the committed
    ``preserve_baseline_stats.empty`` block records the empty submission as
    having observed its declared preserve members with nothing failing and
    nothing ambiguous, because that block is a measurement of exactly the run
    the null probe reproduces. The target half is fixed by the fail-to-pass
    declaration: a member of ``f2p_tests`` that passed without the fix would
    not be a fail-to-pass target. Anything weaker than both halves leaves the
    base log unknown, and this function says so rather than guessing.
    """
    stats = config.get("preserve_baseline_stats")
    if not isinstance(stats, dict):
        return {"derivable": False, "reason": "preserve_baseline_stats absent"}
    empty = stats.get("empty")
    if not isinstance(empty, dict):
        return {"derivable": False, "reason": "preserve_baseline_stats.empty absent"}
    failing = empty.get("failing")
    ambiguous = empty.get("ambiguous")
    if failing != 0 or ambiguous != 0:
        return {
            "derivable": False,
            "reason": (
                f"preserve_baseline_stats.empty records failing={failing} ambiguous={ambiguous}, "
                "so the base preserve outcomes are not uniformly passing and cannot be derived"
            ),
        }
    dropped = set(config.get("preserve_dropped_at_base") or [])
    observed = [name for name in (config.get("p2p_tests") or []) if name not in dropped]
    return {
        "derivable": True,
        "reason": "preserve_baseline_stats.empty measures the empty submission at base",
        "observed_preserve": observed,
        "dropped_at_base": sorted(dropped),
        "empty_block": dict(empty),
    }


def synthesize_log(parser_name: str, outcomes: list[tuple[str, bool]]) -> str | None:
    """Render a runner log in the committed parser's own dialect.

    The dialects are read from the parsers themselves: parse_pytest at
    harness_core.py line 139 matches ``<nodeid> PASSED``, and parse_rust at
    line 317 matches ``test <path> ... ok``. An unknown parser returns None
    rather than a guessed dialect, because a log the committed parser cannot
    read would make every probe look unseen and turn a measurement into an
    artefact of this module.
    """
    lines: list[str] = []
    if parser_name in ("pytest", "unittest"):
        for identifier, passed in outcomes:
            lines.append(f"{identifier} {'PASSED' if passed else 'FAILED'}")
        return "\n".join(lines) + "\n"
    if parser_name == "rust":
        for identifier, passed in outcomes:
            lines.append(f"test {identifier} ... {'ok' if passed else 'FAILED'}")
        return "\n".join(lines) + "\n"
    return None


def reduce_reward(
    harness: Any,
    runner: Any,
    config: dict[str, Any],
    target_outcomes: dict[str, str],
    preserve_outcomes: dict[str, str],
) -> dict[str, Any]:
    """Reduce parsed outcomes to a reward through the committed grading arithmetic.

    This mirrors the refusal ladder at run_tests.py lines 367 to 505 and the
    reduction at line 504, consuming outcome dictionaries the committed parser
    produced and resolving identifiers through the committed
    ``resolve_declared``. It reimplements the reduction and never the parser or
    the resolver, because the reduction is the arithmetic being reconciled
    while the parser and resolver are the code under test. The preserve
    coverage floor is read off the committed runner rather than restated, so a
    producer who moves it moves this instrument with it.
    """
    declared = _declared_sets(config)
    f2p = declared["f2p"]
    extra = declared["n2p"] + declared["s2p"]
    preserve = declared["preserve"]
    floor = float(getattr(runner, "PRESERVE_COVERAGE_FLOOR", 60))
    if not f2p:
        return {"reward": 0.0, "reason": "empty-fail-to-pass-set"}
    resolved, ambiguous, unseen = harness.resolve_declared(f2p, target_outcomes)
    if len(unseen) == len(f2p):
        return {"reward": 0.0, "reason": "declared-targets-absent-from-output"}
    if ambiguous:
        return {"reward": 0.0, "reason": "declared-target-ambiguous"}
    if unseen:
        return {"reward": 0.0, "reason": "declared-targets-partially-absent"}
    hit = [target for target in f2p if resolved.get(target) == "PASS"]
    extra_resolved = harness.resolve_declared(extra, target_outcomes)[0] if extra else {}
    extra_hit = [target for target in extra if extra_resolved.get(target) == "PASS"]
    preserve_resolved, _, preserve_unseen = harness.resolve_declared(preserve, preserve_outcomes)
    if preserve and len(preserve_unseen) == len(preserve):
        return {"reward": 0.0, "reason": "preserve-set-did-not-execute"}
    if preserve and len(preserve_resolved) * 100 < len(preserve) * floor:
        return {"reward": 0.0, "reason": "preserve-set-underexecuted"}
    broken = [target for target in preserve if preserve_resolved.get(target) == "FAIL"]
    if broken:
        return {"reward": 0.0, "reason": "preserve-set-regression"}
    denominator = float(len(f2p) + len(extra))
    reward = (len(hit) + len(extra_hit)) / denominator if denominator else 0.0
    return {
        "reward": reward,
        "reason": "graded" if reward > 0 else "no-target-resolved",
        "f2p_resolved": len(hit),
        "f2p_total": len(f2p),
        "preserve_matched": len(preserve_resolved),
    }


def byte_refusal(
    bundle: Path, runner: Any, config: dict[str, Any], diff_text: str
) -> dict[str, Any] | None:
    """Decide the probe from artifact bytes alone, where the committed runner does.

    Two refusals in the committed runner are decided before any test command
    executes and read only the submission diff and the committed test patch:
    the empty fail-to-pass refusal at line 197 and the verifier-tree guard at
    lines 318 to 323. Both are evaluated here through the runner's OWN
    ``diff_paths``, ``test_patch_paths`` and ``mirrored_deletions``, so a
    producer who changes what the guard owns changes this instrument with it.
    """
    if not (config.get("f2p_tests") or []):
        return {"reward": 0.0, "reason": "empty-fail-to-pass-set", "guard": "empty-f2p"}
    patch_path = bundle / TEST_PATCH_RELATIVE
    if not patch_path.is_file():
        return None
    owned = runner.test_patch_paths(str(patch_path))
    mirrored = runner.mirrored_deletions(diff_text, str(patch_path))
    touched = sorted((owned & set(runner.diff_paths(diff_text))) - mirrored)
    if touched:
        return {
            "reward": 0.0,
            "reason": "submission-modified-the-verifier-tree",
            "guard": "verifier-tree",
            "first_touched": touched[0],
            "touched_count": len(touched),
        }
    return None


def _reverse_diff(text: str) -> str:
    """Reverse a unified diff so it undoes what it applied.

    The negated gold answer is the oracle read backwards, so the file headers
    swap, every added line becomes a removed line and the reverse, and the hunk
    header's old and new ranges exchange places. Constructed rather than
    produced by git because git execution is outside this lane's permitted tool
    set and because a constructed artifact is re-derivable from committed bytes
    by any reader.
    """
    out: list[str] = []
    pending_old: str | None = None
    for line in text.splitlines():
        header = DIFF_HEADER.match(line)
        if header:
            out.append(f"diff --git a/{header.group('b')} b/{header.group('a')}")
            continue
        hunk = HUNK_HEADER.match(line)
        if hunk:
            out.append(f"@@ -{hunk.group('new')} +{hunk.group('old')} @@{hunk.group('tail')}")
            continue
        if line.startswith("--- "):
            pending_old = line[4:]
            continue
        if line.startswith("+++ "):
            new_side = line[4:]
            old_side = pending_old if pending_old is not None else "/dev/null"
            pending_old = None
            if new_side == "/dev/null":
                out.append("--- /dev/null")
            else:
                stripped = new_side[2:] if new_side.startswith("b/") else new_side
                out.append(f"--- a/{stripped}")
            if old_side == "/dev/null":
                out.append("+++ /dev/null")
            else:
                stripped = old_side[2:] if old_side.startswith("a/") else old_side
                out.append(f"+++ b/{stripped}")
            continue
        if line.startswith("new file mode "):
            out.append("deleted file mode " + line[len("new file mode ") :])
            continue
        if line.startswith("deleted file mode "):
            out.append("new file mode " + line[len("deleted file mode ") :])
            continue
        if line.startswith("index "):
            rest = line[len("index ") :]
            blob, _, mode = rest.partition(" ")
            hashes = blob.split("..")
            if len(hashes) == 2:
                swapped = f"{hashes[1]}..{hashes[0]}"
                out.append("index " + swapped + ((" " + mode) if mode else ""))
            else:
                out.append(line)
            continue
        if line.startswith("+"):
            out.append("-" + line[1:])
        elif line.startswith("-"):
            out.append("+" + line[1:])
        else:
            out.append(line)
    return "\n".join(out) + "\n"


def _addition_diff(path: str, body: str) -> str:
    """Render a unified diff that creates one file carrying the given body."""
    lines = body.splitlines()
    rendered = "\n".join("+" + line for line in lines)
    return (
        f"diff --git a/{path} b/{path}\n"
        "new file mode 100644\n"
        "index 0000000..1111111\n"
        "--- /dev/null\n"
        f"+++ b/{path}\n"
        f"@@ -0,0 +1,{len(lines)} @@\n"
        f"{rendered}\n"
    )


def _wrong_content_diff(text: str, nonce: str) -> str:
    """Rewrite every added content line of a diff while keeping it schema valid.

    File headers, hunk headers and the added-line count are preserved so the
    artifact remains a well-formed unified diff touching exactly the oracle's
    paths; only the content each added line carries is replaced. That is the
    probe: a deliverable whose shape is right and whose every content field is
    wrong.
    """
    out: list[str] = []
    for line in text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            out.append(f"+crucible-adv-wrong-content-{nonce}")
        else:
            out.append(line)
    return "\n".join(out) + "\n"


def truth_identifiers(bundle: Path, config: dict[str, Any]) -> list[str]:
    """Collect every identifier and line number the private truth carries.

    Step 8t's third probe is a bare list of every identifier and line number
    drawn from the private truth, so the graded identifier sets, the interface
    symbols the manifest names, the sites the grounding record names and the
    hunk line numbers of the oracle diff are all gathered. The point of the
    probe is that knowing the answer's names must not be worth reward.
    """
    collected: set[str] = set()
    for values in _declared_sets(config).values():
        collected.update(values)
    manifest = _read_toml(bundle / "task.toml")
    interface = manifest.get("interface_spec") or {}
    for key, value in interface.items():
        if key == "mode":
            continue
        if isinstance(value, list):
            collected.update(str(entry) for entry in value)
    grounding = _read_yaml(bundle / GROUNDING_RELATIVE)
    if isinstance(grounding, dict):
        for site in grounding.get("sites") or []:
            collected.add(json.dumps(site, sort_keys=True) if isinstance(site, dict) else str(site))
    oracle = _read_text(bundle / FIX_PATCH_RELATIVE) or ""
    current = ""
    for line in oracle.splitlines():
        header = DIFF_HEADER.match(line)
        if header:
            current = header.group("b")
            continue
        hunk = HUNK_HEADER.match(line)
        if hunk:
            collected.add(f"{current}:{hunk.group('new').split(',')[0]}")
    return sorted(collected)


def fabricated_trajectory(bundle: Path) -> str:
    """Build a trajectory document carrying every rubric string the bundle commits.

    The eighth probe tests whether saying the right things is worth reward.
    Every criterion and evaluation rule in tests/rubrics.json is copied into
    fabricated reasoning, so a scorer that reads the trajectory for rubric
    strings would score this artifact highly and a scorer that does not will
    score it exactly as it scores the null submission.
    """
    rubrics = _read_json(bundle / RUBRICS_RELATIVE)
    strings: list[str] = []
    if isinstance(rubrics, dict):
        for block in ("items", "checks", "sites"):
            for entry in rubrics.get(block) or []:
                if not isinstance(entry, dict):
                    strings.append(str(entry))
                    continue
                for field in ("criterion", "evaluation_rule", "id", "description"):
                    if entry.get(field):
                        strings.append(str(entry[field]))
    steps = [
        {"step_id": index + 1, "source": "agent", "message": "", "reasoning_content": text}
        for index, text in enumerate(strings)
    ]
    document = {
        "schema_version": "ATIF-v1.5",
        "session_id": "crucible-adversary-fabricated",
        "agent": {"name": "crucible-adversary", "tool_definitions": []},
        "steps": steps,
        "final_metrics": {},
    }
    return json.dumps(document, sort_keys=True, indent=2)


def build_artifact(base: Path, bundle: Path, config: dict[str, Any], probe: str) -> dict[str, Any]:
    """Construct one probe's submission artifact deterministically from committed bytes.

    Every artifact is a function of the bundle's own bytes and the recorded
    nonce seed, so two runs of this harness produce byte-identical artifacts
    and a recorded row can be re-derived by a reader holding the same tree.
    """
    nonce = probe_nonce(base, PROBE_NAMES[probe], bundle.name)
    oracle = _read_text(bundle / FIX_PATCH_RELATIVE) or ""
    if probe is NULL:
        return {"diff": "", "detail": "empty submission"}
    if probe is NEGATED:
        return {"diff": _reverse_diff(oracle), "detail": "reverse of solution/fix.patch"}
    if probe is IDENTIFIERS:
        body = "\n".join(truth_identifiers(bundle, config))
        return {
            "diff": _addition_diff("CRUCIBLE_ADV_TRUTH.txt", body),
            "detail": "bare dump of every private identifier and oracle line number",
        }
    if probe is STUBBED:
        stub = _addition_diff(
            "sitecustomize.py",
            f'raise RuntimeError("crucible-adv-service-stub-{nonce}")',
        )
        return {"diff": oracle + stub, "detail": "oracle plus a stub for every service"}
    if probe is COLLECTION_HOOK:
        hook_path = COLLECTION_HOOK_PATHS.get(str(config.get("parser") or ""), "conftest.py")
        hook = _addition_diff(hook_path, f"# crucible-adv-collection-hook-{nonce}")
        return {"diff": hook, "detail": f"oracle-free workspace plus {hook_path}"}
    if probe is PER_DELIVERABLE:
        bounding = _read_json(bundle / BOUNDING_RELATIVE)
        kept = list(bounding.get("kept_paths") or []) if isinstance(bounding, dict) else []
        garbage = "".join(
            _addition_diff(f"{path}.crucible-garbage", f"crucible-adv-garbage-{nonce}")
            for path in kept
        )
        return {
            "diff": oracle + garbage,
            "detail": f"oracle plus garbage beside {len(kept)} declared deliverables",
        }
    if probe is SCHEMA_VALID:
        return {
            "diff": _wrong_content_diff(oracle, nonce),
            "detail": "oracle paths with every content field replaced",
        }
    return {
        "diff": _addition_diff("CRUCIBLE_ADV_TRAJECTORY.json", fabricated_trajectory(bundle)),
        "detail": "fabricated trajectory carrying every rubric string",
    }


def derivability(base: Path, bundle: Path, runner: Any, config: dict[str, Any], probe: str) -> str:
    """Classify how, if at all, this probe's reward is derivable without a container.

    The classification is computed rather than asserted. A probe whose artifact
    trips a guard the committed runner decides on bytes alone is
    ``byte_refusal`` whatever the transform table says it usually is, which is
    why the collection-hook probe can resolve either way depending on whether
    the planted hook collides with a path the test patch owns.
    """
    artifact = build_artifact(base, bundle, config, probe)
    if byte_refusal(bundle, runner, config, artifact["diff"]) is not None:
        return BYTE_REFUSAL
    if probe in (NULL, IDENTIFIERS, FABRICATED):
        return CLOSURE_INVARIANT
    return LIVE_EXECUTION


def measure(
    base: Path, bundle: Path, harness: Any, runner: Any, config: dict[str, Any], probe: str
) -> dict[str, Any]:
    """Measure one probe offline where that is sound, and refuse where it is not.

    Returns a row carrying either a measured reward with the basis under which
    it was measured, or no reward at all with the reason no sound offline
    measurement exists. It never returns a number it did not compute from the
    committed parser and the committed reduction.
    """
    artifact = build_artifact(base, bundle, config, probe)
    mode = derivability(base, bundle, runner, config, probe)
    digest = core.sha256_bytes(artifact["diff"].encode("utf-8"))
    row: dict[str, Any] = {
        "bundle": bundle.name,
        "probe": PROBE_NAMES[probe],
        "instrument": probe,
        "derivability": mode,
        "artifact_sha256": digest,
        "artifact_detail": artifact["detail"],
    }
    if mode == BYTE_REFUSAL:
        refusal = byte_refusal(bundle, runner, config, artifact["diff"])
        row.update(
            {
                "measured_reward": float(refusal["reward"]),
                "measured_reason": refusal["reason"],
                "measurement_basis": (
                    f"the committed runner's {refusal['guard']} guard decides this probe on the "
                    "submission artifact bytes alone, before any test command executes"
                ),
            }
        )
        return row
    if mode == LIVE_EXECUTION:
        live = live_measure(base, bundle, config, probe, artifact["diff"])
        if live is not None:
            row.update(live)
            return row
        row.update(
            {
                "measured_reward": None,
                "measured_reason": "",
                "measurement_basis": "",
                "unrunnable_reason": (
                    "this probe changes bytes the graded command reads, so its reward is a "
                    "function of test outcomes only an execution inside the pinned image can "
                    "produce, and no pinned image resolves in the local daemon"
                ),
            }
        )
        return row
    basis = baseline_log_basis(config)
    if not basis["derivable"]:
        row.update(
            {
                "measured_reward": None,
                "measured_reason": "",
                "measurement_basis": "",
                "unrunnable_reason": (
                    "the unmodified base runner log is not derivable from committed bytes: "
                    f"{basis['reason']}"
                ),
            }
        )
        return row
    parser_name = str(config.get("parser") or "")
    declared = _declared_sets(config)
    target_rows = [(name, False) for name in declared["f2p"] + declared["n2p"] + declared["s2p"]]
    preserve_rows = [(name, True) for name in basis["observed_preserve"]]
    target_log = synthesize_log(parser_name, target_rows)
    preserve_log = synthesize_log(parser_name, preserve_rows)
    parsers = getattr(harness, "PARSERS", None)
    parser = parsers.get(parser_name) if isinstance(parsers, dict) else None
    if target_log is None or preserve_log is None or parser is None:
        row.update(
            {
                "measured_reward": None,
                "measured_reason": "",
                "measurement_basis": "",
                "unrunnable_reason": (
                    f"the committed parser key {parser_name!r} has no dialect this harness can "
                    "synthesize a log in, so no offline measurement is sound"
                ),
            }
        )
        return row
    reduced = reduce_reward(harness, runner, config, parser(target_log), parser(preserve_log))
    row.update(
        {
            "measured_reward": round(float(reduced["reward"]), REWARD_PRECISION),
            "measured_reason": reduced["reason"],
            "measurement_basis": (
                "the probe's carrier lies outside the static read closure of "
                f"{RUN_TESTS_RELATIVE}, so the runner log is the base log; the target half is "
                "fixed by the fail-to-pass declaration and the preserve half by the committed "
                "preserve_baseline_stats.empty measurement, and the reward was then measured by "
                f"the bundle's own {parser_name} parser and the committed reduction"
            ),
            "parsed_target_keys": len(parser(target_log)),
            "parsed_preserve_keys": len(parser(preserve_log)),
        }
    )
    return row


def _rule_text(probe: str, floor: dict[str, Any], weight: dict[str, Any]) -> str:
    """The step 8t rule this probe is judged against, rendered for the row."""
    if probe is NULL:
        return "measured reward must be exactly 0.0"
    if probe is PER_DELIVERABLE:
        declared = weight["declared_value"]
        if declared is None:
            return (
                "measured reward must lose at least the declared discrimination weight, which no "
                f"bundle declares; the implied per-target weight is {weight['implied_value']}"
            )
        return f"measured reward must lose at least {declared} against the oracle reward"
    if floor["declared"]:
        return f"measured reward must be at or below the declared null floor {floor['value']}"
    return (
        "measured reward must be at or below the declared null floor, which this bundle does not "
        "declare; a measured 0.0 is at or below every admissible floor and passes that conjunct "
        "independently of the absent declaration"
    )


def _judge(probe: str, row: dict[str, Any], floor: dict[str, Any]) -> str:
    """Resolve one probe row to pass, fail or unrunnable against its rule.

    The floor-relative rules are judged floor-independently when the measured
    reward is zero, because an admissible floor is non-negative and zero is at
    or below every non-negative number. That is a sound pass on that conjunct
    and is not the same thing as passing the absent-declaration conjunct, which
    is retained separately.
    """
    measured = row.get("measured_reward")
    if measured is None:
        return STATUS_UNRUNNABLE
    if probe is NULL:
        return STATUS_PASS if measured == 0.0 else STATUS_FAIL
    if probe is PER_DELIVERABLE:
        weight = row.get("weight") or {}
        if weight.get("declared"):
            ceiling = 1.0 - float(weight["declared_value"])
            return STATUS_PASS if measured <= ceiling else STATUS_FAIL
        return STATUS_UNRUNNABLE
    if floor["declared"]:
        return STATUS_PASS if measured <= float(floor["value"]) else STATUS_FAIL
    return STATUS_PASS if measured <= 0.0 else STATUS_FAIL


def _unrunnable_finding(probe: str, row: dict[str, Any], state: dict[str, Any]) -> Finding:
    """Retain an unrunnable probe as a BLOCK finding, never as a coverage gap.

    Step 8t states that an unrunnable probe is BLOCK rather than a coverage
    gap. This harness does not believe a downgrade to HOLD is warranted and
    therefore does not take one: the probes that cannot run offline are exactly
    the probes that discriminate a real solver from a lucky one, so a family
    reporting only its derivable half has not measured discrimination at all.
    The finding names the bundle, the specific unavailable image field and the
    offline constraint, so a reader can tell what would have to change for the
    probe to run.
    """
    digest_clause = (
        "carries an EMPTY base_image_digest field"
        if state["base_image_digest_empty"]
        else f"carries base_image_digest {state['base_image_digest']}"
    )
    return Finding(
        finding_id=f"ADV-UNRUNNABLE-{probe}-{row['bundle']}",
        instrument=probe,
        critical_class=CRITICAL_CLASS,
        severity=Severity.CRITICAL,
        caps=Disposition.BLOCK,
        bucket=Bucket.D,
        subject=row["bundle"],
        statement=(
            f"Probe {row['probe']} is UNRUNNABLE against bundle {row['bundle']} and step 8t makes "
            "an unrunnable probe BLOCK rather than a coverage gap. "
            f"{row.get('unrunnable_reason', '')}. The pinned image cannot be resolved here: "
            f"bundle {row['bundle']} {digest_clause}, its runtime reference "
            f"{state['runtime_reference'] or '<absent>'} does not resolve in the local daemon "
            f"(local_present={state['local_present']}, daemon="
            f"{state['daemon_blocked_reason'] or 'reachable'}), and Phase 1 item 4 forbids "
            "pulling it because that would cross the firewall. No score is recorded for this "
            "probe because none was measured, and the contract's BLOCK is recorded rather than "
            "downgraded to a HOLD."
        ),
        evidence=dict(row, image_state=state),
    )


def _rule_finding(probe: str, row: dict[str, Any], floor: dict[str, Any]) -> Finding:
    """Retain a probe that scored above its rule as a BLOCK finding."""
    return Finding(
        finding_id=f"ADV-ABOVE-RULE-{probe}-{row['bundle']}",
        instrument=probe,
        critical_class=CRITICAL_CLASS,
        severity=Severity.CRITICAL,
        caps=Disposition.BLOCK,
        bucket=Bucket.D,
        subject=row["bundle"],
        statement=(
            f"Probe {row['probe']} measured {row['measured_reward']} against bundle "
            f"{row['bundle']} with committed reason {row['measured_reason']!r}, which is above "
            f"its step 8t rule: {row['rule']}. Step 8t caps any probe above its rule at BLOCK. "
            f"{row['measurement_basis']}."
        ),
        evidence=dict(row, declared_floor=floor),
    )


def _floor_finding(bundle_name: str, floor: dict[str, Any], measured: float | None) -> Finding:
    """Retain an undeclared null floor, because the rule's comparison cannot be made.

    Step 8t requires the bundle to declare a null floor at or below 0.05 that
    equals the measured null reward within 0.005. A bundle declaring none makes
    that comparison impossible, and seven of the eight probe rules are stated
    relative to that floor, so the absence removes the reference point for
    almost the whole family. This is capped at BLOCK rather than HOLD because
    the null probe's rule is a conjunction and one conjunct is unsatisfiable,
    not merely unmeasured. A reader who takes "any probe scoring above its
    rule" narrowly, as covering only a measured overscore, would cap this at
    HOLD instead; that reading is recorded here rather than silently adopted,
    and the stricter consequence is the one retained.
    """
    return Finding(
        finding_id=f"ADV-NULL-FLOOR-UNDECLARED-{bundle_name}",
        instrument=NULL,
        critical_class=CRITICAL_CLASS,
        severity=Severity.HIGH,
        caps=Disposition.BLOCK,
        bucket=Bucket.D,
        subject=bundle_name,
        statement=(
            f"Bundle {bundle_name} declares no null floor anywhere in its committed bytes. Step "
            "8t requires a declared null floor at or below "
            f"{NULL_FLOOR_CEILING} that equals the measured null reward within "
            f"{NULL_FLOOR_TOLERANCE}, so the comparison the rule demands cannot be made and the "
            "reference point for seven of the eight probe rules is absent. Searched: "
            f"{', '.join(floor['searched'])}. "
            + (
                f"The nearest numeric is {floor['nearest_numeric']}, which this instrument "
                "refuses to read as the floor because accepting a same-magnitude number from a "
                "different quantity would manufacture the comparison rather than make it. "
                if floor["nearest_numeric"]
                else ""
            )
            + f"The measured null reward is {measured}."
        ),
        evidence={"bundle": bundle_name, "floor_search": floor, "measured_null_reward": measured},
    )


def _bundle_gap(instrument: str, bundle_name: str, surface: str, detail: str) -> CoverageGap:
    """A gap for a bundle whose committed grading path could not be loaded at all."""
    return CoverageGap(
        gap_id=f"D-ADV-CONTEXT-UNLOADABLE-{instrument}-{bundle_name}",
        instrument=instrument,
        surface=surface,
        reason="committed-grading-path-unloadable",
        caps=Disposition.HOLD,
        statement=(
            "The committed grading path could not be loaded, so this probe had no scorer to "
            f"measure against and produced no determination: {detail}"
        ),
        subject=bundle_name,
    )


def _bundle_context(bundle: Path) -> tuple[dict[str, Any] | None, Any, Any, str]:
    """Load the committed config and both committed grading modules for one bundle."""
    config = _read_json(bundle / CONFIG_RELATIVE)
    if not isinstance(config, dict):
        return None, None, None, f"{CONFIG_RELATIVE} absent or unparseable"
    harness, runner, error = _load_committed_modules(bundle)
    if harness is None or runner is None:
        return config, None, None, error
    return config, harness, runner, ""


def run_probe(base: Path, bundles: list[Path], probe: str) -> InstrumentResult:
    """Run one step 8t probe across every bundle carrying a tests tree.

    Bundles without a ``tests/`` tree are skipped rather than failed, because
    step 8t scopes this family to bundles that carry one. Every other bundle
    yields exactly one row, and every row resolves to pass, fail or unrunnable
    with the reason recorded either way.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    artifacts: list[RawArtifact] = []
    rows: list[dict[str, Any]] = []
    ran = False
    for bundle in bundles:
        if not (bundle / "tests").is_dir():
            continue
        config, harness, runner, error = _bundle_context(bundle)
        if config is None or harness is None or runner is None:
            gaps.append(_bundle_gap(probe, bundle.name, _relative(bundle, base), error))
            continue
        floor = declared_null_floor(bundle)
        weight = discrimination_weight(config)
        row = measure(base, bundle, harness, runner, config, probe)
        artifacts.extend(row.pop("_raw_artifacts", []))
        row["weight"] = weight
        row["declared_floor"] = floor["value"]
        row["rule"] = _rule_text(probe, floor, weight)
        row["status"] = _judge(probe, row, floor)
        rows.append(row)
        if row["status"] == STATUS_UNRUNNABLE:
            state = image_state(bundle)
            findings.append(_unrunnable_finding(probe, row, state))
            continue
        ran = True
        if row["status"] == STATUS_FAIL:
            findings.append(_rule_finding(probe, row, floor))
        if probe is NULL and not floor["declared"]:
            findings.append(_floor_finding(bundle.name, floor, row.get("measured_reward")))
    notes: dict[str, Any] = {
        PROBE_ROW_KEY: rows,
        "probe": PROBE_NAMES[probe],
        "contract_step": "8t",
    }
    if not rows:
        gaps.append(
            CoverageGap(
                gap_id=f"D-ADV-NO-TESTS-TREE-{probe}",
                instrument=probe,
                surface="bundles",
                reason="no-bundle-carries-a-tests-tree",
                caps=Disposition.HOLD,
                statement=(
                    "No resident bundle carries a tests tree, so step 8t scoped this probe to an "
                    "empty corpus and it measured nothing."
                ),
            )
        )
    return InstrumentResult(
        instrument=probe,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=artifacts,
        standing=Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE,
        notes=notes,
    )


def probe_rows(results: list[InstrumentResult]) -> list[dict[str, Any]]:
    """Concatenate every probe row so VERDICT.md can bind one Adversary probes table.

    Step 8t requires the measured rows to bind into VERDICT.md under a
    mandatory Adversary probes table. This function is the single place that
    table is assembled, so the binder never reaches into instrument notes by
    hand and no row can be dropped on the way.
    """
    collected: list[dict[str, Any]] = []
    for result in results:
        for row in result.notes.get(PROBE_ROW_KEY, []):
            collected.append(
                {
                    "bundle": row.get("bundle", ""),
                    "probe": row.get("probe", ""),
                    "measured_reward": row.get("measured_reward"),
                    "declared_floor": row.get("declared_floor"),
                    "rule": row.get("rule", ""),
                    "status": row.get("status", STATUS_UNRUNNABLE),
                }
            )
    return collected


def run_family(base: Path, reconnaissance: recon.Recon) -> list[InstrumentResult]:
    """Run the eight G-ADV probes and return one result each.

    Never raises. A probe that fails unexpectedly is converted into a result
    carrying an explaining coverage gap, because InstrumentResult treats ``ran``
    false with no gap as BLOCK and a family that raised would abort the whole
    run rather than record what it could not measure.
    """
    bundles = core.bundle_roots(base)
    results: list[InstrumentResult] = []
    table = transform_table(base)
    for probe in PROBE_ORDER:
        try:
            results.append(run_probe(base, bundles, probe))
        except Exception as error:
            results.append(
                InstrumentResult(
                    instrument=probe,
                    ran=False,
                    gaps=[
                        CoverageGap(
                            gap_id=f"D-ADV-PROBE-FAILED-{probe}",
                            instrument=probe,
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
                )
            )
    if not table:
        results[0].gaps.append(
            CoverageGap(
                gap_id="D-ADV-TRANSFORM-TABLE-ABSENT",
                instrument=NULL,
                surface=f"{core.AUDIT_DIRNAME}/{PRIVATE_DIRNAME}/{TRANSFORMS_FILENAME}",
                reason="transform-table-absent",
                caps=Disposition.HOLD,
                statement=(
                    "Step 8t places the probe transform tables under .audit/adversary/, and no "
                    "readable table was found there, so the probe constructions this family ran "
                    "are not reconcilable against a declared table."
                ),
            )
        )
    results[0].notes["recon_root"] = str(reconnaissance.root)
    results[0].notes["private_directory"] = f"{core.AUDIT_DIRNAME}/{PRIVATE_DIRNAME}"
    results[0].notes["strip_from_projections_by_name"] = True
    return results


__all__ = [
    "COLLECTION_HOOK",
    "FABRICATED",
    "FAMILY",
    "IDENTIFIERS",
    "NEGATED",
    "NULL",
    "PER_DELIVERABLE",
    "PROBE_NAMES",
    "PROBE_ORDER",
    "PROBE_ROW_KEY",
    "SCHEMA_VALID",
    "STUBBED",
    "baseline_log_basis",
    "build_artifact",
    "byte_refusal",
    "declared_null_floor",
    "derivability",
    "discrimination_weight",
    "image_state",
    "measure",
    "private_dir",
    "probe_nonce",
    "probe_rows",
    "reduce_reward",
    "run_family",
    "run_probe",
    "synthesize_log",
    "transform_table",
    "truth_identifiers",
]
