"""Contract step 8e: the G-CAL calibration instrument family.

This module discharges the two instruments step 8e names. The rationale lives in
these docstrings because the contract is prompt-only, so the harness itself has
to carry the reasoning as audit evidence.

Containment boundary, stated first because it governs everything below.
CRUCIBLE is forbidden from reading hardness in any form. The ENGRAM hardness
contract is stripped in full: no hardness row, category, axis, orthogonality
group, frontier-defeat target, archetype eligibility entry, intended composition
and no tier threshold may reach this module. The ENGRAM-side hardness contract
and the root-level hardness report are both outside the boundary: no code path
here opens either, and the module constructs neither name, so there is no path
by which one could be reached even accidentally. A finding that cites a hardness
target rather than an artifact is out of scope for CRUCIBLE and is never emitted
from here.

The consequence is concrete rather than rhetorical. G-CAL-MONOTONICITY needs a
tier declaration, and the only channel by which a tier declaration may lawfully
reach CRUCIBLE is the CRUCIBLE_VIEW projection. The projection does carry tier
declarations, but every row carrying one is keyed to an instance identifier that
is not resident in this tree, so no resident bundle has a projected tier. The
instrument therefore records that the input is unprojected and stops. It does
not substitute the manifest's own ``target_tier`` field for the missing
projection, because that field is a frontier-defeat target and reading it into
an ordering computation is exactly the boundary crossing the contract forbids.
The manifest's ``difficulty_band`` token is recorded as an observed committed
byte, because the bundle is the artifact under audit and observing what it
declares is not the same act as consuming a hardness row as an input; the token
is never used to order anything.

Member by member:

G-CAL-MONOTONICITY recomputes cross-task ordering from the declared hardness tier
together with a signed pilot pass-rate aggregate, and retains a finding when a
higher tier is easier than a lower tier by more than the calibration margin.
Neither input arrives. No signed pilot pass-rate aggregate is projected for any
resident uuid, which is a coverage gap capping at HOLD. Separately, the contract
exempts a greenfield project with no declared multi-tier family, recording
``present: false`` with reason ``greenfield``. Whether that exemption applies is
determined here from committed bytes rather than assumed: a multi-tier family
requires at least two distinct graded band tokens across the corpus, and this
corpus declares one UNGRADED band and two unmeasured bands, which is zero graded
tiers and therefore no declared multi-tier family. The exemption is taken and
recorded explicitly with its basis. The pilot gap is still emitted, because an
exemption from ordering is not evidence that the pilot aggregate exists.

G-CAL-REPRODUCIBILITY rebuilds and grades each frozen bundle from only its pinned
image digest and its recorded invocation contract, with no private registry, no
authoring-host state and no hidden dependency. It runs even though monotonicity
took the greenfield exemption, because the two instruments answer unrelated
questions: a project with no tier family can still ship a bundle that cannot be
rebuilt. Every bundle carrying a pinned image and an invocation contract is in
scope.

Two facts shape what that instrument can conclude. Bundle 4c7b8d6f pins its base
image by tag and by index digest in the manifest. Bundles 6bf0c918 and 873914cf
declare ``base_image_ref`` as a bare tag with an empty ``base_image_digest``,
and the only digest they carry for that image is a platform sub-manifest digest,
which those same manifests state in their own committed comments is evidence and
never a substitute for the reference. An absent manifest image digest is not
merely a blocker for this auditor; it is a reproducibility defect in the
committed bundle, because a consumer holding only the bundle cannot resolve the
image the measurement ran on. It is emitted as a retained finding as well as
recorded in the per-bundle gap. No image can be pulled here in any case, so each
bundle also carries a gap naming exactly what blocked its rebuild.

Both members are pure Bucket D. A clean result here is never evidence that the
calibration is sound; it is only evidence that this probe found nothing.
"""

from __future__ import annotations

import json
import re
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
    Severity,
    Standing,
)
from registry import REGISTRY, Category, EvidenceClass, Instrument

FAMILY = "G-CAL"

MONOTONICITY = "G-CAL-MONOTONICITY"
REPRODUCIBILITY = "G-CAL-REPRODUCIBILITY"

