"""DELIVERY-CONFORMANCE grounding instruments for contract step 8g.

This module implements the five members of the G-DEL family that step 8g names
explicitly, plus G-TRUTH-REGEN, which step 8g places in the same paragraph
because it is the only instrument in CRUCIBLE permitted to execute producer
code. The family re-derives delivery conformance from committed bundle bytes
alone. Every member is pure Bucket D: it may lower or cap a disposition and can
never raise one, so a clean result here is never evidence of correctness.

Member by member, and why each is shaped the way it is:

G-DEL-LAYOUT resolves every required Harbor path under all three lane roots plus
the verification root itself, confirms that no committed artifact sits at a path
the delivery format does not define, and reconciles declared steps against
on-disk step trees in both directions. The Harbor path vocabulary is restated
here as local constants rather than imported from trinity/tools/integrity.py,
because an instrument that imports the producer's own definition of correctness
cannot detect a producer that changed it. A step is a Harbor bundle step: the
format defines a ``steps/`` root beside ``environment/``, ``solution/`` and
``tests/``, and a manifest declares the steps that root must hold. Both
directions are computed as set relations so that a declared step with no tree
and a tree with no declaration are distinguishable rather than folded into one
count. The bundle-level artifact declaration in ``task.toml`` is reconciled
against each committed rollout's verifier tree on the same both-directions
footing, because an artifact the manifest declares and the committed evidence
does not carry is a declared path that does not exist.

G-DEL-DISJOINT re-derives task-lane residency across all three lane roots from
committed bytes. ``staging/``, ``samples/`` and ``delivery/`` are three disjoint
roots holding every bundle exactly once, a partition and not a curated copy, so
a uuid resident under two lane roots is a retained ``lane-overlap`` finding and
a uuid resident under ``staging/`` and a lane root is a retained
``staging-residue`` finding. At this verification root every bundle is a direct
child of the root itself and no lane root exists, so the partition holds
vacuously; the instrument still runs and records the derived residency map as
evidence, because a partition asserted without a derived map is a claim rather
than a measurement.

G-DEL-SCHEMA validates each task manifest against the schema version projected
through CRUCIBLE_VIEW as bound at sign-off. It never validates against whatever
schema version happens to be installed on this host: a locally installed
validator encodes the producer's current expectations, not the expectations the
sign-off bound, so consulting it would convert an unbound check into a
self-consistent one. When the projection does not carry the resident bundles,
the version is unprojected and the governing coverage gap fires.

G-DEL-PIN confirms that every container image reference carries an ``@sha256:``
digest and that the declared network policy matches the environment that
produced the committed evidence. Every reference the bundle commits is
enumerated: the manifest's base image reference and digest, the manifest's
runtime image, and every ``FROM`` instruction in both Dockerfiles. ``FROM
scratch`` and a reference naming an earlier build stage are excluded because
neither resolves against a registry.

G-DEL-REWARD confirms that the verifier terminates by writing the bound reward
contract path and that every committed zero score carries a machine-readable
reason. The bound path is read out of the committed verifier entry point rather
than assumed, and the pre-write of a zero before grading is checked because an
unwritten reward file is indistinguishable from a zero the grader never
computed.

G-TRUTH-REGEN re-runs the committed generator. This is the sole execution of
producer code anywhere in CRUCIBLE. The generator runs twice, under two sandbox
identities that differ in working directory, home directory, user name and
environment, and the two regenerated artifact sets must agree byte for byte,
because host-dependent output fingerprints the auditor. The kernel-reported
hostname and the real uid cannot be varied without privilege this harness does
not hold, so the identity variation is partial and says so in an explicit
coverage gap rather than claiming a full two-identity proof. Regeneration drift
against committed bytes, an unreconciled ground-truth step set and hand-edited
ground truth are each retained findings.

House rule: the rationale for every decision lives in these docstrings because
the contract is prompt-only, so the harness itself has to carry the reasoning as
audit evidence.
"""

from __future__ import annotations

import json
import re
import shutil
import tempfile
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

LANE_ROOT_NAMES: tuple[str, ...] = ("staging", "samples", "delivery")

HARBOR_BUNDLE_DIRS: tuple[str, ...] = ("environment", "solution", "steps", "tests")

TRINITY_BUNDLE_DIRS: tuple[str, ...] = ("trajectories",)

HARBOR_BUNDLE_FILES: tuple[str, ...] = ("instruction.md", "task.toml")

REQUIRED_BUNDLE_PATHS: tuple[str, ...] = (
    "environment/Dockerfile",
    "environment/sanitize-entrypoint.sh",
    "instruction.md",
    "solution/TRUTH.md",
    "solution/bounding.json",
    "solution/fix.patch",
    "solution/grounding.yaml",
    "solution/policy.yaml",
    "solution/provenance.yaml",
    "solution/recompute.py",
    "solution/rubrics.json",
    "solution/solve.sh",
    "solution/span_diff.patch",
    "task.toml",
    "tests/Dockerfile",
    "tests/config.json",
    "tests/graded/run.sh",
    "tests/harness_core.py",
    "tests/preserve.txt",
    "tests/rubrics.json",
    "tests/run_tests.py",
    "tests/test.patch",
    "tests/test.sh",
    "tests/test_output.py",
)

GENERATED_ARTIFACTS: tuple[str, ...] = (
    "solution/TRUTH.md",
    "solution/rubrics.json",
    "solution/solve.sh",
    "tests/test_output.py",
)

REWARD_CONTRACT_FILES: tuple[str, ...] = ("reward.json", "reward.txt", "reward_reason.json")

IMAGE_DIGEST = re.compile(r"@sha256:[0-9a-f]{64}")

DOCKER_FROM = re.compile(r"^\s*FROM\s+(\S+)", re.MULTILINE)

INVALID_ESCAPE = re.compile(r"invalid escape sequence.*")

RECORD_PROPERTY_REQUIREMENT = re.compile(r"E2-req:([^'\"]+)")

RECORD_PROPERTY_SITE = re.compile(r"E1-touched:([^'\"]+)")

REGEN_TIMEOUT_SECONDS = 300.0

IDENTITY_A: dict[str, str] = {
    "HOME": "/tmp/crucible-identity-alpha",
    "USER": "crucible-alpha",
    "LOGNAME": "crucible-alpha",
    "HOSTNAME": "crucible-alpha.invalid",
    "LANG": "C",
    "LC_ALL": "C",
    "TZ": "UTC",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONWARNINGS": "always",
}

IDENTITY_B: dict[str, str] = {
    "HOME": "/tmp/crucible-identity-bravo",
    "USER": "crucible-bravo",
    "LOGNAME": "crucible-bravo",
    "HOSTNAME": "crucible-bravo.invalid",
    "LANG": "en_US.UTF-8",
    "LC_ALL": "en_US.UTF-8",
    "TZ": "Pacific/Kiritimati",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONWARNINGS": "always",
}

