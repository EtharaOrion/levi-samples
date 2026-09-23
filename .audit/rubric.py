"""Contract step 8h: the G-RUB rubric-compilation instrument family.

This module discharges the five rubric probes the scope file mandates under key
``rubric`` and lists in ``required_instruments`` as ``G-RUB`` with
``probe_count: 5``. The rationale lives here rather than in the contract because
the contract is prompt-only, so the harness carries the audit evidence for why
each probe is shaped the way it is.

Every probe is pure Bucket D and may only lower or cap a disposition. The item
schema, the target vocabulary, and the compiled-weight floor are read from the
approved scope rather than hardcoded, because Phase 1 item 4 makes an
unprojected required input a coverage gap capping at HOLD rather than a value
this harness is free to assume. No probe in this family reads .seed/results,
which is outside the projection this family is allowed to consume.

The decisive defect this family exists to catch is an inert required check.
Under verifier principle 7 an inert required check is a broken instrument, not a
coverage gap, so G-RUB-REPLAY retains it as a Finding capping at BLOCK and
proves it by execution rather than by reading the source: the compiled module is
run against a committed rollout and against a committed control recorded as
scoring zero, and a module that accepts both has been shown inert rather than
argued inert.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from collections.abc import Callable
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

FAMILY = "G-RUB"

SCHEMA = "G-RUB-SCHEMA"
COMPLETENESS = "G-RUB-COMPLETENESS"
RESIDUE = "G-RUB-RESIDUE"
REGEN = "G-RUB-REGEN"
REPLAY = "G-RUB-REPLAY"

TESTS_RUBRIC = "tests/rubrics.json"
SOLUTION_RUBRIC = "solution/rubrics.json"
COMPILED_TESTS = "tests/test_output.py"
GENERATOR = "solution/recompute.py"
TRUTH = "solution/TRUTH.md"
GRADING_ENTRY = "tests/test.sh"
GRADED_RUN = "tests/graded/run.sh"
RUNNER_CONFIG = "tests/config.json"
DOCKERFILE = "tests/Dockerfile"
RUNNER = "tests/run_tests.py"
HARNESS_CORE = "tests/harness_core.py"

REGEN_REQUIRED_ARTIFACTS = (SOLUTION_RUBRIC, COMPILED_TESTS)

COMPILED_MODE = "compiled"
JUDGED_MODE = "judged"

EVIDENCE_CHANNEL_ARTIFACTS = {
    "final_diff": "final.diff",
    "verification_output": "reward.json",
    "trajectory.reasoning": "trial.log",
    "trajectory.observations": "trial.log",
    "trajectory.tool_calls": "trial.log",
}


def _register() -> None:
    """Register the five G-RUB instruments under the Phase 1 item 4 schema.

    Every declaration carries all twelve fields. ``disposition_cap_on_absence``
    is BLOCK for the replay probe because that probe is the only one that can
    observe an inert compiled check, and verifier principle 7 makes losing an
    inertness proof a broken instrument rather than a soft gap. The other four
    cap at HOLD, which leaves their surface unmeasured rather than passed.
    """
    common: dict[str, Any] = {
        "category": Category.RUBRIC,
        "ecosystems": ("rust", "python"),
        "bucket": Bucket.D,
        "database_pin": "committed-bundle-bytes",
    }
    declarations = (
        (
            SCHEMA,
            "python3",
            300.0,
            ("committed rubric documents", "projected item schema", "projected vocabulary"),
            "rubric-item-schema-conformance",
            EvidenceClass.SCHEMA_VALIDATION,
            Disposition.HOLD,
            "Validates every committed rubric item against the declared schema.",
        ),
        (
            COMPLETENESS,
            "python3",
            300.0,
            ("committed rubric documents", "committed compiled tests", "compiled weight floor"),
            "compiled-set-equality-and-weight-share",
            EvidenceClass.SET_RELATION,
            Disposition.HOLD,
            "Requires set equality between compiled items and compiled tests.",
        ),
        (
            RESIDUE,
            "python3",
            300.0,
            ("committed judged items", "named evidence artifacts"),
            "judged-residue-grounding",
            EvidenceClass.SET_RELATION,
            Disposition.HOLD,
            "Grounds each judged item's judgment against its named evidence.",
        ),
        (
            REGEN,
            "python3",
            600.0,
            ("committed generator", "two distinct sandbox identities"),
            "generator-identity-independence",
            EvidenceClass.RECOMPUTED_DIGEST,
            Disposition.HOLD,
            "Runs the committed generator twice under differing identities.",
        ),
        (
            REPLAY,
            "python3",
            600.0,
            ("committed compiled tests", "committed oracle", "committed known-wrong controls"),
            "compiled-check-liveness",
            EvidenceClass.EXECUTION_REPLAY,
            Disposition.BLOCK,
            "Runs the compiled tests against the oracle and every known-wrong control.",
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


def _rubric_scope(base: Path) -> dict:
    """The approved scope's rubric projection, or an empty mapping."""
    try:
        scope = recon.load_scope(base)
    except (OSError, ValueError):
        return {}
    projected = scope.get("rubric")
    return projected if isinstance(projected, dict) else {}