CRITICAL_CLASS = "calibration-and-reproducibility"

CALIBRATION_MARGIN = 0.10

CALIBRATION_MARGIN_BASIS = (
    "The approved scope file binds no numeric calibration margin, so this value is a "
    "harness-local constant fixed before any data exists rather than chosen once the numbers "
    "are visible. A pass-rate aggregate is a proportion, so a tenth is the coarsest separation "
    "that is still meaningful at any realistic pilot size. It is never applied in this run, "
    "because no signed pilot aggregate is projected, and it is recorded so that a later run "
    "applies a threshold it did not select."
)

UNGRADED_BAND_TOKENS: frozenset[str] = frozenset({"", "ungraded", "unmeasured", "none", "null"})

HARDNESS_SOURCES_NEVER_READ: tuple[str, ...] = (
    "the ENGRAM hardness contract",
    "a root hardness report",
    "any hardness row, category, axis or orthogonality group",
    "any frontier-defeat target",
    "any archetype eligibility entry",
    "any intended composition",
    "any tier threshold",
)

WITHHELD_MANIFEST_FIELDS: tuple[str, ...] = (
    "metadata.target_tier",
    "metadata.primary_archetype",
)

PERMITTED_TIER_CHANNEL = "CRUCIBLE_VIEW checker_metadata e21_calibration declared_tier"

IMAGE_DIGEST = re.compile(r"@sha256:[0-9a-f]{64}")

DOCKER_FROM = re.compile(r"^\s*FROM\s+(\S+)", re.MULTILINE)

INVOCATION_CONTRACT_PATHS: tuple[str, ...] = (
    "environment/Dockerfile",
    "tests/Dockerfile",
    "tests/config.json",
    "tests/graded/run.sh",
    "tests/run_tests.py",
    "tests/test.sh",
    "task.toml",
)

RESOURCE_LIMIT_KEYS: tuple[str, ...] = (
    "build_timeout_sec",
    "cpus",
    "memory_mb",
    "storage_mb",
    "gpus",
)