VARIED_IDENTITY_DIMENSIONS: tuple[str, ...] = (
    "working directory",
    "HOME",
    "PWD",
    "USER and LOGNAME",
    "HOSTNAME environment variable",
    "locale (LANG, LC_ALL)",
    "timezone (TZ)",
)

UNVARIED_IDENTITY_DIMENSIONS: tuple[str, ...] = (
    "kernel-reported hostname (uname and gethostname)",
    "real and effective uid and gid",
    "mount namespace and filesystem root",
    "process namespace",
)


def _register() -> None:
    """Declare every step 8g instrument under the twelve-field registry schema.

    Phase 1 item 4 requires the declaration to carry what a missing instrument
    costs, so ``disposition_cap_on_absence`` is set on every row and is never
    SHIP: the absence of a delivery-conformance instrument is a coverage gap,
    never a pass.
    """
    rows = (
        Instrument(
            name="G-DEL-LAYOUT",
            category=Category.DELIVERY,
            binary="",
            ecosystems=("*",),
            timeout_seconds=120.0,
            required_conditions=("committed task bundles present",),
            critical_capability="required Harbor path resolution and step reconciliation",
            evidence_class=EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="Restates the Harbor path vocabulary locally rather than importing it.",
        ),
        Instrument(
            name="G-DEL-DISJOINT",
            category=Category.DELIVERY,
            binary="",
            ecosystems=("*",),
            timeout_seconds=120.0,
            required_conditions=("committed task bundles present",),
            critical_capability="task-lane residency partition across all three lane roots",
            evidence_class=EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="lane-overlap and staging-residue are retained delivery-integrity findings.",
        ),
        Instrument(
            name="G-DEL-SCHEMA",
            category=Category.DELIVERY,
            binary="",
            ecosystems=("*",),
            timeout_seconds=120.0,
            required_conditions=("task manifest schema version projected through CRUCIBLE_VIEW",),
            critical_capability="task manifest validation against the bound schema version",
            evidence_class=EvidenceClass.SCHEMA_VALIDATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="Never validates against a locally installed schema version.",
        ),
        Instrument(
            name="G-DEL-PIN",
            category=Category.DELIVERY,
            binary="",
            ecosystems=("*",),
            timeout_seconds=120.0,
            required_conditions=("committed container image references present",),
            critical_capability="image digest pinning and network policy correspondence",
            evidence_class=EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="Surrounding surface gap D-EVALUATOR-IMAGE-UNPINNED is already in scope.yaml.",
        ),
        Instrument(
            name="G-DEL-REWARD",
            category=Category.DELIVERY,
            binary="",
            ecosystems=("*",),
            timeout_seconds=120.0,
            required_conditions=("committed rollout evidence present",),
            critical_capability="reward contract termination and zero-score attribution",
            evidence_class=EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="Reads the bound reward path out of the committed verifier entry point.",
        ),
        Instrument(
            name="G-TRUTH-REGEN",
            category=Category.PROVENANCE,
            binary="python3",
            ecosystems=("*",),
            timeout_seconds=REGEN_TIMEOUT_SECONDS,
            required_conditions=("solution/recompute.py present", "python3 resolvable"),
            critical_capability="byte-identical regeneration of generated ground truth",
            evidence_class=EvidenceClass.EXECUTION_REPLAY,
            requires_parser=True,
            requires_raw_artifact=True,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="The sole execution of producer code anywhere in CRUCIBLE.",
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


def _load_json(path: Path) -> Any:
    """Parse one committed JSON document, failing closed to None."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_yaml(path: Path) -> Any:
    """Parse one committed YAML document, failing closed to None."""
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def bundles_of(base: Path) -> list[Path]:
    """Every resident bundle directory, derived from committed bytes alone."""
    return sorted(core.bundle_roots(base), key=lambda path: path.name)


def lane_roots_of(base: Path) -> dict[str, dict[str, Any]]:
    """Resolve the four roots a bundle may legally be resident under.

    The verification root itself is included beside the three lane roots because
    this root holds its bundles as direct children, and a residency derivation
    that only looked at the three named lanes would report an empty corpus and
    then call the partition satisfied, which is a vacuous pass over bundles it
    never saw.
    """
    resolved: dict[str, dict[str, Any]] = {
        "root": {"path": str(base), "exists": base.is_dir(), "is_lane_root": False}
    }
    for name in LANE_ROOT_NAMES:
        candidate = base / name
        resolved[name] = {
            "path": str(candidate),
            "exists": candidate.is_dir(),
            "is_lane_root": True,
        }
    return resolved


def rollouts_of(bundle: Path) -> list[Path]:
    """Every committed rollout directory under this bundle's own trajectories tree.

    Step 8 binds rollout evidence to the bundle's own subtree, so this never
    walks outside the bundle and never reads another bundle's trajectories.
    """
    trajectories = bundle / "trajectories"
    if not trajectories.is_dir():
        return []
    found: list[Path] = []
    for model in sorted(trajectories.iterdir()):
        if not model.is_dir():
            continue
        for run in sorted(model.iterdir()):
            if run.is_dir():
                found.append(run)
    return found


def committed_relative_paths(bundle: Path) -> list[str]:
    """Every committed file under a bundle as a sorted POSIX relative path list."""
    found: list[str] = []
    for path in bundle.rglob("*"):
        if path.is_file() and not path.is_symlink():
            found.append(path.relative_to(bundle).as_posix())
    return sorted(found)


def declared_steps(manifest: dict[str, Any]) -> list[str]:
    """The step names a task manifest declares, under either Harbor spelling.

    Harbor admits a ``steps`` table keyed by name and a ``[[steps]]`` array of
    tables carrying a ``name``. Both are read so that a manifest is never
    reported as declaring no step merely because it chose the other spelling,
    which would turn a real reconciliation failure into a vacuous pass.
    """
    raw = manifest.get("steps")
    names: list[str] = []
    if isinstance(raw, dict):
        names.extend(str(key) for key in raw)
    elif isinstance(raw, list):
        for entry in raw:
            if isinstance(entry, dict) and entry.get("name"):
                names.append(str(entry["name"]))
            elif isinstance(entry, str):
                names.append(entry)
    return sorted(set(names))


def on_disk_steps(bundle: Path) -> list[str]:
    """The step trees committed under the bundle's Harbor ``steps/`` root."""
    steps = bundle / "steps"
    if not steps.is_dir():
        return []
    return sorted(child.name for child in steps.iterdir() if child.is_dir())


def _undefined_paths(bundle: Path, relatives: list[str]) -> list[str]:
    """Committed paths the delivery format does not define a home for.

    The defined vocabulary is the Harbor bundle roots plus the Harbor task-root
    files, widened by ``trajectories/``, which step 8 defines as the home of
    committed rollout evidence.
    """
    defined_dirs = HARBOR_BUNDLE_DIRS + TRINITY_BUNDLE_DIRS
    undefined: list[str] = []
    for relative in relatives:
        head = relative.split("/", 1)[0]
        if head in defined_dirs and "/" in relative:
            continue
        if relative in HARBOR_BUNDLE_FILES:
            continue
        undefined.append(relative)
    return undefined


def run_layout(base: Path) -> InstrumentResult:
    """G-DEL-LAYOUT: required path resolution and both-directions step reconciliation.

    Three set relations are computed and all three are recorded whether or not
    they fire. First, every required Harbor path is resolved for every bundle
    under every candidate lane root, so a bundle resident in a lane this root
    does not use is still enumerated rather than silently skipped. Second, every
    committed path is tested against the defined-path vocabulary. Third, the
    declared step set and the on-disk step tree set are compared in both
    directions, and the manifest's declared artifact set is compared against
    each committed rollout's verifier tree on the same footing, because a
    declared artifact absent from committed evidence is a declared path that
    does not exist.
    """
    findings: list[Finding] = []
    roots = lane_roots_of(base)
    resident = bundles_of(base)
    per_bundle: list[dict[str, Any]] = []

    for bundle in resident:
        manifest = _load_toml(bundle / "task.toml")
        relatives = committed_relative_paths(bundle)
        missing = [name for name in REQUIRED_BUNDLE_PATHS if not (bundle / name).is_file()]
        undefined = _undefined_paths(bundle, relatives)
        declared = declared_steps(manifest)
        on_disk = on_disk_steps(bundle)
        declared_without_tree = sorted(set(declared) - set(on_disk))
        tree_without_declaration = sorted(set(on_disk) - set(declared))
        artifacts = [str(entry) for entry in (manifest.get("artifacts") or [])]
        artifact_rows = _reconcile_rollout_artifacts(bundle, artifacts)

        row = {
            "uuid": bundle.name,
            "lane": core.lane_of(bundle, base),
            "required_paths_total": len(REQUIRED_BUNDLE_PATHS),
            "required_paths_missing": missing,
            "committed_paths_total": len(relatives),
            "undefined_paths": undefined,
            "declared_steps": declared,
            "on_disk_steps": on_disk,
            "declared_steps_without_tree": declared_without_tree,
            "on_disk_steps_without_declaration": tree_without_declaration,
            "declared_artifacts": artifacts,
            "rollout_artifact_reconciliation": artifact_rows,
        }
        per_bundle.append(row)

        if missing:
            findings.append(
                Finding(
                    finding_id=f"F-DEL-LAYOUT-REQUIRED-ABSENT-{bundle.name}",
                    instrument="G-DEL-LAYOUT",
                    critical_class=CRITICAL_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        "The bundle does not resolve every required Harbor path: "
                        + ", ".join(missing)
                    ),
                    evidence={"missing": missing, "lane": row["lane"]},
                )
            )
        if undefined:
            findings.append(
                Finding(
                    finding_id=f"F-DEL-LAYOUT-UNDEFINED-PATH-{bundle.name}",
                    instrument="G-DEL-LAYOUT",
                    critical_class=CRITICAL_CLASS,
                    severity=Severity.MEDIUM,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        "The bundle commits an artifact at a path the delivery format "
                        "does not define: " + ", ".join(undefined[:20])
                    ),
                    evidence={"undefined_paths": undefined},
                )
            )
        if declared_without_tree or tree_without_declaration:
            findings.append(
                Finding(
                    finding_id=f"F-DEL-LAYOUT-STEP-UNRECONCILED-{bundle.name}",
                    instrument="G-DEL-LAYOUT",
                    critical_class=CRITICAL_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        "Declared steps and on-disk step trees do not agree in both directions."
                    ),
                    evidence={
                        "declared_without_tree": declared_without_tree,
                        "tree_without_declaration": tree_without_declaration,
                    },
                )
            )
        findings.extend(_artifact_findings(bundle, artifact_rows))

    return InstrumentResult(
        instrument="G-DEL-LAYOUT",
        ran=True,
        findings=findings,
        gaps=[],
        artifacts=[],
        standing=(Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE),
        notes={
            "lane_roots": roots,
            "resident_bundles": [bundle.name for bundle in resident],
            "defined_path_vocabulary": {
                "directories": list(HARBOR_BUNDLE_DIRS + TRINITY_BUNDLE_DIRS),
                "task_root_files": list(HARBOR_BUNDLE_FILES),
                "vocabulary_basis": (
                    "the Harbor delivery format bundle roots and task-root files, widened "
                    "by trajectories/ which contract step 8 defines as the home of "
                    "committed rollout evidence"
                ),
            },
            "per_bundle": per_bundle,
        },
    )