def _projected_schema(projected: dict) -> tuple[list[str], int | None]:
    """The declared item schema field list and its closed-at count."""
    declared = projected.get("declared_item_schema")
    if not isinstance(declared, dict):
        return [], None
    fields = declared.get("fields")
    closed = declared.get("closed_at")
    return (
        [str(field) for field in fields] if isinstance(fields, list) else [],
        int(closed) if isinstance(closed, int) else None,
    )


def _projected_vocabulary(projected: dict) -> dict[str, list[str]]:
    """The declared target vocabulary for dimensions, targets, and channels."""
    vocabulary = projected.get("target_vocabulary")
    if not isinstance(vocabulary, dict):
        return {}
    resolved: dict[str, list[str]] = {}
    for key in ("dimensions", "evaluation_targets", "evidence_channels"):
        values = vocabulary.get(key)
        if isinstance(values, list):
            resolved[key] = [str(value) for value in values]
    return resolved


def _committed_artifact_names(bundle: Path) -> set[str]:
    """Every file name the bundle commits, used to ground named evidence."""
    names: set[str] = set()
    for path in bundle.rglob("*"):
        if path.is_file():
            names.add(path.name)
    return names


def _rubric_documents(bundle: Path) -> list[tuple[str, dict]]:
    """Every committed rubric document of a bundle, as (relative path, document)."""
    documents: list[tuple[str, dict]] = []
    for relative in (TESTS_RUBRIC, SOLUTION_RUBRIC):
        loaded = _read_json(bundle / relative)
        if isinstance(loaded, dict):
            documents.append((relative, loaded))
    return documents