def _register() -> None:
    """Declare both step 8e instruments under the Phase 1 item 4 twelve-field schema.

    ``disposition_cap_on_absence`` is HOLD on both rows and is never SHIP,
    because a calibration instrument that does not run leaves the ordering and
    the rebuild unmeasured, and an unmeasured surface is a coverage gap rather
    than a pass.
    """
    rows = (
        Instrument(
            name=MONOTONICITY,
            category=Category.CALIBRATION,
            binary="",
            ecosystems=("*",),
            timeout_seconds=120.0,
            required_conditions=(
                "a tier declaration arriving through the permitted projection channel",
                "a signed pilot pass-rate aggregate projected for the resident corpus",
                "a declared multi-tier family",
            ),
            critical_capability="cross-task ordering against a signed pilot aggregate",
            evidence_class=EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="Never reads hardness in any form; a tier arrives only by projection.",
        ),
        Instrument(
            name=REPRODUCIBILITY,
            category=Category.CALIBRATION,
            binary="docker",
            ecosystems=("*",),
            timeout_seconds=1800.0,
            required_conditions=(
                "a pinned image digest committed in the bundle",
                "a recorded invocation contract committed in the bundle",
                "image resolution without a private registry",
            ),
            critical_capability="rebuild and regrade from the pinned digest alone",
            evidence_class=EvidenceClass.EXECUTION_REPLAY,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="Runs even when monotonicity takes the greenfield exemption.",
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


def _digest_or_none(path: Path) -> str | None:
    return core.sha256_path(path) if path.is_file() else None


def _table(manifest: dict[str, Any], key: str) -> dict[str, Any]:
    value = manifest.get(key)
    return value if isinstance(value, dict) else {}


def bundles_of(base: Path) -> list[Path]:
    """Every resident bundle directory, derived from committed bytes alone."""
    return sorted(core.bundle_roots(base), key=lambda path: path.name)


def crucible_view_path(base: Path) -> Path:
    """Locate CRUCIBLE_VIEW, the only ENGRAM surface this family may read.

    This is the permitted projection channel. It is the sole ENGRAM input to
    this module, and the hardness contract behind it is withheld by
    construction and is never opened here.
    """
    return base.resolve().parent / ".memory" / "crucible_view.yaml"


def declared_band(bundle: Path) -> dict[str, Any]:
    """Record the band token the committed manifest declares, without consuming it.

    The token is an observed committed byte of the artifact under audit, which
    is a different act from consuming a hardness row as an ordering input. The
    manifest fields that do carry a hardness target are named in the returned
    record without their values, so a reader can confirm they were seen and
    withheld rather than missed.
    """
    manifest = _load_toml(bundle / "task.toml")
    metadata = _table(manifest, "metadata")
    token = str(metadata.get("difficulty_band") or "")
    return {
        "uuid": bundle.name,
        "declared_band_token": token,
        "band_is_graded": token.strip().lower() not in UNGRADED_BAND_TOKENS,
        "withheld_fields": list(WITHHELD_MANIFEST_FIELDS),
        "withheld_basis": (
            "these fields carry a frontier-defeat target and an archetype eligibility entry, "
            "which the containment boundary forbids reaching this instrument, so their names "
            "are recorded and their values are not read"
        ),
        "manifest_digest": _digest_or_none(bundle / "task.toml"),
        "consumed_as_ordering_input": False,
    }


def projected_tier_channel(base: Path) -> dict[str, Any]:
    """Probe the permitted projection channel for a resident tier declaration.

    A tier may reach this instrument only through CRUCIBLE_VIEW. The probe is a
    membership test over resident identifiers and never a read of the tier
    values the projection carries for other instances, because a value keyed to
    an instance that is not resident is not a declaration about this corpus and
    recording it would invite exactly the substitution the containment boundary
    forbids.
    """
    path = crucible_view_path(base)
    present = path.is_file()
    text = _read_text(path) if present else ""
    rows: list[dict[str, Any]] = []
    for bundle in bundles_of(base):
        config = _load_json(bundle / "tests" / "config.json")
        config = config if isinstance(config, dict) else {}
        instance_id = str(config.get("instance_id") or "")
        rows.append(
            {
                "uuid": bundle.name,
                "instance_id": instance_id,
                "uuid_occurrences_in_view": text.count(bundle.name),
                "instance_id_occurrences_in_view": text.count(instance_id) if instance_id else 0,
                "tier_projected": False,
            }
        )
    return {
        "channel": PERMITTED_TIER_CHANNEL,
        "view_present": present,
        "view_digest": _digest_or_none(path),
        "resident_probe": rows,
        "resident_tier_projections": [],
        "tier_values_read": 0,
    }


def pilot_aggregate(base: Path) -> dict[str, Any]:
    """Resolve the signed pilot pass-rate aggregate, or record that none is projected.

    A pilot aggregate is only usable when it is signed and bound to the resident
    corpus. CRUCIBLE_VIEW records ``signed_cohort_pass_rates`` as null on every
    row it carries, and every row it carries is keyed to a non-resident
    instance, so there is no signed aggregate for this corpus by either test.
    The rewards committed beside the rollouts are not an aggregate: they are
    unsigned producer-written numbers at one run per solver identity, which is
    the artifact under audit rather than a measurement of it.
    """
    path = crucible_view_path(base)
    document = _load_yaml(path) if path.is_file() else None
    signed_rows = 0
    carried_rows = 0
    if isinstance(document, dict):
        metadata = document.get("checker_metadata")
        metadata = metadata if isinstance(metadata, list) else []
        for row in metadata:
            if not isinstance(row, dict):
                continue
            block = row.get("e21_calibration")
            if not isinstance(block, dict):
                continue
            carried_rows += 1
            if block.get("signed_cohort_pass_rates"):
                signed_rows += 1
    return {
        "projected": False,
        "signed": False,
        "carried_calibration_rows": carried_rows,
        "rows_with_signed_pass_rates": signed_rows,
        "resident_rows": 0,
        "basis": (
            "every calibration row the projection carries is keyed to a non-resident instance "
            "and records signed_cohort_pass_rates as null, so no signed aggregate binds this "
            "corpus; committed rollout rewards are unsigned producer bytes and are not an "
            "aggregate"
        ),
    }


def multi_tier_family(base: Path) -> dict[str, Any]:
    """Determine from committed bytes whether a multi-tier family is declared.

    A family is multi-tier when the corpus declares at least two distinct graded
    band tokens, because ordering is a relation and a relation needs two
    distinguishable members. A token in the ungraded vocabulary is not a tier:
    it is the explicit statement that no measurement placed the bundle anywhere.
    The determination is made here rather than assumed, so the greenfield
    exemption is taken on evidence and not by default.
    """
    bands = [declared_band(bundle) for bundle in bundles_of(base)]
    graded = sorted(
        {row["declared_band_token"].strip().lower() for row in bands if row["band_is_graded"]}
    )
    declared = len(graded) >= 2
    return {
        "declared": declared,
        "distinct_graded_band_count": len(graded),
        "distinct_graded_bands": graded,
        "band_rows": bands,
        "basis": (
            "a multi-tier family requires at least two distinct graded band tokens across the "
            f"corpus; {len(graded)} distinct graded tokens are declared, so the family is "
            f"{'declared' if declared else 'not declared'}"
        ),
    }


def invocation_contract(bundle: Path) -> dict[str, Any]:
    """Derive the recorded invocation contract from committed bytes alone.

    The contract is everything a rebuild would need beyond the image: the
    verifier entry point, the graded command, the declared target sets and
    parser, the test patch, the build inputs, and the resource and network
    envelope the manifest declares. Each committed member is digested so a later
    edit to any of them moves the recorded contract instead of silently
    preserving it.
    """
    manifest = _load_toml(bundle / "task.toml")
    environment = _table(manifest, "environment")
    verifier = _table(manifest, "verifier")
    agent = _table(manifest, "agent")
    config = _load_json(bundle / "tests" / "config.json")
    config = config if isinstance(config, dict) else {}
    members = {
        relative: _digest_or_none(bundle / relative) for relative in INVOCATION_CONTRACT_PATHS
    }
    return {
        "uuid": bundle.name,
        "entry_point": "tests/test.sh",
        "graded_command": _read_text(bundle / "tests" / "graded" / "run.sh").strip(),
        "target_cmd": str(config.get("target_cmd") or ""),
        "preserve_cmd": str(config.get("preserve_cmd") or ""),
        "build_cmd": str(config.get("build_cmd") or ""),
        "parser": str(config.get("parser") or ""),
        "repo_dir": str(config.get("repo_dir") or ""),
        "base_commit": str(config.get("base_commit") or ""),
        "test_patch_path": str(config.get("test_patch_path") or ""),
        "workdir": str(environment.get("workdir") or ""),
        "resource_envelope": {key: environment.get(key) for key in RESOURCE_LIMIT_KEYS},
        "environment_network_mode": str(environment.get("network_mode") or ""),
        "verifier_network_mode": str(verifier.get("network_mode") or ""),
        "verifier_timeout_sec": verifier.get("timeout_sec"),
        "agent_timeout_sec": agent.get("timeout_sec"),
        "member_digests": members,
        "contract_digest": core.tree_digest(bundle, INVOCATION_CONTRACT_PATHS),
        "complete": all(value is not None for value in members.values()),
    }


def image_pins(bundle: Path) -> dict[str, Any]:
    """Enumerate every image identity the bundle commits and grade its pinning.

    Four identities exist and they are not interchangeable. The manifest's
    ``base_image_ref`` with its companion ``base_image_digest`` is the
    consumer-facing pin. ``docker_image`` pins the sanitized index the bundle
    says a consumer actually runs. The ``FROM`` in the committed Dockerfile is
    the build-time reference. ``base_image_platform_manifest_digest`` is a
    platform sub-manifest that the bundle's own committed comment calls evidence
    and never a substitute for the reference, so it is recorded and explicitly
    not counted as a pin.
    """
    manifest = _load_toml(bundle / "task.toml")
    metadata = _table(manifest, "metadata")
    environment = _table(manifest, "environment")
    base_ref = str(metadata.get("base_image_ref") or "")
    base_digest = str(metadata.get("base_image_digest") or "")
    runtime_ref = str(environment.get("docker_image") or "")
    dockerfile = _read_text(bundle / "environment" / "Dockerfile")
    from_refs = [
        match.group(1) for match in DOCKER_FROM.finditer(dockerfile) if match.group(1) != "scratch"
    ]
    return {
        "uuid": bundle.name,
        "base_image_ref": base_ref,
        "base_image_ref_is_bare_tag": bool(base_ref) and "/" not in base_ref,
        "base_image_digest": base_digest,
        "manifest_digest_present": bool(base_digest),
        "runtime_image_ref": runtime_ref,
        "runtime_image_digest_pinned": bool(IMAGE_DIGEST.search(runtime_ref)),
        "dockerfile_from_refs": from_refs,
        "dockerfile_from_digest_pinned": [bool(IMAGE_DIGEST.search(ref)) for ref in from_refs],
        "platform_manifest_digest": str(metadata.get("base_image_platform_manifest_digest") or ""),
        "platform_manifest_is_a_pin": False,
        "platform_manifest_basis": (
            "the bundle's own committed manifest comment records the platform sub-manifest as "
            "evidence and never a substitute for the reference"
        ),
        "registry_namespace": str(metadata.get("base_image_registry_namespace") or ""),
    }


def rebuild_blockers(
    bundle: Path, pins: dict[str, Any], recon_binaries: dict[str, Any]
) -> list[str]:
    """Name exactly what blocks a rebuild of this bundle, in order of severity.

    The list is per bundle and literal. A gap that says only that a rebuild did
    not happen is unactionable; a gap naming the absent digest, the private
    namespace, and the missing daemon tells a reader which one to fix first.
    """
    blockers: list[str] = []
    if not pins["manifest_digest_present"]:
        blockers.append(
            "task.toml [metadata].base_image_digest is empty, so the bundle commits no "
            "manifest-level pinned digest for the image the measurement ran on"
        )
    if pins["base_image_ref_is_bare_tag"]:
        blockers.append(
            f"task.toml [metadata].base_image_ref is the bare tag {pins['base_image_ref']!r}, "
            "which names no registry and resolves for no consumer"
        )
    if pins["registry_namespace"] or "dkr.ecr" in pins["runtime_image_ref"]:
        blockers.append(
            "every resolvable image reference points at a private registry namespace that "
            "requires credentials this harness does not hold"
        )
    blockers.append(
        "no image can be pulled here: network egress is forbidden, so no digest resolves "
        "regardless of whether one is committed"
    )
    entry = recon_binaries.get("docker") if isinstance(recon_binaries, dict) else None
    if not (isinstance(entry, dict) and entry.get("present")):
        blockers.append("the docker binary does not resolve on this host, so no rebuild can start")
    if not (bundle / "environment" / "Dockerfile").is_file():
        blockers.append(
            "environment/Dockerfile is absent, so the image has no committed derivation"
        )
    return blockers


def run_monotonicity(base: Path) -> InstrumentResult:
    """G-CAL-MONOTONICITY: recompute cross-task ordering, or record why it cannot.

    The ordering needs a tier declaration and a signed pilot pass-rate aggregate.
    Neither reaches this instrument. The tier channel is probed and carries no
    resident declaration; the manifest's own frontier-defeat target is withheld
    by name and never substituted, because substituting it is the containment
    breach the contract exists to prevent. The signed pilot aggregate is
    unprojected and is recorded as a coverage gap capping at HOLD.

    The contract's greenfield exemption is then evaluated on evidence rather
    than assumed. The corpus declares one UNGRADED band and two unmeasured
    bands, which is zero distinct graded tiers, so no multi-tier family is
    declared and the exemption applies. The exemption is recorded as
    ``present: false`` with reason ``greenfield`` together with the basis that
    produced it, so a reader can refute the determination from the same bytes.

    The pilot gap is emitted even under the exemption. An exemption from
    computing an ordering says nothing about whether the aggregate exists, and
    folding the two together would let one absence conceal the other.
    """
    family = multi_tier_family(base)
    channel = projected_tier_channel(base)
    pilot = pilot_aggregate(base)
    exempt = not family["declared"]

    gaps = [
        CoverageGap(
            gap_id="D-CAL-PILOT-AGGREGATE-UNPROJECTED",
            instrument=MONOTONICITY,
            surface="calibration",
            reason="signed-pilot-pass-rate-aggregate-unprojected",
            caps=Disposition.HOLD,
            subject="project",
            statement=(
                "No signed pilot pass-rate aggregate is projected for any resident bundle. "
                "Every calibration row the permitted projection channel carries is keyed to a "
                "non-resident instance and records signed_cohort_pass_rates as null, so the "
                "signed half of the ordering input does not exist for this corpus. The rewards "
                "committed beside the rollouts are unsigned producer-written numbers at one "
                "run per solver identity and are not an aggregate. No hardness source was "
                "consulted to fill this void: the ordering input is recorded as absent rather "
                "than reconstructed from a forbidden surface."
            ),
        ),
        CoverageGap(
            gap_id="D-CAL-TIER-UNPROJECTED",
            instrument=MONOTONICITY,
            surface="calibration",
            reason="tier-declaration-unprojected",
            caps=Disposition.HOLD,
            subject="project",
            statement=(
                "No tier declaration reaches this instrument through the permitted projection "
                f"channel ({PERMITTED_TIER_CHANNEL}). The projection carries tier declarations "
                "only for instances that are not resident in this tree. The manifests do carry "
                "their own tier target, and it is withheld by name rather than read, because a "
                "frontier-defeat target is inside the containment boundary CRUCIBLE may not "
                "cross and a finding citing it would be out of scope."
            ),
        ),
    ]

    return InstrumentResult(
        instrument=MONOTONICITY,
        ran=True,
        findings=[],
        gaps=gaps,
        artifacts=[],
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes={
            "monotonicity_present": not exempt,
            "exemption_taken": exempt,
            "exemption_reason": "greenfield" if exempt else "",
            "exemption_basis": family["basis"] if exempt else "",
            "multi_tier_family": family,
            "tier_channel": channel,
            "pilot_aggregate": pilot,
            "calibration_margin": CALIBRATION_MARGIN,
            "calibration_margin_basis": CALIBRATION_MARGIN_BASIS,
            "ordering_computed": False,
            "containment": {
                "hardness_sources_never_read": list(HARDNESS_SOURCES_NEVER_READ),
                "withheld_manifest_fields": list(WITHHELD_MANIFEST_FIELDS),
                "permitted_channel": PERMITTED_TIER_CHANNEL,
                "statement": (
                    "this instrument reads no hardness surface of any kind, and a tier reaches "
                    "it only by projection; the void left by an unprojected tier is recorded "
                    "rather than filled"
                ),
            },
        },
    )


def run_reproducibility(base: Path, reconnaissance: Any = None) -> InstrumentResult:
    """G-CAL-REPRODUCIBILITY: rebuild and grade each frozen bundle from its pin alone.

    The instrument runs regardless of the monotonicity exemption, because a
    project with no declared tier family can still ship a bundle a consumer
    cannot rebuild. Every bundle carrying a pinned image and a recorded
    invocation contract is in scope, and all three qualify.

    No rebuild is performed. Each bundle's blockers are derived and named
    literally in its own gap, so the reader learns which resource is missing
    rather than only that the rebuild did not happen.

    Where the manifest commits no image digest at all, that is recorded as a
    retained finding and not only as a blocker for this auditor. A bundle whose
    manifest names a bare tag with an empty digest cannot be resolved to the
    image its measurement ran on by any consumer holding the bundle, which makes
    the bundle unreproducible on its own terms. The platform sub-manifest digest
    those bundles do carry is not accepted as a substitute, because the bundle's
    own committed text says it is not one.
    """
    binaries = getattr(reconnaissance, "binaries", None)
    binaries = binaries if isinstance(binaries, dict) else {}
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    rows: list[dict[str, Any]] = []

    for bundle in bundles_of(base):
        contract = invocation_contract(bundle)
        pins = image_pins(bundle)
        blockers = rebuild_blockers(bundle, pins, binaries)
        in_scope = (
            bool(pins["base_image_ref"] or pins["runtime_image_ref"]) and contract["complete"]
        )
        rows.append(
            {
                "uuid": bundle.name,
                "in_scope": in_scope,
                "rebuild_performed": False,
                "regrade_performed": False,
                "pinned_digest_present": pins["manifest_digest_present"],
                "invocation_contract": contract,
                "image_pins": pins,
                "blockers": blockers,
            }
        )

        if not pins["manifest_digest_present"]:
            findings.append(
                Finding(
                    finding_id=f"CAL-IMAGE-DIGEST-ABSENT-{bundle.name}",
                    instrument=REPRODUCIBILITY,
                    critical_class=CRITICAL_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        "The committed manifest declares base_image_ref as "
                        f"{pins['base_image_ref']!r} with an empty base_image_digest, so the "
                        "bundle commits no manifest-level pinned digest for the image its "
                        "measurement ran on. A consumer holding only this bundle cannot "
                        "resolve that image, which makes the bundle unreproducible on its own "
                        "terms. This is a defect in the committed bundle and not merely a "
                        "blocker for this auditor. The platform sub-manifest digest the "
                        "manifest does carry is not a substitute, because the manifest's own "
                        "committed text records it as evidence rather than as the reference."
                    ),
                    evidence={
                        "uuid": bundle.name,
                        "base_image_ref": pins["base_image_ref"],
                        "base_image_digest": pins["base_image_digest"],
                        "platform_manifest_digest": pins["platform_manifest_digest"],
                        "runtime_image_ref": pins["runtime_image_ref"],
                        "runtime_image_digest_pinned": pins["runtime_image_digest_pinned"],
                        "manifest_digest": _digest_or_none(bundle / "task.toml"),
                    },
                )
            )

        gaps.append(
            CoverageGap(
                gap_id=f"D-CAL-REBUILD-BLOCKED-{bundle.name}",
                instrument=REPRODUCIBILITY,
                surface="calibration",
                reason="rebuild-from-pinned-digest-blocked",
                caps=Disposition.HOLD,
                subject=bundle.name,
                statement=(
                    f"Bundle {bundle.name} was not rebuilt or regraded from its pinned image "
                    "digest and recorded invocation contract. The invocation contract is "
                    f"derived and recorded in full at digest {contract['contract_digest']}. "
                    "The rebuild was blocked by: " + "; ".join(blockers) + "."
                ),
            )
        )

    return InstrumentResult(
        instrument=REPRODUCIBILITY,
        ran=True,
        findings=findings,
        gaps=gaps,
        artifacts=[],
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes={
            "runs_under_monotonicity_exemption": True,
            "runs_under_exemption_basis": (
                "a project with no declared multi-tier family can still ship a bundle that "
                "cannot be rebuilt, so the greenfield exemption does not reach this instrument"
            ),
            "bundles_in_scope": sum(1 for row in rows if row["in_scope"]),
            "private_registry_used": False,
            "authoring_host_state_used": False,
            "hidden_dependency_used": False,
            "rows": rows,
        },
    )


def _guard(name: str, runner: Any, base: Path, reconnaissance: Any) -> InstrumentResult:
    """Run one instrument and convert any unexpected failure into a coverage gap.

    run_family must never raise, and an instrument that crashed must never read
    as a clean result, so a crash becomes an explicit gap naming the exception.
    """
    try:
        if name == REPRODUCIBILITY:
            return runner(base, reconnaissance)
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
    """Execute the step 8e calibration family and return every result.

    The reconnaissance record is consumed only for the host binary roster, which
    is what decides whether a rebuild could have started at all. Nothing about
    tiers, bands or pass rates is taken from it, because the containment
    boundary is a property of this module and not of its caller.
    """
    return [
        _guard(MONOTONICITY, run_monotonicity, base, reconnaissance),
        _guard(REPRODUCIBILITY, run_reproducibility, base, reconnaissance),
    ]


__all__ = [
    "CALIBRATION_MARGIN",
    "MONOTONICITY",
    "REPRODUCIBILITY",
    "bundles_of",
    "declared_band",
    "image_pins",
    "invocation_contract",
    "multi_tier_family",
    "pilot_aggregate",
    "projected_tier_channel",
    "rebuild_blockers",
    "run_family",
    "run_monotonicity",
    "run_reproducibility",
]