def _reconcile_rollout_artifacts(bundle: Path, artifacts: list[str]) -> list[dict[str, Any]]:
    """Compare the manifest's declared artifact set with each rollout's verifier tree.

    Declared artifacts are container paths under the runner's log root, so they
    are matched into committed evidence by basename under the rollout's
    ``verifier/`` directory. The rollout's own collection manifest is read
    beside the comparison so that an absence the runner already recorded as a
    failed collection is distinguishable from an absence nothing explains.
    """
    declared_names = sorted({Path(entry).name for entry in artifacts if entry})
    rows: list[dict[str, Any]] = []
    for rollout in rollouts_of(bundle):
        verifier = rollout / "verifier"
        present = sorted(child.name for child in verifier.iterdir()) if verifier.is_dir() else []
        manifest = _load_json(rollout / "artifacts" / "manifest.json")
        statuses: dict[str, str] = {}
        if isinstance(manifest, list):
            for entry in manifest:
                if isinstance(entry, dict) and entry.get("source"):
                    statuses[Path(str(entry["source"])).name] = str(entry.get("status", ""))
        rows.append(
            {
                "rollout": rollout.relative_to(bundle).as_posix(),
                "declared_artifacts": declared_names,
                "verifier_tree": present,
                "declared_absent_from_tree": sorted(set(declared_names) - set(present)),
                "tree_not_declared": sorted(set(present) - set(declared_names)),
                "collection_status": statuses,
            }
        )
    return rows


def _artifact_findings(bundle: Path, rows: list[dict[str, Any]]) -> list[Finding]:
    """Retain a declared artifact that no committed rollout evidence carries.

    The reverse direction, a committed verifier file the manifest does not
    declare, is recorded as evidence and is not a finding: the manifest's
    artifact list is the runner's extra-collection list, not an exhaustive
    inventory of what the verifier writes, so treating every undeclared
    verifier file as a defect would manufacture findings the format does not
    support.
    """
    findings: list[Finding] = []
    for row in rows:
        absent = row["declared_absent_from_tree"]
        if not absent:
            continue
        rollout = row["rollout"]
        slug = rollout.replace("/", "-")
        findings.append(
            Finding(
                finding_id=f"F-DEL-LAYOUT-DECLARED-ARTIFACT-ABSENT-{bundle.name}-{slug}",
                instrument="G-DEL-LAYOUT",
                critical_class=CRITICAL_CLASS,
                severity=Severity.MEDIUM,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject=f"{bundle.name}/{rollout}",
                statement=(
                    "The task manifest declares an artifact that this committed rollout's "
                    "verifier tree does not carry: " + ", ".join(absent)
                ),
                evidence={
                    "declared_absent_from_tree": absent,
                    "verifier_tree": row["verifier_tree"],
                    "collection_status": row["collection_status"],
                },
            )
        )
    return findings