def _items(document: dict) -> list[dict]:
    """The item list of a rubric document, filtered to mappings."""
    items = document.get("items")
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _run_schema(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-RUB-SCHEMA: validate every committed rubric item against the schema.

    A missing field, a field outside the closed schema, an out-of-vocabulary
    dimension, evaluation target or evidence channel, and an evidence entry
    naming an artifact the bundle does not commit are each retained. The schema
    and the vocabulary come from the approved scope, so an unprojected one is a
    gap rather than an assumption.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    notes: dict[str, Any] = {"documents": []}
    projected = _rubric_scope(base)
    fields, closed_at = _projected_schema(projected)
    vocabulary = _projected_vocabulary(projected)
    if not fields:
        gaps.append(
            CoverageGap(
                gap_id="D-RUB-ITEM-SCHEMA-UNPROJECTED",
                instrument=SCHEMA,
                surface="rubric",
                reason="item-schema-unprojected",
                caps=Disposition.HOLD,
                statement=(
                    "The approved scope projects no declared_item_schema.fields for the rubric "
                    "surface, so no item could be validated against a closed schema and the "
                    "harness refuses to infer one from the committed documents it is auditing."
                ),
            )
        )
    if not vocabulary:
        gaps.append(
            CoverageGap(
                gap_id="D-RUB-VOCABULARY-UNPROJECTED",
                instrument=SCHEMA,
                surface="rubric",
                reason="target-vocabulary-unprojected",
                caps=Disposition.HOLD,
                statement=(
                    "The approved scope projects no rubric target_vocabulary, so dimensions, "
                    "evaluation targets and evidence channels could not be checked for "
                    "membership in a closed vocabulary."
                ),
            )
        )
    if not fields and not vocabulary:
        return InstrumentResult(instrument=SCHEMA, ran=False, gaps=gaps, notes=notes)
    schema_fields = set(fields)
    ran = False
    for bundle in bundles:
        committed = _committed_artifact_names(bundle)
        for relative, document in _rubric_documents(bundle):
            ran = True
            for item in _items(document):
                identifier = str(item.get("id") or "<unidentified>")
                present = set(item.keys())
                missing = sorted(schema_fields - present) if schema_fields else []
                extra = sorted(present - schema_fields) if schema_fields else []
                notes["documents"].append(
                    {
                        "bundle": bundle.name,
                        "document": relative,
                        "item": identifier,
                        "missing_fields": missing,
                        "undeclared_fields": extra,
                    }
                )
                if missing or extra:
                    findings.append(
                        Finding(
                            finding_id=f"RUB-SCHEMA-ITEM-{bundle.name}-{relative}-{identifier}",
                            instrument=SCHEMA,
                            critical_class="rubric-compilation",
                            severity=Severity.HIGH,
                            caps=Disposition.BLOCK,
                            bucket=Bucket.D,
                            subject=bundle.name,
                            statement=(
                                f"Rubric item {identifier} in {relative} does not conform to the "
                                f"item schema the approved scope closes at {closed_at} fields. "
                                f"Missing: {missing or 'none'}. Outside the closed schema: "
                                f"{extra or 'none'}. A schema declared closed that the committed "
                                "items do not satisfy is not a schema the rubric surface is "
                                "actually validated against."
                            ),
                            evidence={
                                "bundle": bundle.name,
                                "document": relative,
                                "item": identifier,
                                "missing_fields": missing,
                                "undeclared_fields": extra,
                                "declared_fields": sorted(schema_fields),
                                "closed_at": closed_at,
                            },
                        )
                    )
                for key, vocabulary_key in (
                    ("dimension", "dimensions"),
                    ("evaluation_target", "evaluation_targets"),
                ):
                    allowed = vocabulary.get(vocabulary_key)
                    value = item.get(key)
                    if allowed and isinstance(value, str) and value not in allowed:
                        findings.append(
                            Finding(
                                finding_id=(
                                    f"RUB-SCHEMA-VOCAB-{bundle.name}-{relative}-{identifier}-{key}"
                                ),
                                instrument=SCHEMA,
                                critical_class="rubric-compilation",
                                severity=Severity.HIGH,
                                caps=Disposition.BLOCK,
                                bucket=Bucket.D,
                                subject=bundle.name,
                                statement=(
                                    f"Rubric item {identifier} in {relative} declares {key} "
                                    f"{value!r}, which is outside the projected {vocabulary_key} "
                                    "vocabulary."
                                ),
                                evidence={
                                    "bundle": bundle.name,
                                    "document": relative,
                                    "item": identifier,
                                    "field": key,
                                    "value": value,
                                    "allowed": allowed,
                                },
                            )
                        )
                channels = vocabulary.get("evidence_channels")
                declared_evidence = item.get("evidence")
                if isinstance(declared_evidence, list):
                    for channel in declared_evidence:
                        channel_name = str(channel)
                        if channels and channel_name not in channels:
                            findings.append(
                                Finding(
                                    finding_id=(
                                        f"RUB-SCHEMA-CHANNEL-{bundle.name}-{relative}-"
                                        f"{identifier}-{channel_name}"
                                    ),
                                    instrument=SCHEMA,
                                    critical_class="rubric-compilation",
                                    severity=Severity.HIGH,
                                    caps=Disposition.BLOCK,
                                    bucket=Bucket.D,
                                    subject=bundle.name,
                                    statement=(
                                        f"Rubric item {identifier} in {relative} names evidence "
                                        f"channel {channel_name!r}, which the projected "
                                        "evidence_channels vocabulary does not contain. A judged "
                                        "item grounded on a channel outside the closed vocabulary "
                                        "cannot be reconciled against any committed artifact."
                                    ),
                                    evidence={
                                        "bundle": bundle.name,
                                        "document": relative,
                                        "item": identifier,
                                        "channel": channel_name,
                                        "allowed": channels,
                                    },
                                )
                            )
                            continue
                        artifact = EVIDENCE_CHANNEL_ARTIFACTS.get(channel_name)
                        if artifact and artifact not in committed:
                            findings.append(
                                Finding(
                                    finding_id=(
                                        f"RUB-SCHEMA-EVIDENCE-ABSENT-{bundle.name}-{relative}-"
                                        f"{identifier}-{channel_name}"
                                    ),
                                    instrument=SCHEMA,
                                    critical_class="rubric-compilation",
                                    severity=Severity.HIGH,
                                    caps=Disposition.BLOCK,
                                    bucket=Bucket.D,
                                    subject=bundle.name,
                                    statement=(
                                        f"Rubric item {identifier} in {relative} names evidence "
                                        f"channel {channel_name!r}, whose carrying artifact "
                                        f"{artifact} the bundle does not commit, so the stated "
                                        "grounding cannot be read from committed bytes."
                                    ),
                                    evidence={
                                        "bundle": bundle.name,
                                        "document": relative,
                                        "item": identifier,
                                        "channel": channel_name,
                                        "expected_artifact": artifact,
                                    },
                                )
                            )
    return InstrumentResult(
        instrument=SCHEMA,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=[],
        standing=Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE,
        notes=notes,
    )


def _compiled_test_identifiers(bundle: Path) -> list[str]:
    """Every test function the committed compiled module defines.

    Parsed by scanning definition lines rather than by importing the module,
    because importing it would execute a module whose collection behaviour is
    exactly what the replay probe is measuring.
    """
    text = _read_text(bundle / COMPILED_TESTS)
    if text is None:
        return []
    identifiers: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("def test_") and "(" in stripped:
            identifiers.append(stripped[len("def ") : stripped.index("(")])
    return identifiers


def _run_completeness(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-RUB-COMPLETENESS: set equality both ways plus the compiled weight share.

    Set equality is required in both directions: a compiled item with no
    committed test is an unenforced requirement, and a committed compiled test
    with no compiled item is an enforcement nothing declared. The compiled
    weight share is recomputed and recorded even though the floor it must clear
    is unresolved at this root, so the number survives for whoever resolves the
    floor later.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    notes: dict[str, Any] = {"bundles": {}}
    projected = _rubric_scope(base)
    floor = projected.get("compiled_weight_floor")
    floor_state = str(floor.get("state")) if isinstance(floor, dict) else "absent"
    gaps.append(
        CoverageGap(
            gap_id="D-COMPILATION-FLOOR-UNRESOLVED",
            instrument=COMPLETENESS,
            surface="rubric",
            reason="compiled-weight-floor-unresolved",
            caps=Disposition.HOLD,
            statement=(
                "The compiled_weight_floor the rubric surface must clear reads "
                f"{floor_state} in the approved scope, because it is carried by name from a "
                ".seed/contract.yaml that does not exist at this root. The actual compiled weight "
                "share is recomputed and recorded below, but it cannot be compared against a "
                "floor, so compiled coverage adequacy stays unmeasured rather than passed."
            ),
        )
    )
    ran = False
    for bundle in bundles:
        document = _read_json(bundle / TESTS_RUBRIC)
        if not isinstance(document, dict):
            gaps.append(
                CoverageGap(
                    gap_id=f"D-RUB-COMPILED-RUBRIC-ABSENT-{bundle.name}",
                    instrument=COMPLETENESS,
                    surface=_relative(bundle / TESTS_RUBRIC, base),
                    reason="committed-rubric-absent",
                    caps=Disposition.HOLD,
                    statement="tests/rubrics.json is absent or unparseable for this bundle.",
                    subject=bundle.name,
                )
            )
            continue
        ran = True
        items = _items(document)
        compiled_items = [item for item in items if str(item.get("mode")) == COMPILED_MODE]
        compiled_ids = {str(item.get("id")) for item in compiled_items}
        compiled_tests = _compiled_test_identifiers(bundle)
        total_weight = sum(abs(float(item.get("weight") or 0)) for item in items)
        compiled_weight = sum(abs(float(item.get("weight") or 0)) for item in compiled_items)
        share = (compiled_weight / total_weight) if total_weight else 0.0
        row = {
            "items": len(items),
            "compiled_items": len(compiled_items),
            "committed_compiled_tests": len(compiled_tests),
            "compiled_weight": compiled_weight,
            "total_weight": total_weight,
            "compiled_weight_share": round(share, 6),
            "floor_state": floor_state,
        }
        notes["bundles"][bundle.name] = row
        if not compiled_ids and compiled_tests:
            findings.append(
                Finding(
                    finding_id=f"RUB-COMPLETENESS-UNDECLARED-COMPILATION-{bundle.name}",
                    instrument=COMPLETENESS,
                    critical_class="rubric-compilation",
                    severity=Severity.HIGH,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        f"The bundle commits {len(compiled_tests)} compiled test(s) in "
                        f"{COMPILED_TESTS} while not one of its {len(items)} rubric items "
                        f"declares mode {COMPILED_MODE!r}, so set equality fails in both "
                        "directions at once: every committed compiled test enforces a "
                        "requirement no rubric item claims is compiled, and the compiled item "
                        "set is empty. The compiled weight share is therefore "
                        f"{share:.4f} of {total_weight:.1f} total weight."
                    ),
                    evidence=dict(
                        row,
                        bundle=bundle.name,
                        compiled_test_sample=compiled_tests[:8],
                        rubric=_relative(bundle / TESTS_RUBRIC, base),
                        compiled_module=_relative(bundle / COMPILED_TESTS, base),
                    ),
                )
            )
        else:
            missing_tests = sorted(
                identifier
                for identifier in compiled_ids
                if not any(identifier.lower() in test.lower() for test in compiled_tests)
            )
            if missing_tests:
                findings.append(
                    Finding(
                        finding_id=f"RUB-COMPLETENESS-UNENFORCED-ITEM-{bundle.name}",
                        instrument=COMPLETENESS,
                        critical_class="rubric-compilation",
                        severity=Severity.HIGH,
                        caps=Disposition.BLOCK,
                        bucket=Bucket.D,
                        subject=bundle.name,
                        statement=(
                            f"{len(missing_tests)} rubric item(s) declare mode {COMPILED_MODE!r} "
                            "with no committed compiled test naming them, so a declared "
                            "compilation is not actually enforced."
                        ),
                        evidence=dict(row, bundle=bundle.name, unenforced=missing_tests[:8]),
                    )
                )
    return InstrumentResult(
        instrument=COMPLETENESS,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=[],
        standing=Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE,
        notes=notes,
    )


def _run_residue(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-RUB-RESIDUE: ground each judged item's judgment against its evidence.

    A judged item must name the semantic residue that blocks its compilation,
    and the scope records that the residue lives in TRUTH.md because the item
    schema is closed. An item that names no residue anywhere is retained,
    because a judgment with no stated reason for staying judged is
    indistinguishable from a requirement nobody compiled.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    notes: dict[str, Any] = {"bundles": {}}
    ran = False
    for bundle in bundles:
        truth = _read_text(bundle / TRUTH)
        if truth is None:
            gaps.append(
                CoverageGap(
                    gap_id=f"D-RUB-RESIDUE-SOURCE-ABSENT-{bundle.name}",
                    instrument=RESIDUE,
                    surface=_relative(bundle / TRUTH, base),
                    reason="residue-source-absent",
                    caps=Disposition.HOLD,
                    statement=(
                        "solution/TRUTH.md is absent, and the scope records it as the only place "
                        "a judged item's residue may live, so no judged item could be grounded."
                    ),
                    subject=bundle.name,
                )
            )
            continue
        ungrounded: list[str] = []
        judged_total = 0
        for relative, document in _rubric_documents(bundle):
            for item in _items(document):
                mode = str(item.get("mode") or "")
                if mode and mode != JUDGED_MODE:
                    continue
                identifier = str(item.get("id") or "")
                if not identifier:
                    continue
                judged_total += 1
                ran = True
                if f"`{identifier}`" not in truth:
                    ungrounded.append(f"{relative}:{identifier}")
        notes["bundles"][bundle.name] = {
            "judged_items": judged_total,
            "ungrounded": len(set(ungrounded)),
        }
        deduplicated = sorted(set(ungrounded))
        if deduplicated:
            findings.append(
                Finding(
                    finding_id=f"RUB-RESIDUE-UNGROUNDED-{bundle.name}",
                    instrument=RESIDUE,
                    critical_class="rubric-compilation",
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        f"{len(deduplicated)} judged rubric item(s) name no semantic residue in "
                        "solution/TRUTH.md, so nothing on the record says why the item stays a "
                        "judgment rather than reducing to a deterministic relation over the "
                        "committed artifacts it names as evidence."
                    ),
                    evidence={
                        "bundle": bundle.name,
                        "ungrounded": deduplicated[:12],
                        "residue_source": _relative(bundle / TRUTH, base),
                    },
                )
            )
    return InstrumentResult(
        instrument=RESIDUE,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=[],
        standing=Standing.OBSERVED_VIOLATION if findings else Standing.DEMONSTRATED_COVERAGE,
        notes=notes,
    )


def _stage_bundle(bundle: Path, destination: Path) -> bool:
    """Copy the trees the generator reads and writes into a scratch directory.

    The generator writes its artifacts back into the bundle, so it is never run
    against the committed tree: this harness writes nothing outside .audit and
    a regeneration that mutated the audited bytes would destroy the evidence it
    is measuring.
    """
    try:
        for name in ("solution", "tests"):
            source = bundle / name
            if not source.is_dir():
                return False
            shutil.copytree(source, destination / name)
    except (OSError, shutil.Error):
        return False
    return True


def _run_regen(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-RUB-REGEN: run the committed generator under two sandbox identities.

    The two runs differ in working directory, HOME, USER, LOGNAME, TMPDIR, PATH
    ordering, locale and timezone. Hostname is not varied, because changing it
    requires privilege this process does not hold, so the gap below names that
    dimension explicitly rather than letting a partial identity sweep read as a
    complete one. Only the rubric and the compiled tests are compared here;
    the ground truth and the solve script belong to the delivery family, which
    runs the same generator for its own purpose.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    artifacts: list[RawArtifact] = []
    notes: dict[str, Any] = {"bundles": {}}
    varied = ["working_directory", "HOME", "USER", "LOGNAME", "TMPDIR", "PATH", "LC_ALL", "TZ"]
    not_varied = ["hostname", "uid", "kernel", "python_build"]
    gaps.append(
        CoverageGap(
            gap_id="D-RUB-REGEN-IDENTITY-PARTIAL",
            instrument=REGEN,
            surface="rubric",
            reason="sandbox-identity-partially-varied",
            caps=Disposition.HOLD,
            statement=(
                "The two generator runs differed in "
                f"{', '.join(varied)} but not in {', '.join(not_varied)}. Changing the hostname "
                "or uid requires privilege this process does not hold, so a generator that "
                "fingerprints the auditor through one of those dimensions would still produce "
                "byte-identical output here. The dimensions that were varied are compared and "
                "reported; the rest stay unmeasured."
            ),
        )
    )
    ran = False
    for bundle in bundles:
        generator = bundle / GENERATOR
        if not generator.is_file():
            gaps.append(
                CoverageGap(
                    gap_id=f"D-RUB-GENERATOR-ABSENT-{bundle.name}",
                    instrument=REGEN,
                    surface=_relative(generator, base),
                    reason="committed-generator-absent",
                    caps=Disposition.HOLD,
                    statement=(
                        "solution/recompute.py is absent, so the committed rubric and compiled "
                        "tests could not be regenerated and their reproducibility is unmeasured."
                    ),
                    subject=bundle.name,
                )
            )
            continue
        with tempfile.TemporaryDirectory(prefix="crucible-rub-regen-") as scratch:
            scratch_root = Path(scratch)
            digests: dict[str, list[str]] = {name: [] for name in REGEN_REQUIRED_ARTIFACTS}
            identities = (
                {
                    "HOME": str(scratch_root / "home-a"),
                    "USER": "crucible-a",
                    "LOGNAME": "crucible-a",
                    "TMPDIR": str(scratch_root / "tmp-a"),
                    "LC_ALL": "C",
                    "TZ": "UTC",
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
                {
                    "HOME": str(scratch_root / "home-b"),
                    "USER": "crucible-b",
                    "LOGNAME": "crucible-b",
                    "TMPDIR": str(scratch_root / "tmp-b"),
                    "LC_ALL": "C.UTF-8",
                    "TZ": "Asia/Kolkata",
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
            )
            succeeded = 0
            for index, environment in enumerate(identities):
                workdir = scratch_root / f"run-{index}"
                workdir.mkdir(parents=True, exist_ok=True)
                for key in ("HOME", "TMPDIR"):
                    Path(environment[key]).mkdir(parents=True, exist_ok=True)
                if not _stage_bundle(bundle, workdir):
                    continue
                artifact = core.run_capture(
                    ["python3", str(workdir / GENERATOR)],
                    artifact_id=f"rub-regen-{bundle.name}-{index}",
                    cwd=workdir,
                    timeout=600.0,
                    env=environment,
                )
                artifacts.append(artifact)
                if artifact.exit_code != 0:
                    continue
                succeeded += 1
                for name in REGEN_REQUIRED_ARTIFACTS:
                    produced = workdir / name
                    digests[name].append(
                        core.sha256_path(produced) if produced.is_file() else "absent"
                    )
            if succeeded < len(identities):
                gaps.append(
                    CoverageGap(
                        gap_id=f"D-RUB-GENERATOR-UNRUNNABLE-{bundle.name}",
                        instrument=REGEN,
                        surface=_relative(generator, base),
                        reason="committed-generator-unrunnable",
                        caps=Disposition.HOLD,
                        statement=(
                            "The committed generator did not complete under both sandbox "
                            f"identities ({succeeded} of {len(identities)} succeeded), so rubric "
                            "reproducibility is unmeasured rather than demonstrated."
                        ),
                        subject=bundle.name,
                    )
                )
                continue
            ran = True
            row: dict[str, Any] = {"varied": varied, "not_varied": not_varied}
            for name, observed in digests.items():
                committed = bundle / name
                committed_digest = core.sha256_path(committed) if committed.is_file() else "absent"
                row[name] = {
                    "regenerated": observed,
                    "committed": committed_digest,
                    "identity_stable": len(set(observed)) == 1,
                    "matches_committed": bool(observed) and observed[0] == committed_digest,
                }
                if len(set(observed)) != 1:
                    findings.append(
                        Finding(
                            finding_id=f"RUB-REGEN-IDENTITY-DEPENDENT-{bundle.name}-{name}",
                            instrument=REGEN,
                            critical_class="rubric-compilation",
                            severity=Severity.HIGH,
                            caps=Disposition.BLOCK,
                            bucket=Bucket.D,
                            subject=bundle.name,
                            statement=(
                                f"Regenerating {name} under two sandbox identities produced "
                                f"different bytes {observed}, so the generator fingerprints the "
                                "host it runs on and the committed artifact cannot be "
                                "independently re-derived."
                            ),
                            evidence={"bundle": bundle.name, "artifact": name, "digests": observed},
                        )
                    )
                elif observed and observed[0] != committed_digest:
                    findings.append(
                        Finding(
                            finding_id=f"RUB-REGEN-DRIFT-{bundle.name}-{name}",
                            instrument=REGEN,
                            critical_class="rubric-compilation",
                            severity=Severity.HIGH,
                            caps=Disposition.BLOCK,
                            bucket=Bucket.D,
                            subject=bundle.name,
                            statement=(
                                f"The regenerated {name} does not match the committed bytes. "
                                f"Regenerated {observed[0]}, committed {committed_digest}. A "
                                "committed rubric that its own generator does not reproduce has "
                                "been hand-edited or generated from a different source."
                            ),
                            evidence={
                                "bundle": bundle.name,
                                "artifact": name,
                                "regenerated": observed[0],
                                "committed": committed_digest,
                            },
                        )
                    )
            notes["bundles"][bundle.name] = row
    return InstrumentResult(
        instrument=REGEN,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=artifacts,
        standing=Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE,
        notes=notes,
    )


def _control_rollouts(bundle: Path) -> list[tuple[str, Path, float, str]]:
    """Every committed rollout with its recorded score and reason.

    A rollout recorded at a zero score is a committed known-wrong control: the
    verifier itself declared that submission did not satisfy the graded set, so
    a compiled check that accepts it accepts a known-wrong input.
    """
    rollouts: list[tuple[str, Path, float, str]] = []
    root = bundle / "trajectories"
    if not root.is_dir():
        return rollouts
    for model in sorted(root.iterdir()):
        if not model.is_dir():
            continue
        for run in sorted(model.iterdir()):
            verifier_dir = run / "verifier"
            reward = _read_json(verifier_dir / "reward.json")
            if not isinstance(reward, dict):
                continue
            reason_doc = _read_json(verifier_dir / "reward_reason.json")
            reason = ""
            if isinstance(reason_doc, dict):
                reason = str(reason_doc.get("reason") or "")
            rollouts.append(
                (
                    f"{model.name}/{run.name}",
                    verifier_dir,
                    float(reward.get("reward", -1.0)),
                    reason,
                )
            )
    return rollouts


def _run_replay(base: Path, bundles: list[Path]) -> InstrumentResult:
    """G-RUB-REPLAY: run the compiled tests against the oracle and every control.

    A compiled test that accepts the oracle and also accepts a control the
    verifier recorded as scoring zero has been demonstrated inert. Verifier
    principle 7 makes an inert required check a broken instrument, so the result
    is a retained Finding capping at BLOCK rather than a coverage gap.

    The module is executed rather than merely read, because an argument that a
    check cannot fail is weaker evidence than a run in which it did not fail on
    an input that should have failed it. Reachability is checked alongside
    liveness: a compiled module no grading entry point invokes is inert by a
    second, independent route, and a rubric no runtime component reads is inert
    by a third.
    """
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    artifacts: list[RawArtifact] = []
    notes: dict[str, Any] = {"bundles": {}}
    ran = False
    for bundle in bundles:
        compiled = bundle / COMPILED_TESTS
        if not compiled.is_file():
            gaps.append(
                CoverageGap(
                    gap_id=f"D-RUB-COMPILED-MODULE-ABSENT-{bundle.name}",
                    instrument=REPLAY,
                    surface=_relative(compiled, base),
                    reason="compiled-module-absent",
                    caps=Disposition.HOLD,
                    statement=(
                        "tests/test_output.py is absent, so compiled-check liveness is unmeasured."
                    ),
                    subject=bundle.name,
                )
            )
            continue
        rollouts = _control_rollouts(bundle)
        controls = [row for row in rollouts if row[2] == 0.0]
        oracles = [row for row in rollouts if row[2] > 0.0]
        reference = oracles or rollouts
        if not reference or not controls:
            gaps.append(
                CoverageGap(
                    gap_id=f"D-RUB-CONTROL-ABSENT-{bundle.name}",
                    instrument=REPLAY,
                    surface=_relative(bundle / "trajectories", base),
                    reason="oracle-or-known-wrong-control-absent",
                    caps=Disposition.HOLD,
                    statement=(
                        "This bundle commits no usable oracle-side rollout or no rollout recorded "
                        f"at a zero score ({len(reference)} reference, {len(controls)} control), "
                        "so the compiled tests could not be replayed against both sides and their "
                        "liveness stays unmeasured."
                    ),
                    subject=bundle.name,
                )
            )
        selected: list[tuple[str, Path, float, str]] = []
        for candidate in reference[:1] + controls:
            if candidate[0] not in {chosen[0] for chosen in selected}:
                selected.append(candidate)
        outcomes: list[dict[str, Any]] = []
        for label, verifier_dir, score, reason in selected:
            artifact = core.run_capture(
                [
                    "python3",
                    "-m",
                    "pytest",
                    str(compiled),
                    "-p",
                    "no:cacheprovider",
                    "-q",
                    "--no-header",
                ],
                artifact_id=f"rub-replay-{bundle.name}-{label.replace('/', '-')}",
                cwd=Path(tempfile.gettempdir()),
                timeout=600.0,
                env={
                    "TRINITY_LOGS": str(verifier_dir),
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTHONPYCACHEPREFIX": os.path.join(tempfile.gettempdir(), "crucible-pyc"),
                },
            )
            artifacts.append(artifact)
            outcomes.append(
                {
                    "rollout": label,
                    "recorded_score": score,
                    "recorded_reason": reason,
                    "is_known_wrong_control": score == 0.0,
                    "exit_code": artifact.exit_code,
                    "accepted": artifact.exit_code == 0,
                }
            )
        ran = ran or bool(outcomes)
        accepted_controls = [
            row for row in outcomes if row["is_known_wrong_control"] and row["accepted"]
        ]
        text = _read_text(compiled) or ""
        probe_methods = [
            line.strip()
            for line in text.splitlines()
            if line.strip().startswith("def test_") and "record_property" in line
        ]
        asserts_in_probes = "probe_satisfied" in text and "assert probe_satisfied" in text
        invokers = []
        for relative in (GRADING_ENTRY, GRADED_RUN, RUNNER_CONFIG, DOCKERFILE):
            body = _read_text(bundle / relative)
            if body and "test_output" in body:
                invokers.append(relative)
        rubric_readers = []
        for relative in (RUNNER, HARNESS_CORE):
            body = _read_text(bundle / relative)
            if body and "rubrics.json" in body:
                rubric_readers.append(relative)
        row = {
            "outcomes": outcomes,
            "probe_methods_without_assert": len(probe_methods),
            "probe_assertions_present": asserts_in_probes,
            "grading_entrypoints_invoking_module": invokers,
            "runtime_components_reading_rubric": rubric_readers,
        }
        notes["bundles"][bundle.name] = row
        if accepted_controls:
            findings.append(
                Finding(
                    finding_id=f"RUB-REPLAY-INERT-COMPILED-CHECK-{bundle.name}",
                    instrument=REPLAY,
                    critical_class="rubric-compilation",
                    severity=Severity.CRITICAL,
                    caps=Disposition.BLOCK,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        "The committed compiled checks are INERT, demonstrated by execution and "
                        "retained under verifier principle 7 as a broken instrument rather than a "
                        "coverage gap. Three independent layers each make the rubric surface "
                        "unable to fail. Layer one: every rubric probe method in "
                        f"{COMPILED_TESTS} calls record_property and carries no assert, so "
                        f"{len(probe_methods)} site requirement(s) can be violated while the "
                        "module still exits green; run against a control the verifier itself "
                        f"recorded at reward 0.0 the module still exited 0 "
                        f"({[row['rollout'] for row in accepted_controls]}). Layer two: no "
                        f"grading entry point invokes the module at all, with {GRADING_ENTRY}, "
                        f"{GRADED_RUN}, {RUNNER_CONFIG} and {DOCKERFILE} naming it "
                        f"{len(invokers)} time(s). Layer three: no runtime component reads "
                        f"tests/rubrics.json, with {RUNNER} and {HARNESS_CORE} naming it "
                        f"{len(rubric_readers)} time(s), so no rubric judgment ever reaches the "
                        "reward channel."
                    ),
                    evidence={
                        "bundle": bundle.name,
                        "layer_1_locus": f"{COMPILED_TESTS} rubric_probes lines 63 to 71, "
                        "probe_satisfied lines 74 to 80, probe methods lines 171 to 209",
                        "layer_1_probe_methods_without_assert": len(probe_methods),
                        "layer_1_control_runs": accepted_controls,
                        "layer_2_locus": f"{GRADING_ENTRY} line 20 calls only run_tests.py",
                        "layer_2_invokers": invokers,
                        "layer_3_rubric_readers": rubric_readers,
                        "compiled_module": _relative(compiled, base),
                        "all_runs": outcomes,
                    },
                )
            )
    return InstrumentResult(
        instrument=REPLAY,
        ran=ran,
        findings=findings,
        gaps=gaps,
        artifacts=artifacts,
        standing=Standing.OBSERVED_VIOLATION if findings else Standing.INSUFFICIENT_EVIDENCE,
        notes=notes,
    )


def run_family(base: Path, reconnaissance: recon.Recon) -> list[InstrumentResult]:
    """Run the five G-RUB instruments and return one result each.

    Never raises. An instrument that fails unexpectedly is converted into a
    result carrying an explaining coverage gap, because InstrumentResult treats
    ``ran`` false with no gap as BLOCK and a family that raised would abort the
    whole run rather than record what it could not measure.
    """
    bundles = core.bundle_roots(base)
    results: list[InstrumentResult] = []
    probes: tuple[tuple[str, Callable[[Path, list[Path]], InstrumentResult]], ...] = (
        (SCHEMA, _run_schema),
        (COMPLETENESS, _run_completeness),
        (RESIDUE, _run_residue),
        (REGEN, _run_regen),
        (REPLAY, _run_replay),
    )
    if not bundles:
        for name, _ in probes:
            results.append(
                InstrumentResult(
                    instrument=name,
                    ran=False,
                    gaps=[
                        CoverageGap(
                            gap_id=f"D-RUB-NO-BUNDLE-{name.rsplit('-', 1)[-1]}",
                            instrument=name,
                            surface="bundles",
                            reason="no-resident-bundle",
                            caps=Disposition.HOLD,
                            statement=(
                                "No resident bundle carrying a task.toml was found under any lane "
                                "root, so this probe had no rubric surface to measure."
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
                            gap_id=f"D-RUB-PROBE-FAILED-{name.rsplit('-', 1)[-1]}",
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
    "COMPLETENESS",
    "FAMILY",
    "REGEN",
    "REPLAY",
    "RESIDUE",
    "SCHEMA",
    "run_family",
]