def run_disjoint(base: Path) -> InstrumentResult:
    """G-DEL-DISJOINT: re-derive task-lane residency across all three lane roots.

    Residency is derived rather than read from any declaration, because a
    declared lane is an author claim and the partition is a property of where
    bytes actually sit. A uuid seen under two lane roots is ``lane-overlap`` and
    a uuid seen under ``staging/`` and a lane root is ``staging-residue``; both
    are retained delivery-integrity findings capping at BLOCK, because a bundle
    existing in two places is a bundle whose two copies can drift apart.
    """
    residency: dict[str, list[str]] = {}
    per_root: dict[str, list[str]] = {}
    for name, row in lane_roots_of(base).items():
        root = Path(row["path"])
        seen: list[str] = []
        if root.is_dir():
            for child in sorted(root.iterdir()):
                if (
                    child.is_dir()
                    and not child.name.startswith(".")
                    and (child / "task.toml").is_file()
                ):
                    seen.append(child.name)
                    residency.setdefault(child.name, []).append(name)
        per_root[name] = seen

    findings: list[Finding] = []
    lane_overlap = {
        uuid: sorted(set(where) & set(LANE_ROOT_NAMES))
        for uuid, where in residency.items()
        if len(set(where) & set(LANE_ROOT_NAMES)) > 1
    }
    staging_residue = {
        uuid: sorted(where)
        for uuid, where in residency.items()
        if "staging" in where and (set(where) & {"samples", "delivery"})
    }
    for uuid, where in sorted(lane_overlap.items()):
        findings.append(
            Finding(
                finding_id=f"F-DEL-DISJOINT-LANE-OVERLAP-{uuid}",
                instrument="G-DEL-DISJOINT",
                critical_class=CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.BLOCK,
                bucket=Bucket.D,
                subject=uuid,
                statement=(
                    "lane-overlap: the uuid is resident under more than one lane root, so "
                    "the three lane roots are not a partition."
                ),
                evidence={"lane_roots": where},
            )
        )
    for uuid, where in sorted(staging_residue.items()):
        findings.append(
            Finding(
                finding_id=f"F-DEL-DISJOINT-STAGING-RESIDUE-{uuid}",
                instrument="G-DEL-DISJOINT",
                critical_class=CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.BLOCK,
                bucket=Bucket.D,
                subject=uuid,
                statement=(
                    "staging-residue: the uuid is resident under staging/ and under a lane "
                    "root at the same time."
                ),
                evidence={"lane_roots": where},
            )
        )

    return InstrumentResult(
        instrument="G-DEL-DISJOINT",
        ran=True,
        findings=findings,
        gaps=[],
        artifacts=[],
        standing=(Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE),
        notes={
            "residency_by_uuid": {uuid: sorted(where) for uuid, where in sorted(residency.items())},
            "residency_by_root": per_root,
            "lane_roots_present": [name for name in LANE_ROOT_NAMES if (base / name).is_dir()],
            "partition_satisfied": not lane_overlap and not staging_residue,
            "partition_basis": (
                "every derived uuid resolves under exactly one root; no bundle is resident "
                "under two lane roots and none is resident under staging/ and a lane root"
            ),
        },
    )


def crucible_view_path(base: Path) -> Path:
    """Locate CRUCIBLE_VIEW, the only ENGRAM surface this family may read.

    The projection sits beside the verification root in the parent project. It
    is the sole ENGRAM input: the hardness contract and its rendered report are
    withheld from CRUCIBLE by construction and are never opened here.
    """
    return base.resolve().parent / ".memory" / "crucible_view.yaml"


def run_schema(base: Path) -> InstrumentResult:
    """G-DEL-SCHEMA: validate each manifest against the projected schema version.

    The instrument resolves the schema version the sign-off bound by looking for
    the resident bundles in CRUCIBLE_VIEW. The projection carries determinations
    for a different set of instances, so no resident bundle is projected and no
    bound schema version exists to validate against. The governing coverage gap
    D-DEL-SCHEMA-UNPROJECTED fires and caps at HOLD.

    Validating against a locally installed schema version instead is refused
    explicitly. That version reflects whatever the producer's tooling currently
    expects, which is the thing under audit, so a pass against it would prove
    only that the manifest agrees with the tool that wrote it.
    """
    view_path = crucible_view_path(base)
    view_present = view_path.is_file()
    view_text = _read_text(view_path) if view_present else ""
    view_document = _load_yaml(view_path) if view_present else None

    declared: list[dict[str, Any]] = []
    projection: list[dict[str, Any]] = []
    for bundle in bundles_of(base):
        manifest = _load_toml(bundle / "task.toml")
        grounding = _load_json(bundle / "solution" / "grounding.yaml")
        instance_id = ""
        if isinstance(grounding, dict):
            instance_id = str(grounding.get("instance_id") or "")
        declared.append(
            {
                "uuid": bundle.name,
                "declared_schema_version": str(manifest.get("schema_version") or ""),
                "instance_id": instance_id,
                "manifest_digest": core.sha256_path(bundle / "task.toml"),
            }
        )
        projection.append(
            {
                "uuid": bundle.name,
                "uuid_occurrences_in_view": view_text.count(bundle.name),
                "instance_id": instance_id,
                "instance_id_occurrences_in_view": (
                    view_text.count(instance_id) if instance_id else 0
                ),
            }
        )

    projected_uuids = [
        row["uuid"]
        for row in projection
        if row["uuid_occurrences_in_view"] or row["instance_id_occurrences_in_view"]
    ]
    view_schema = ""
    if isinstance(view_document, dict):
        view_schema = str(view_document.get("schema_version") or "")

    gaps = [
        CoverageGap(
            gap_id="D-DEL-SCHEMA-UNPROJECTED",
            instrument="G-DEL-SCHEMA",
            surface="delivery_manifest_schema",
            reason="schema-version-unprojected",
            caps=Disposition.HOLD,
            subject="project",
            statement=(
                "CRUCIBLE_VIEW carries determinations for instances that are not the "
                "resident bundles and records no task-manifest schema version for any "
                "resident uuid, so the schema version bound at sign-off is unprojected. "
                "The manifests are recorded as declaring their own version and are not "
                "validated, because validating against the schema version installed on "
                "this host would test the manifest against the producer's current "
                "tooling rather than against the version the sign-off bound."
            ),
        )
    ]

    return InstrumentResult(
        instrument="G-DEL-SCHEMA",
        ran=True,
        findings=[],
        gaps=gaps,
        artifacts=[],
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes={
            "crucible_view_path": str(view_path),
            "crucible_view_present": view_present,
            "crucible_view_digest": (core.sha256_path(view_path) if view_present else None),
            "crucible_view_schema_version": view_schema,
            "projected_resident_uuids": projected_uuids,
            "projection_probe": projection,
            "declared_manifests": declared,
            "validation_performed": False,
            "validation_refusal_basis": (
                "no schema version is projected through CRUCIBLE_VIEW for any resident "
                "uuid, and a locally installed schema version is never a substitute"
            ),
        },
    )


def image_references(bundle: Path) -> list[dict[str, Any]]:
    """Enumerate every container image reference the bundle commits.

    References come from four places: the manifest's base image reference and
    its separately recorded digest, the manifest's runtime image, and every
    ``FROM`` instruction in both committed Dockerfiles. A ``FROM scratch`` and a
    ``FROM`` naming an earlier build stage are marked as resolving against no
    registry, because neither can carry a digest and calling either unpinned
    would be a false positive.
    """
    manifest = _load_toml(bundle / "task.toml")
    metadata = manifest.get("metadata") if isinstance(manifest.get("metadata"), dict) else {}
    environment = (
        manifest.get("environment") if isinstance(manifest.get("environment"), dict) else {}
    )
    rows: list[dict[str, Any]] = []

    for source, key in (
        ("task.toml [metadata].base_image_ref", "base_image_ref"),
        ("task.toml [environment].docker_image", "docker_image"),
    ):
        table = metadata if key == "base_image_ref" else environment
        value = str(table.get(key) or "")
        rows.append(
            {
                "source": source,
                "reference": value,
                "registry_resolvable": bool(value),
                "digest_pinned": bool(IMAGE_DIGEST.search(value)),
                "companion_digest": str(metadata.get("base_image_digest") or "")
                if key == "base_image_ref"
                else "",
            }
        )

    for relative in ("environment/Dockerfile", "tests/Dockerfile"):
        path = bundle / relative
        if not path.is_file():
            continue
        text = _read_text(path)
        stages = {
            match.group(1).lower()
            for match in re.finditer(r"^\s*FROM\s+\S+\s+AS\s+(\S+)", text, re.MULTILINE | re.I)
        }
        for match in DOCKER_FROM.finditer(text):
            reference = match.group(1)
            resolvable = reference != "scratch" and reference.lower() not in stages
            rows.append(
                {
                    "source": f"{relative} FROM",
                    "reference": reference,
                    "registry_resolvable": resolvable,
                    "digest_pinned": bool(IMAGE_DIGEST.search(reference)),
                    "companion_digest": "",
                }
            )
    return rows


def network_policy(bundle: Path) -> dict[str, Any]:
    """Read the declared network policy and what committed evidence records of it.

    The declaration is per phase in the manifest. The committed rollout records
    whether the run widened that policy, through the runner's own
    ``extra_allowed_hosts`` and override fields, but it does not record the
    enforced mode itself, so correspondence is checked in the direction the
    bytes support and the unsupported direction is reported as unobserved
    rather than as agreement.
    """
    manifest = _load_toml(bundle / "task.toml")
    declared = {}
    for phase in ("environment", "agent", "verifier"):
        table = manifest.get(phase)
        if isinstance(table, dict):
            declared[phase] = {
                "network_mode": str(table.get("network_mode") or ""),
                "allowed_hosts": [str(host) for host in (table.get("allowed_hosts") or [])],
            }

    observed: list[dict[str, Any]] = []
    for rollout in rollouts_of(bundle):
        lock = _load_json(rollout / "lock.json")
        widened: dict[str, Any] = {}
        if isinstance(lock, dict):
            for phase in ("agent", "environment"):
                table = lock.get(phase)
                if isinstance(table, dict):
                    widened[phase] = [
                        str(host) for host in (table.get("extra_allowed_hosts") or [])
                    ]
        observed.append(
            {
                "rollout": rollout.relative_to(bundle).as_posix(),
                "extra_allowed_hosts": widened,
                "enforced_mode_recorded": False,
            }
        )
    return {"declared": declared, "observed": observed}


def run_pin(base: Path) -> InstrumentResult:
    """G-DEL-PIN: image digest pinning and network policy correspondence.

    An unpinned base image is emitted as a finding rather than folded into the
    standing gap D-EVALUATOR-IMAGE-UNPINNED. That gap covers the surrounding
    surface, namely that no bundle pins the evaluator image its measurement ran
    on, which is a missing measurement. A manifest that declares a base image
    reference as a bare tag with an empty digest field is not a missing
    measurement: it is an observed defect in committed bytes, and recording it
    only as a gap would convert a present defect into an absent one.

    Network policy correspondence caps at HOLD through its own gap, because the
    committed rollout evidence records only that the run did not widen the
    declared policy and never records the mode the runner enforced.
    """
    findings: list[Finding] = []
    per_bundle: list[dict[str, Any]] = []
    for bundle in bundles_of(base):
        references = image_references(bundle)
        unpinned = [
            row for row in references if row["registry_resolvable"] and not row["digest_pinned"]
        ]
        policy = network_policy(bundle)
        per_bundle.append(
            {
                "uuid": bundle.name,
                "references": references,
                "unpinned_references": unpinned,
                "network_policy": policy,
            }
        )
        if unpinned:
            findings.append(
                Finding(
                    finding_id=f"F-DEL-PIN-IMAGE-UNPINNED-{bundle.name}",
                    instrument="G-DEL-PIN",
                    critical_class=CRITICAL_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        "A committed container image reference carries no @sha256: digest, "
                        "so the bytes the reference resolves to can be replaced without "
                        "changing any committed byte: "
                        + "; ".join(
                            f"{row['source']} = {row['reference'] or '(empty)'}" for row in unpinned
                        )
                    ),
                    evidence={
                        "unpinned_references": unpinned,
                        "all_references": references,
                        "surrounding_surface_gap": "D-EVALUATOR-IMAGE-UNPINNED",
                    },
                )
            )

    gaps = [
        CoverageGap(
            gap_id="D-DEL-PIN-NETWORK-POLICY-UNOBSERVED",
            instrument="G-DEL-PIN",
            surface="delivery_closure",
            reason="enforced-network-mode-unrecorded",
            caps=Disposition.HOLD,
            subject="project",
            statement=(
                "The declared network policy is read from every committed manifest and no "
                "committed rollout record widens it, but no rollout record carries the "
                "network mode the runner actually enforced, so the declared policy is "
                "confirmed to be unwidened and is not confirmed to be the policy the "
                "environment producing the committed evidence ran under."
            ),
        )
    ]

    return InstrumentResult(
        instrument="G-DEL-PIN",
        ran=True,
        findings=findings,
        gaps=gaps,
        artifacts=[],
        standing=(Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE),
        notes={"per_bundle": per_bundle, "digest_pattern": IMAGE_DIGEST.pattern},
    )


def reward_contract(bundle: Path) -> dict[str, Any]:
    """Derive the reward contract the committed verifier entry point terminates on.

    The bound path is read out of ``tests/test.sh`` and ``tests/run_tests.py``
    rather than assumed, because the check is whether the verifier terminates by
    writing the path the contract binds, and an assumed path would make the
    check agree with itself.
    """
    entry = _read_text(bundle / "tests" / "test.sh")
    runner = _read_text(bundle / "tests" / "run_tests.py")
    prewritten = {name: (name in entry) for name in REWARD_CONTRACT_FILES}
    zero_reasons = sorted(set(re.findall(r'write_reward\([^,]+,\s*0\.0,\s*"([^"]+)"', runner)))
    return {
        "entry_point_prewrites": prewritten,
        "entry_point_prewrites_reason": "verifier-did-not-complete" in entry,
        "runner_writes_contract_paths": {name: (name in runner) for name in REWARD_CONTRACT_FILES},
        "zero_without_grading_reasons": zero_reasons,
        "zero_without_grading_reason_count": len(zero_reasons),
    }


def rollout_rewards(bundle: Path) -> list[dict[str, Any]]:
    """Read every committed rollout's reward triple and reconcile the three files."""
    rows: list[dict[str, Any]] = []
    for rollout in rollouts_of(bundle):
        verifier = rollout / "verifier"
        reward_json = _load_json(verifier / "reward.json")
        reason_json = _load_json(verifier / "reward_reason.json")
        reward_txt = _read_text(verifier / "reward.txt").strip()
        value: float | None = None
        if isinstance(reward_json, dict) and isinstance(reward_json.get("reward"), int | float):
            value = float(reward_json["reward"])
        text_value: float | None = None
        try:
            text_value = float(reward_txt) if reward_txt else None
        except ValueError:
            text_value = None
        reason = ""
        reason_value: float | None = None
        if isinstance(reason_json, dict):
            reason = str(reason_json.get("reason") or "")
            if isinstance(reason_json.get("reward"), int | float):
                reason_value = float(reason_json["reward"])
        rows.append(
            {
                "rollout": rollout.relative_to(bundle).as_posix(),
                "files_present": {
                    name: (verifier / name).is_file() for name in REWARD_CONTRACT_FILES
                },
                "reward": value,
                "reward_txt": text_value,
                "reward_reason_reward": reason_value,
                "reason": reason,
                "is_zero": value == 0.0,
                "zero_carries_reason": bool(reason) if value == 0.0 else None,
                "triple_agrees": value is not None
                and value == text_value
                and value == reason_value,
            }
        )
    return rows


def run_reward(base: Path) -> InstrumentResult:
    """G-DEL-REWARD: reward contract termination and zero-score attribution.

    Two relations are checked. The verifier entry point must terminate by
    writing the bound reward contract path, which it does by pre-writing a zero
    carrying the reason ``verifier-did-not-complete`` before the grader runs, so
    a grader that dies before deciding leaves a zero with a reason rather than
    an absent file. Every committed zero score must then carry a
    machine-readable reason, checked against the committed rollout bytes rather
    than against the runner's ability to write one.
    """
    findings: list[Finding] = []
    per_bundle: list[dict[str, Any]] = []
    for bundle in bundles_of(base):
        contract = reward_contract(bundle)
        rewards = rollout_rewards(bundle)
        per_bundle.append({"uuid": bundle.name, "contract": contract, "rollouts": rewards})

        if not all(contract["entry_point_prewrites"].values()):
            findings.append(
                Finding(
                    finding_id=f"F-DEL-REWARD-CONTRACT-UNWRITTEN-{bundle.name}",
                    instrument="G-DEL-REWARD",
                    critical_class=CRITICAL_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        "The committed verifier entry point does not terminate by writing "
                        "every bound reward contract path."
                    ),
                    evidence=contract,
                )
            )
        for row in rewards:
            slug = row["rollout"].replace("/", "-")
            missing = [name for name, ok in row["files_present"].items() if not ok]
            if missing:
                findings.append(
                    Finding(
                        finding_id=f"F-DEL-REWARD-FILE-ABSENT-{bundle.name}-{slug}",
                        instrument="G-DEL-REWARD",
                        critical_class=CRITICAL_CLASS,
                        severity=Severity.HIGH,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=f"{bundle.name}/{row['rollout']}",
                        statement=(
                            "A committed rollout does not carry every bound reward "
                            "contract file: " + ", ".join(missing)
                        ),
                        evidence=row,
                    )
                )
                continue
            if row["is_zero"] and not row["zero_carries_reason"]:
                findings.append(
                    Finding(
                        finding_id=f"F-DEL-REWARD-ZERO-UNATTRIBUTED-{bundle.name}-{slug}",
                        instrument="G-DEL-REWARD",
                        critical_class=CRITICAL_CLASS,
                        severity=Severity.HIGH,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=f"{bundle.name}/{row['rollout']}",
                        statement=("A committed zero score carries no machine-readable reason."),
                        evidence=row,
                    )
                )
            if not row["triple_agrees"]:
                findings.append(
                    Finding(
                        finding_id=f"F-DEL-REWARD-TRIPLE-DISAGREES-{bundle.name}-{slug}",
                        instrument="G-DEL-REWARD",
                        critical_class=CRITICAL_CLASS,
                        severity=Severity.HIGH,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=f"{bundle.name}/{row['rollout']}",
                        statement=(
                            "The three committed reward contract files do not carry the same value."
                        ),
                        evidence=row,
                    )
                )

    zeros = [row for entry in per_bundle for row in entry["rollouts"] if row["is_zero"]]
    return InstrumentResult(
        instrument="G-DEL-REWARD",
        ran=True,
        findings=findings,
        gaps=[],
        artifacts=[],
        standing=(Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE),
        notes={
            "per_bundle": per_bundle,
            "committed_zero_count": len(zeros),
            "committed_zero_reasons": sorted({row["reason"] for row in zeros}),
        },
    )


def _stage_identity(bundle: Path, workspace: Path, name: str) -> Path:
    """Copy the generator's input closure into one named sandbox identity.

    Only ``solution/`` and ``tests/`` are copied because the committed generator
    resolves its bundle root from its own file location and reads and writes
    only inside those two trees. Copying the rollout evidence as well would add
    minutes of I/O without changing a byte the generator can observe.
    """
    target = workspace / name / f"bundle-{name}"
    target.mkdir(parents=True, exist_ok=True)
    for tree in ("solution", "tests"):
        source = bundle / tree
        if source.is_dir():
            shutil.copytree(source, target / tree, symlinks=True)
    return target


def _regenerate(staged: Path, identity: dict[str, str], artifact_id: str) -> RawArtifact:
    """Execute the committed generator once under one sandbox identity."""
    env = dict(identity)
    env["PWD"] = str(staged)
    env["TMPDIR"] = str(staged.parent)
    return core.run_capture(
        ["python3", "solution/recompute.py"],
        artifact_id=artifact_id,
        cwd=staged,
        timeout=REGEN_TIMEOUT_SECONDS,
        env=env,
    )


def ground_truth_steps(bundle: Path) -> dict[str, list[str]]:
    """Derive the ground-truth step set and the committed checker set.

    The generated ground truth names one load-bearing site per entry in the
    grounding source and one requirement per site. The committed checker set is
    the requirement and site vocabulary the compiled deterministic channel and
    the committed probe table actually carry. Reconciling the two in both
    directions is what catches a ground-truth step that no checker observes and
    a checker that grades a step the ground truth never names.
    """
    grounding = _load_json(bundle / "solution" / "grounding.yaml")
    sites = grounding.get("sites") or [] if isinstance(grounding, dict) else []
    truth_requirements = sorted(
        {
            str(requirement.get("id"))
            for site in sites
            for requirement in (site.get("requirements") or [])
            if requirement.get("id")
        }
    )
    truth_sites = sorted({str(site.get("path")) for site in sites if site.get("path")})

    rubrics = _load_json(bundle / "tests" / "rubrics.json")
    checker_sites_doc = rubrics.get("sites") or [] if isinstance(rubrics, dict) else []
    checker_requirements = sorted(
        {
            str(requirement.get("id"))
            for site in checker_sites_doc
            for requirement in (site.get("requirements") or [])
            if requirement.get("id")
        }
    )
    checker_sites = sorted(
        {str(site.get("path")) for site in checker_sites_doc if site.get("path")}
    )

    compiled = _read_text(bundle / "tests" / "test_output.py")
    compiled_requirements = sorted(set(RECORD_PROPERTY_REQUIREMENT.findall(compiled)))
    compiled_sites = sorted(set(RECORD_PROPERTY_SITE.findall(compiled)))

    return {
        "truth_requirements": truth_requirements,
        "truth_sites": truth_sites,
        "checker_requirements": checker_requirements,
        "checker_sites": checker_sites,
        "compiled_requirements": compiled_requirements,
        "compiled_sites": compiled_sites,
    }


def _step_reconciliation(steps: dict[str, list[str]]) -> dict[str, Any]:
    """Compare the ground-truth step set against the committed checker set."""
    truth_requirements = set(steps["truth_requirements"])
    checker_requirements = set(steps["checker_requirements"]) | set(steps["compiled_requirements"])
    truth_sites = set(steps["truth_sites"])
    checker_sites = set(steps["checker_sites"]) | set(steps["compiled_sites"])
    return {
        "requirements_without_checker": sorted(truth_requirements - checker_requirements),
        "checkers_without_requirement": sorted(checker_requirements - truth_requirements),
        "sites_without_checker": sorted(truth_sites - checker_sites),
        "checkers_without_site": sorted(checker_sites - truth_sites),
        "reconciled": truth_requirements == checker_requirements and truth_sites == checker_sites,
    }


def run_truth_regen(base: Path) -> InstrumentResult:
    """G-TRUTH-REGEN: byte-identical regeneration under two sandbox identities.

    This is the sole execution of producer code anywhere in CRUCIBLE. The
    generator runs twice from two distinct staged copies under two distinct
    environments, and three separate relations are recorded: run A against
    committed bytes, run B against committed bytes, and run A against run B. The
    third relation is the host-dependence test, and it is kept separate from the
    first two so that a generator that is stable but drifted is distinguishable
    from one that is unstable across identities.

    Identity variation is partial and the accompanying coverage gap says exactly
    which dimensions were varied and which were not, because claiming a full
    two-identity proof this harness cannot perform would be the same failure the
    check exists to catch.

    The committed generator emits a warning for an invalid escape sequence at
    line 225 of every copy. It is recorded as a finding because producer code
    carrying an escape sequence the language has scheduled for removal is a
    latent defect, and the finding states explicitly that the warning does not
    move any regenerated byte, so a reader is never left to infer the severity.
    """
    findings: list[Finding] = []
    artifacts: list[RawArtifact] = []
    per_bundle: list[dict[str, Any]] = []
    gaps: list[CoverageGap] = [
        CoverageGap(
            gap_id="D-TRUTH-REGEN-IDENTITY-PARTIAL",
            instrument="G-TRUTH-REGEN",
            surface="generated_ground_truth",
            reason="sandbox-identity-partially-varied",
            caps=Disposition.HOLD,
            subject="project",
            statement=(
                "The two-identity regeneration varied "
                + ", ".join(VARIED_IDENTITY_DIMENSIONS)
                + ", and could not vary "
                + ", ".join(UNVARIED_IDENTITY_DIMENSIONS)
                + ", because changing the kernel-reported hostname or the real uid "
                "requires privilege this harness does not hold and must not acquire. "
                "A generator reading its hostname through uname rather than through the "
                "HOSTNAME environment variable would therefore not be caught by this "
                "run, so byte-for-byte agreement across the two identities is evidence "
                "over the varied dimensions only."
            ),
        )
    ]

    with tempfile.TemporaryDirectory(prefix="crucible-truth-regen-") as workspace_name:
        workspace = Path(workspace_name)
        for bundle in bundles_of(base):
            generator = bundle / "solution" / "recompute.py"
            if not generator.is_file():
                gaps.append(
                    CoverageGap(
                        gap_id=f"D-TRUTH-REGEN-GENERATOR-ABSENT-{bundle.name}",
                        instrument="G-TRUTH-REGEN",
                        surface="generated_ground_truth",
                        reason="generator-absent",
                        caps=Disposition.HOLD,
                        subject=bundle.name,
                        statement=(
                            "The bundle commits no solution/recompute.py, so regeneration "
                            "could not run and the committed ground truth stands "
                            "unverified."
                        ),
                    )
                )
                continue

            staged_a = _stage_identity(bundle, workspace / bundle.name, "alpha")
            staged_b = _stage_identity(bundle, workspace / bundle.name, "bravo")
            run_a = _regenerate(staged_a, IDENTITY_A, f"truth-regen-{bundle.name}-alpha")
            run_b = _regenerate(staged_b, IDENTITY_B, f"truth-regen-{bundle.name}-bravo")
            artifacts.extend((run_a, run_b))

            if run_a.blocked_reason or run_b.blocked_reason:
                gaps.append(
                    CoverageGap(
                        gap_id=f"D-TRUTH-REGEN-UNRUNNABLE-{bundle.name}",
                        instrument="G-TRUTH-REGEN",
                        surface="generated_ground_truth",
                        reason="generator-unrunnable",
                        caps=Disposition.HOLD,
                        subject=bundle.name,
                        statement=(
                            "The committed generator could not be executed: "
                            f"{run_a.blocked_reason or run_b.blocked_reason}."
                        ),
                    )
                )
                continue

            comparison = _compare_regeneration(bundle, staged_a, staged_b)
            steps = ground_truth_steps(bundle)
            reconciliation = _step_reconciliation(steps)
            warnings = sorted(
                set(INVALID_ESCAPE.findall(run_a.stderr))
                | set(INVALID_ESCAPE.findall(run_b.stderr))
            )
            per_bundle.append(
                {
                    "uuid": bundle.name,
                    "exit_codes": {"alpha": run_a.exit_code, "bravo": run_b.exit_code},
                    "comparison": comparison,
                    "step_sets": steps,
                    "step_reconciliation": reconciliation,
                    "generator_warnings": warnings,
                }
            )

            findings.extend(_regen_findings(bundle, comparison, reconciliation, warnings))

    return InstrumentResult(
        instrument="G-TRUTH-REGEN",
        ran=bool(per_bundle),
        findings=findings,
        gaps=gaps,
        artifacts=artifacts,
        standing=(Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE),
        notes={
            "per_bundle": per_bundle,
            "identity_alpha": IDENTITY_A,
            "identity_bravo": IDENTITY_B,
            "varied_identity_dimensions": list(VARIED_IDENTITY_DIMENSIONS),
            "unvaried_identity_dimensions": list(UNVARIED_IDENTITY_DIMENSIONS),
            "generated_artifacts": list(GENERATED_ARTIFACTS),
        },
    )


def _compare_regeneration(bundle: Path, staged_a: Path, staged_b: Path) -> dict[str, Any]:
    """Digest every regenerated artifact against committed bytes and against itself."""
    rows: dict[str, Any] = {}
    for relative in GENERATED_ARTIFACTS:
        committed = bundle / relative
        produced_a = staged_a / relative
        produced_b = staged_b / relative
        digest_committed = core.sha256_path(committed) if committed.is_file() else "absent"
        digest_a = core.sha256_path(produced_a) if produced_a.is_file() else "absent"
        digest_b = core.sha256_path(produced_b) if produced_b.is_file() else "absent"
        rows[relative] = {
            "committed_sha256": digest_committed,
            "alpha_sha256": digest_a,
            "bravo_sha256": digest_b,
            "matches_committed": digest_committed == digest_a == digest_b,
            "identities_agree": digest_a == digest_b,
        }
    return {
        "artifacts": rows,
        "drifted": sorted(name for name, row in rows.items() if not row["matches_committed"]),
        "host_dependent": sorted(name for name, row in rows.items() if not row["identities_agree"]),
    }


def _regen_findings(
    bundle: Path,
    comparison: dict[str, Any],
    reconciliation: dict[str, Any],
    warnings: list[str],
) -> list[Finding]:
    """Retain regeneration drift, host dependence, step unreconciliation and warnings."""
    findings: list[Finding] = []
    if comparison["host_dependent"]:
        findings.append(
            Finding(
                finding_id=f"F-TRUTH-REGEN-HOST-DEPENDENT-{bundle.name}",
                instrument="G-TRUTH-REGEN",
                critical_class=CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.BLOCK,
                bucket=Bucket.D,
                subject=bundle.name,
                statement=(
                    "The committed generator produced different bytes under two sandbox "
                    "identities, so its output fingerprints the host it ran on: "
                    + ", ".join(comparison["host_dependent"])
                ),
                evidence=comparison,
            )
        )
    if comparison["drifted"]:
        findings.append(
            Finding(
                finding_id=f"F-TRUTH-REGEN-DRIFT-{bundle.name}",
                instrument="G-TRUTH-REGEN",
                critical_class=CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.BLOCK,
                bucket=Bucket.D,
                subject=bundle.name,
                statement=(
                    "Regenerating the committed generator does not reproduce the "
                    "committed generated artifacts byte for byte, so the committed "
                    "ground truth is not what the committed generator produces and is "
                    "either drifted or hand-edited: " + ", ".join(comparison["drifted"])
                ),
                evidence=comparison,
            )
        )
    if not reconciliation["reconciled"]:
        findings.append(
            Finding(
                finding_id=f"F-TRUTH-REGEN-STEPS-UNRECONCILED-{bundle.name}",
                instrument="G-TRUTH-REGEN",
                critical_class=CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.BLOCK,
                bucket=Bucket.D,
                subject=bundle.name,
                statement=(
                    "The ground-truth step set and the committed checker set do not "
                    "reconcile in both directions."
                ),
                evidence=reconciliation,
            )
        )
    if warnings:
        findings.append(
            Finding(
                finding_id=f"F-TRUTH-REGEN-GENERATOR-WARNING-{bundle.name}",
                instrument="G-TRUTH-REGEN",
                critical_class=CRITICAL_CLASS,
                severity=Severity.LOW,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject=bundle.name,
                statement=(
                    "The committed generator emits a warning for an invalid escape "
                    "sequence at solution/recompute.py line 225. The regenerated bytes "
                    "are unaffected by it, so this is a latent defect in producer code "
                    "and not a cause of the regeneration result: " + "; ".join(warnings)
                ),
                evidence={"warnings": warnings, "line": 225},
            )
        )
    return findings


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
    """Execute the step 8g delivery-conformance family and return every result.

    The reconnaissance record is accepted because crucible.py's dispatch passes
    it to every family, and the recorded bundle roster is carried into the notes
    of the layout instrument so that a later reader can see which corpus the
    run reasoned over. Residency itself is re-derived from committed bytes
    rather than read from the record, because G-DEL-DISJOINT's whole job is to
    derive residency and consuming a pre-derived answer would make it vacuous.
    """
    results = [
        _guard("G-DEL-LAYOUT", run_layout, base),
        _guard("G-DEL-DISJOINT", run_disjoint, base),
        _guard("G-DEL-SCHEMA", run_schema, base),
        _guard("G-DEL-PIN", run_pin, base),
        _guard("G-DEL-REWARD", run_reward, base),
        _guard("G-TRUTH-REGEN", run_truth_regen, base),
    ]
    recorded = getattr(reconnaissance, "bundles", None)
    if isinstance(recorded, list):
        results[0].notes["recon_bundle_roster"] = [
            str(row.get("uuid", "")) for row in recorded if isinstance(row, dict)
        ]
    return results


__all__ = [
    "GENERATED_ARTIFACTS",
    "REQUIRED_BUNDLE_PATHS",
    "bundles_of",
    "declared_steps",
    "ground_truth_steps",
    "image_references",
    "lane_roots_of",
    "network_policy",
    "on_disk_steps",
    "reward_contract",
    "rollout_rewards",
    "rollouts_of",
    "run_disjoint",
    "run_family",
    "run_layout",
    "run_pin",
    "run_reward",
    "run_schema",
    "run_truth_regen",
]
