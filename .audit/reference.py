"""Contract step 8d: the G-REF reference-fidelity instrument family.

This module discharges the four instruments step 8d names, under the scope key
``reference_emulation`` whose ``present`` field reads true. The rationale lives
in these docstrings because the contract is prompt-only, so the harness itself
has to carry the reasoning as audit evidence.

Why this family is in scope at all. CRUCIBLE_VIEW declares
``e20_reference_fidelity`` present false under a greenfield exemption. The
audited bytes refute that declaration directly: every task.toml carries an
``[interface_spec]`` block whose mode is ``names-only``, every bundle grades
against a named versioned upstream at a pinned base commit, and
``tests/rubrics.json`` asserts exact golden strings against ``final.diff``. A
projection only ever tightens a parameter or lowers a disposition and never
grants an exemption the tree refutes, so the local detection stands and the
scope file records the conflict as ``A-VIEW-EXEMPTION-REFUTED``. This family
runs.

Member by member, and why each is shaped the way it is:

G-REF-OBTAIN obtains the real upstream artifact at the version the bundle pins.
It cannot. The pinned identities are upstream repositories at commit SHAs, and
resolving any of them requires reaching the upstream host across a firewall this
harness is forbidden to cross. The instrument therefore performs the half that
is derivable from committed bytes, which is resolving and recording exactly
which artifact at exactly which version would have to be obtained, and records
the obtain itself as coverage gap ``fidelity-upstream-unobtainable``. Recording
the pinned identity is not a substitute for holding the artifact and never reads
as one.

G-REF-REPLAY replays the committed live checkers against the real artifact and
emits a REAL-UPSTREAM-SCORE. With no real artifact there is no real score, and
the score is recorded as null with its reason rather than as a number. The
derivable half is the full inventory of what the committed checkers would test:
the graded command, the fail-to-pass and preserve target sets, the parser in
force, the reward reduction, and the golden-string probes. That inventory is
what a real replay would exercise, so it is recorded now and the replay itself
is a named gap.

G-REF-DISCRIMINATION compares the real-upstream score against the candidate
score. Both halves are unavailable for different reasons and the difference
matters. The real score is unavailable because the artifact is unobtainable. The
candidate score is unavailable because no candidate is projected through
CRUCIBLE_VIEW for any resident uuid, which is its own coverage gap. The
instrument therefore computes against the no-op baseline alone, which is
derivable from the committed reward reduction without executing anything: a
submission that changes nothing resolves no fail-to-pass target, so the
reduction yields zero. A separation that cannot be measured, and a measured
separation falling inside the discrimination margin, both cap at HOLD. The
committed rollout rewards are recorded as evidence and are explicitly not read
as the projected candidate score, because a reward the producer committed is the
thing under audit rather than an independent measurement of it.

G-REF-DIVERGENCE-TAXONOMY classifies every real-artifact check failure into
exactly one of four classes: exit-code-contract, output-literal,
invented-or-assumed-interface, validation-locus. Without the real artifact there
are no measured failures to classify, and that absence is a named gap. What can
be classified, and is, is the committed interface specification itself. A
names-only interface specification is exactly the shape that produces
invented-or-assumed-interface divergence: a checker that asserts a symbol name
without asserting the symbol's behaviour cannot distinguish a real
implementation from a stub that carries the name and does nothing. Every entry
in every ``[interface_spec]`` block is therefore classified statically by shape,
per-class counts are recorded, and the implicated harness locations are named.
The evidence labels this a static classification of the specification and never
as a measured classification of real-artifact failures, because conflating the
two would convert an unmeasured surface into a measured one.

An entry whose shape matches no recognized form is recorded verbatim and caps
fail-closed, because an unclassifiable entry silently dropped from the counts
would make the taxonomy read as complete when it is not.

Every member is pure Bucket D. A clean result here is never evidence that the
reference fidelity is sound; it is only evidence that this probe found nothing.
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

FAMILY = "G-REF"

OBTAIN = "G-REF-OBTAIN"
REPLAY = "G-REF-REPLAY"
DISCRIMINATION = "G-REF-DISCRIMINATION"
DIVERGENCE = "G-REF-DIVERGENCE-TAXONOMY"

CRITICAL_CLASS = "reference-fidelity"

UPSTREAM_UNOBTAINABLE_REASON = "fidelity-upstream-unobtainable"

DIVERGENCE_CLASSES: tuple[str, ...] = (
    "exit-code-contract",
    "output-literal",
    "invented-or-assumed-interface",
    "validation-locus",
)

DISCRIMINATION_MARGIN = 0.25

DISCRIMINATION_MARGIN_BASIS = (
    "The scope file's reference_emulation block binds no numeric threshold, so this margin is a "
    "harness-local constant recorded here rather than invented at the moment it first has data. "
    "The smallest committed fail-to-pass set holds five targets, so one resolved target moves the "
    "reward reduction by 0.2; a real-versus-candidate separation at or below that size is inside "
    "the noise of a single target and is not discrimination. 0.25 is the next quarter above it."
)

NOOP_BASELINE_BASIS = (
    "A submission that changes nothing resolves no fail-to-pass target, so the committed reward "
    "reduction at tests/run_tests.py, which is (resolved fail-to-pass plus resolved extra) over "
    "(fail-to-pass total plus extra total), yields zero. This is derived from the committed "
    "reduction and never from executing the grader."
)

INTERFACE_SHAPES: tuple[str, ...] = (
    "cli-flag",
    "typed-signature",
    "dotted-symbol",
    "bare-symbol",
)

CLI_FLAG = re.compile(r"(?:^|\s)--[A-Za-z0-9][A-Za-z0-9._-]*")

TYPED_SIGNATURE = re.compile(r"(?:^def\s)|(?:->)")

DOTTED_SYMBOL = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*")

BARE_SYMBOL = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

EXIT_CODE_LOCI: tuple[str, ...] = (
    "tests/run_tests.py",
    "tests/test.sh",
    "tests/graded/run.sh",
)

VALIDATION_LOCUS_KEYS: tuple[str, ...] = (
    "target_cmd",
    "preserve_cmd",
    "build_cmd",
    "report_globs",
)


def _register() -> None:
    """Declare every step 8d instrument under the Phase 1 item 4 twelve-field schema.

    ``disposition_cap_on_absence`` is HOLD on every row and is never SHIP,
    because a reference-fidelity instrument that does not run leaves the
    emulation surface unmeasured, and an unmeasured surface is a coverage gap
    rather than a pass.
    """
    rows = (
        Instrument(
            name=OBTAIN,
            category=Category.REFERENCE,
            binary="",
            ecosystems=("*",),
            timeout_seconds=300.0,
            required_conditions=(
                "upstream repository reachable at the pinned commit",
                "committed task bundles present",
            ),
            critical_capability="possession of the real upstream artifact at its pinned version",
            evidence_class=EvidenceClass.EXTERNAL_ATTESTATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="Network egress is forbidden here, so the obtain resolves as a coverage gap.",
        ),
        Instrument(
            name=REPLAY,
            category=Category.REFERENCE,
            binary="",
            ecosystems=("*",),
            timeout_seconds=600.0,
            required_conditions=(
                "real upstream artifact obtained",
                "committed live checkers present",
            ),
            critical_capability="REAL-UPSTREAM-SCORE from the committed checkers",
            evidence_class=EvidenceClass.EXECUTION_REPLAY,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="Records the committed checker inventory even when no real score is producible.",
        ),
        Instrument(
            name=DISCRIMINATION,
            category=Category.REFERENCE,
            binary="",
            ecosystems=("*",),
            timeout_seconds=120.0,
            required_conditions=(
                "REAL-UPSTREAM-SCORE available",
                "candidate score projected through CRUCIBLE_VIEW",
            ),
            critical_capability="separation between the real-upstream score and the candidate",
            evidence_class=EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="An unprojected candidate falls back to the no-op baseline alone and caps HOLD.",
        ),
        Instrument(
            name=DIVERGENCE,
            category=Category.REFERENCE,
            binary="",
            ecosystems=("*",),
            timeout_seconds=120.0,
            required_conditions=("committed interface specification present",),
            critical_capability="four-class taxonomy over real-artifact check failures",
            evidence_class=EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="Static classification of the specification is labelled as such, never measured.",
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


def bundles_of(base: Path) -> list[Path]:
    """Every resident bundle directory, derived from committed bytes alone."""
    return sorted(core.bundle_roots(base), key=lambda path: path.name)


def crucible_view_path(base: Path) -> Path:
    """Locate CRUCIBLE_VIEW, the only ENGRAM surface this family may read.

    The hardness contract and its rendered report are withheld from CRUCIBLE by
    construction and are never opened here or anywhere else in this module.
    """
    return base.resolve().parent / ".memory" / "crucible_view.yaml"


def scope_reference_block(base: Path) -> dict[str, Any]:
    """Read the bound reference_emulation block out of the approved scope file.

    The block is read rather than restated because the approved scope digest
    binds its bytes, so a later edit to the interface specification it records
    invalidates approval instead of silently re-parameterizing this family.
    """
    document = _load_yaml(base / core.AUDIT_DIRNAME / core.SCOPE_FILENAME)
    if not isinstance(document, dict):
        return {}
    block = document.get("reference_emulation")
    return block if isinstance(block, dict) else {}


def upstream_identity(bundle: Path) -> dict[str, Any]:
    """Resolve the exact upstream artifact and version this bundle pins.

    Three committed sources carry it and all three are recorded rather than one
    being preferred, because a disagreement between them is itself evidence. The
    manifest's span_provenance names the repository and the version span, the
    verifier config names the upstream base commit the span was cut from, and
    the config's own base_commit names the rebuilt commit that exists inside the
    image, which is a different object and is never read as the upstream one.
    """
    manifest = _load_toml(bundle / "task.toml")
    span = manifest.get("span_provenance")
    span = span if isinstance(span, dict) else {}
    config = _load_json(bundle / "tests" / "config.json")
    config = config if isinstance(config, dict) else {}
    return {
        "uuid": bundle.name,
        "instance_identity": str(span.get("instance_identity") or ""),
        "span_label": str(span.get("span_label") or ""),
        "repository": str(config.get("repo") or ""),
        "upstream_base_commit": str(config.get("upstream_base_commit") or ""),
        "image_local_base_commit": str(config.get("base_commit") or ""),
        "image_local_base_commit_basis": str(config.get("base_commit_basis") or ""),
        "instance_id": str(config.get("instance_id") or ""),
        "pinned_by": "upstream base commit sha and the sanitized image digest",
        "resolution_requires_network": True,
    }


def interface_spec(bundle: Path) -> dict[str, Any]:
    """Enumerate the committed interface specification entry by entry.

    Every non-mode key under ``[interface_spec]`` is an issue label carrying a
    list of external symbols. The entries are flattened with their issue label
    retained, because a divergence class is only actionable when the audit can
    say which issue's asserted interface produced it.
    """
    manifest = _load_toml(bundle / "task.toml")
    block = manifest.get("interface_spec")
    block = block if isinstance(block, dict) else {}
    entries: list[dict[str, Any]] = []
    for key in sorted(block):
        if key == "mode":
            continue
        value = block[key]
        listed = value if isinstance(value, list) else [value]
        for item in listed:
            entries.append({"issue": key, "entry": str(item)})
    return {
        "uuid": bundle.name,
        "mode": str(block.get("mode") or ""),
        "issue_keys": sorted(key for key in block if key != "mode"),
        "entry_count": len(entries),
        "entries": entries,
    }


def golden_probes(bundle: Path) -> dict[str, Any]:
    """Collect every golden-string probe the committed rubric asserts.

    The probes live under ``sites[].requirements[].probe`` and assert exact
    literals against ``final.diff``. They are the only committed mechanism that
    can observe an interface symbol at all, so they are the harness locations
    the output-literal divergence class implicates.
    """
    document = _load_json(bundle / "tests" / "rubrics.json")
    document = document if isinstance(document, dict) else {}
    sites = document.get("sites")
    sites = sites if isinstance(sites, list) else []
    literals: list[dict[str, Any]] = []
    for site in sites:
        if not isinstance(site, dict):
            continue
        requirements = site.get("requirements")
        requirements = requirements if isinstance(requirements, list) else []
        for requirement in requirements:
            if not isinstance(requirement, dict):
                continue
            probe = requirement.get("probe")
            probe = probe if isinstance(probe, dict) else {}
            for operator in sorted(probe):
                values = probe[operator]
                values = values if isinstance(values, list) else [values]
                for value in values:
                    literals.append(
                        {
                            "path": str(site.get("path") or ""),
                            "symbol": str(site.get("symbol") or ""),
                            "requirement_id": str(requirement.get("id") or ""),
                            "operator": operator,
                            "load_bearing": bool(requirement.get("load_bearing", False)),
                            "literal_sha256": core.sha256_bytes(
                                str(value).encode("utf-8", "replace")
                            ),
                            "literal_length": len(str(value)),
                        }
                    )
    checks = document.get("checks")
    checks = checks if isinstance(checks, dict) else {}
    return {
        "uuid": bundle.name,
        "rubric_digest": _digest_or_none(bundle / "tests" / "rubrics.json"),
        "site_count": len(sites),
        "probe_literal_count": len(literals),
        "load_bearing_probe_count": sum(1 for row in literals if row["load_bearing"]),
        "check_ids": sorted(str(key) for key in checks),
        "probes": literals,
    }


def committed_checkers(bundle: Path) -> dict[str, Any]:
    """Record exactly what the committed live checkers would test on a real artifact.

    This is the derivable half of G-REF-REPLAY. It is an inventory and not a
    score: it says which command runs, which targets are declared, which parser
    reads the output, and how the reward reduces, all read out of committed
    bytes. A real replay would exercise precisely this set, so recording it now
    makes the missing half nameable rather than merely absent.
    """
    config = _load_json(bundle / "tests" / "config.json")
    config = config if isinstance(config, dict) else {}
    manifest = _load_toml(bundle / "task.toml")

    def _count(key: str) -> int:
        value = config.get(key)
        return len(value) if isinstance(value, list) else 0

    return {
        "uuid": bundle.name,
        "language": str(config.get("language") or ""),
        "parser": str(config.get("parser") or ""),
        "target_cmd": str(config.get("target_cmd") or ""),
        "preserve_cmd": str(config.get("preserve_cmd") or ""),
        "build_cmd": str(config.get("build_cmd") or ""),
        "graded_run_digest": _digest_or_none(bundle / "tests" / "graded" / "run.sh"),
        "entry_point_digest": _digest_or_none(bundle / "tests" / "test.sh"),
        "runner_digest": _digest_or_none(bundle / "tests" / "run_tests.py"),
        "parser_module_digest": _digest_or_none(bundle / "tests" / "harness_core.py"),
        "config_digest": _digest_or_none(bundle / "tests" / "config.json"),
        "test_patch_digest": _digest_or_none(bundle / "tests" / "test.patch"),
        "f2p_total": _count("f2p_tests"),
        "p2p_total": _count("p2p_tests"),
        "n2p_total": _count("n2p_tests"),
        "s2p_total": _count("s2p_tests"),
        "n2p_excluded_total": _count("n2p_excluded"),
        "reward_reduction": (
            "(resolved fail-to-pass + resolved extra) / (fail-to-pass total + extra total)"
        ),
        "artifacts_declared": [str(item) for item in (manifest.get("artifacts") or [])],
        "verifier_network_mode": str(
            (manifest.get("verifier") or {}).get("network_mode")
            if isinstance(manifest.get("verifier"), dict)
            else ""
        ),
    }


def noop_baseline(bundle: Path) -> dict[str, Any]:
    """Derive the no-op baseline score from the committed reward reduction.

    No grader runs. The reduction is arithmetic over a resolved-target count,
    and a submission that changes nothing resolves nothing, so the numerator is
    zero for any non-empty denominator. An empty fail-to-pass set is recorded
    separately because the committed runner short-circuits it to zero under the
    reason ``empty-fail-to-pass-set`` rather than reaching the reduction at all.
    """
    checkers = committed_checkers(bundle)
    denominator = checkers["f2p_total"] + checkers["n2p_total"]
    if checkers["f2p_total"] == 0:
        return {
            "uuid": bundle.name,
            "score": 0.0,
            "denominator": denominator,
            "path": "empty-fail-to-pass-set short circuit",
            "basis": NOOP_BASELINE_BASIS,
        }
    return {
        "uuid": bundle.name,
        "score": 0.0,
        "denominator": denominator,
        "path": "reward reduction with a zero numerator",
        "basis": NOOP_BASELINE_BASIS,
    }


def committed_rollout_rewards(bundle: Path) -> list[dict[str, Any]]:
    """Record the rewards the producer committed beside each rollout.

    These are evidence about the producer, not an independent measurement of a
    candidate. They are recorded so the discrimination instrument can say what
    the tree claims, and they are never read as the projected candidate score,
    because the committed reward is the artifact under audit.
    """
    rows: list[dict[str, Any]] = []
    root = bundle / "trajectories"
    if not root.is_dir():
        return rows
    for model in sorted(child for child in root.iterdir() if child.is_dir()):
        for run in sorted(child for child in model.iterdir() if child.is_dir()):
            summary = _load_json(run / "verifier" / "summary.json")
            summary = summary if isinstance(summary, dict) else {}
            reason = _load_json(run / "verifier" / "reward_reason.json")
            reason = reason if isinstance(reason, dict) else {}
            rows.append(
                {
                    "uuid": bundle.name,
                    "rollout": f"{model.name}/{run.name}",
                    "committed_reward": reason.get("reward"),
                    "committed_reason": str(reason.get("reason") or ""),
                    "f2p_resolved": summary.get("f2p_resolved"),
                    "f2p_total": summary.get("f2p_total"),
                    "is_projected_candidate": False,
                }
            )
    return rows


def classify_interface_entry(entry: str) -> dict[str, Any]:
    """Classify one committed interface-specification entry by its shape.

    The mapping is the whole argument of this instrument and is stated here so
    it can be audited rather than inferred. Every recognized shape maps to
    ``invented-or-assumed-interface`` because every one of them asserts an
    identifier and none of them asserts behaviour. A checker that fires on the
    presence of a name is satisfied by any implementation carrying that name,
    including a stub that returns immediately, so the check cannot distinguish a
    real implementation from an invented one. A typed signature narrows the
    shape of the name and still asserts nothing the implementation does, so it
    lands in the same class rather than a weaker one.

    An entry matching no recognized shape returns a null class and is recorded
    verbatim by the caller, because silently dropping it would make the per-class
    counts read as covering the whole specification when they do not.
    """
    text = entry.strip()
    if CLI_FLAG.search(text) or text.lower().startswith("cli flag"):
        shape = "cli-flag"
    elif TYPED_SIGNATURE.search(text):
        shape = "typed-signature"
    elif DOTTED_SYMBOL.match(text):
        shape = "dotted-symbol"
    elif BARE_SYMBOL.match(text):
        shape = "bare-symbol"
    else:
        return {
            "entry": entry,
            "shape": "unclassifiable",
            "divergence_class": None,
            "asserts_behaviour": False,
            "basis": "the entry matches no recognized interface shape",
        }
    return {
        "entry": entry,
        "shape": shape,
        "divergence_class": "invented-or-assumed-interface",
        "asserts_behaviour": False,
        "basis": (
            "a names-only entry asserts an identifier and not a behaviour, so a checker built "
            "on it is satisfied by a stub carrying the same identifier"
        ),
    }


def _harness_loci(bundle: Path, probes: dict[str, Any], checkers: dict[str, Any]) -> dict[str, Any]:
    """Name the committed harness locations each divergence class implicates.

    The counts here are locations, not failures. A location is a place in the
    committed harness where a real-artifact failure of that class would surface,
    so naming them is what makes a later measured classification actionable
    instead of a bare histogram.
    """
    exit_code_sites = [relative for relative in EXIT_CODE_LOCI if (bundle / relative).is_file()]
    validation_sites = [
        {"key": key, "value": checkers.get(key, "")}
        for key in VALIDATION_LOCUS_KEYS
        if checkers.get(key)
    ]
    return {
        "exit-code-contract": {
            "locations": exit_code_sites,
            "count": len(exit_code_sites),
            "basis": (
                "tests/test.sh pre-writes a zero reward and tests/run_tests.py returns 0 only "
                "when the reward reaches 1.0, so an exit-code disagreement surfaces here"
            ),
        },
        "output-literal": {
            "locations": [f"tests/rubrics.json sites ({probes['site_count']})"],
            "count": probes["probe_literal_count"],
            "basis": (
                "every golden-string probe asserts an exact literal against final.diff, so a "
                "real artifact whose wording differs diverges here without being wrong"
            ),
        },
        "invented-or-assumed-interface": {
            "locations": ["task.toml [interface_spec]", "tests/rubrics.json sites"],
            "count": 0,
            "basis": (
                "the specification names symbols without asserting behaviour, and the rubric "
                "sites are the only committed place those names are observed"
            ),
        },
        "validation-locus": {
            "locations": validation_sites,
            "count": len(validation_sites),
            "basis": (
                "the graded command, the preserve command and the rubric sites are three "
                "separate loci, so a failure can be attributed to the wrong one"
            ),
        },
    }


def run_obtain(base: Path) -> InstrumentResult:
    """G-REF-OBTAIN: obtain the real upstream artifact at its pinned version.

    The obtain requires network access to the upstream repository. This harness
    is forbidden to reach across the firewall, and no vendored copy of any
    upstream tree exists in this verification root, so the artifact cannot be
    held. The derivable half runs: each bundle's pinned upstream identity is
    resolved and recorded, including the distinction between the upstream base
    commit and the rebuilt commit that exists inside the sanitized image, which
    are different objects and are never conflated.

    The gap reason is fixed at ``fidelity-upstream-unobtainable`` because the
    contract names that token, and a gap whose reason token drifts cannot be
    reconciled against the contract that mandates it.
    """
    identities = [upstream_identity(bundle) for bundle in bundles_of(base)]
    block = scope_reference_block(base)
    named = block.get("upstream_identity")
    named = [str(item) for item in named] if isinstance(named, list) else []

    gaps = [
        CoverageGap(
            gap_id="D-REF-UPSTREAM-UNOBTAINABLE",
            instrument=OBTAIN,
            surface="reference_emulation",
            reason=UPSTREAM_UNOBTAINABLE_REASON,
            caps=Disposition.HOLD,
            subject="project",
            statement=(
                "The real upstream artifact at the pinned version cannot be obtained. Every "
                "resident bundle pins a named upstream repository at a base commit sha, and "
                "resolving any of them requires reaching the upstream host across a firewall "
                "this harness is forbidden to cross. No vendored upstream tree exists in this "
                "verification root. The pinned identities are recorded so the missing artifact "
                "is nameable, and recording an identity is never possession of the artifact."
            ),
        )
    ]

    return InstrumentResult(
        instrument=OBTAIN,
        ran=True,
        findings=[],
        gaps=gaps,
        artifacts=[],
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes={
            "artifact_obtained": False,
            "obtain_channel": "upstream repository over the network",
            "network_permitted": False,
            "vendored_upstream_present": False,
            "pinned_identities": identities,
            "scope_declared_upstreams": named,
            "scope_pinned_version_statement": str(block.get("pinned_version") or ""),
        },
    )


def run_replay(base: Path) -> InstrumentResult:
    """G-REF-REPLAY: replay the committed checkers against the real artifact.

    With no artifact there is no REAL-UPSTREAM-SCORE, and the score is recorded
    as null carrying its reason rather than as a number. Emitting a placeholder
    number would be worse than emitting none, because a downstream reader cannot
    tell a placeholder from a measurement once it is written.

    The half that does run is the inventory of what the committed checkers would
    test. It is derived entirely from committed bytes: the graded command and
    its digest, the declared target sets and their sizes, the parser in force,
    the reward reduction, and the golden-string probes the rubric asserts.
    """
    inventory: list[dict[str, Any]] = []
    for bundle in bundles_of(base):
        checkers = committed_checkers(bundle)
        probes = golden_probes(bundle)
        checkers["golden_probe_literal_count"] = probes["probe_literal_count"]
        checkers["rubric_check_id_count"] = len(probes["check_ids"])
        inventory.append(checkers)

    gaps = [
        CoverageGap(
            gap_id="D-REF-REAL-SCORE-UNAVAILABLE",
            instrument=REPLAY,
            surface="reference_emulation",
            reason="real-upstream-score-unproducible",
            caps=Disposition.HOLD,
            subject="project",
            statement=(
                "No REAL-UPSTREAM-SCORE was produced. The committed live checkers are present "
                "and their full inventory is recorded, but the artifact they would be replayed "
                "against is unobtainable under D-REF-UPSTREAM-UNOBTAINABLE, so the replay has "
                "no subject. The score is recorded as null with this reason rather than as a "
                "number, because a placeholder number is indistinguishable from a measurement "
                "once it is written into evidence."
            ),
        )
    ]

    return InstrumentResult(
        instrument=REPLAY,
        ran=True,
        findings=[],
        gaps=gaps,
        artifacts=[],
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes={
            "real_upstream_score": None,
            "real_upstream_score_reason": "the real upstream artifact was not obtained",
            "replay_executed": False,
            "committed_checker_inventory": inventory,
            "inventory_basis": "derived from committed bytes with no execution",
        },
    )


def run_discrimination(base: Path) -> InstrumentResult:
    """G-REF-DISCRIMINATION: separate the real-upstream score from the candidate.

    Two inputs are missing for two different reasons and the difference is
    recorded rather than flattened. The real score is missing because the
    artifact is unobtainable. The candidate score is missing because no resident
    uuid is projected through CRUCIBLE_VIEW, which the contract makes its own
    coverage gap.

    With an unprojected candidate the instrument computes against the no-op
    baseline alone and caps at HOLD. The baseline is derived from the committed
    reward reduction and needs no execution. The committed rollout rewards are
    recorded beside it and are explicitly flagged as not the projected
    candidate, because a reward the producer wrote is the artifact under audit
    rather than an independent measurement of it.

    The margin comparison is implemented rather than skipped so that a later run
    holding both scores applies a threshold that was fixed before the data
    existed, which is the only way a threshold can be evidence rather than a
    result.
    """
    rows: list[dict[str, Any]] = []
    committed: list[dict[str, Any]] = []
    view_path = crucible_view_path(base)
    view_text = _read_text(view_path) if view_path.is_file() else ""

    for bundle in bundles_of(base):
        baseline = noop_baseline(bundle)
        identity = upstream_identity(bundle)
        projected = bool(view_text) and (
            view_text.count(bundle.name) > 0
            or (identity["instance_id"] and view_text.count(identity["instance_id"]) > 0)
        )
        rows.append(
            {
                "uuid": bundle.name,
                "real_upstream_score": None,
                "candidate_score": None,
                "candidate_projected": projected,
                "noop_baseline_score": baseline["score"],
                "noop_baseline_path": baseline["path"],
                "separation": None,
                "separation_inside_margin": None,
                "margin": DISCRIMINATION_MARGIN,
                "comparison_performed": "noop-baseline-only",
            }
        )
        committed.extend(committed_rollout_rewards(bundle))

    gaps = [
        CoverageGap(
            gap_id="D-REF-CANDIDATE-UNPROJECTED",
            instrument=DISCRIMINATION,
            surface="reference_emulation",
            reason="candidate-score-unprojected",
            caps=Disposition.HOLD,
            subject="project",
            statement=(
                "No candidate score is projected through CRUCIBLE_VIEW for any resident uuid. "
                "The projection carries determinations for instances that are not the resident "
                "bundles, so the candidate side of the comparison has no bound value. The "
                "instrument falls back to the no-op baseline alone and caps at HOLD. The "
                "rewards committed beside the rollouts are recorded as evidence and are not "
                "read as the projected candidate, because a producer-written reward is the "
                "artifact under audit rather than a measurement of it."
            ),
        ),
        CoverageGap(
            gap_id="D-REF-DISCRIMINATION-UNMEASURED",
            instrument=DISCRIMINATION,
            surface="reference_emulation",
            reason="real-versus-candidate-separation-unmeasured",
            caps=Disposition.HOLD,
            subject="project",
            statement=(
                "The separation between the real-upstream score and the candidate score was "
                "not measured, because neither score exists: the real score is blocked by "
                "D-REF-UPSTREAM-UNOBTAINABLE and the candidate score by "
                "D-REF-CANDIDATE-UNPROJECTED. The margin of "
                f"{DISCRIMINATION_MARGIN} is recorded with its basis so that a later run "
                "applies a threshold fixed before the data existed."
            ),
        ),
    ]

    return InstrumentResult(
        instrument=DISCRIMINATION,
        ran=True,
        findings=[],
        gaps=gaps,
        artifacts=[],
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes={
            "discrimination_margin": DISCRIMINATION_MARGIN,
            "discrimination_margin_basis": DISCRIMINATION_MARGIN_BASIS,
            "scope_binds_numeric_threshold": False,
            "crucible_view_present": view_path.is_file(),
            "crucible_view_digest": _digest_or_none(view_path),
            "rows": rows,
            "committed_rollout_rewards": committed,
        },
    )


def run_divergence(base: Path) -> InstrumentResult:
    """G-REF-DIVERGENCE-TAXONOMY: classify divergence into exactly four classes.

    The measured half needs real-artifact check failures and there are none,
    because the artifact was never obtained. That absence is a named gap and is
    never softened into a zero count, since a taxonomy reporting zero failures
    reads as a clean result and this one is not a result at all.

    The half that does run is a static classification of the committed interface
    specification. Every entry in every ``[interface_spec]`` block is classified
    by shape, per-class counts are recorded, and each class names the committed
    harness locations that would surface a failure of that kind. Every
    recognized entry lands in ``invented-or-assumed-interface``, which is the
    substantive result: a names-only specification asserts identifiers and not
    behaviour, so a checker built on it cannot distinguish a real implementation
    from a stub carrying the same identifiers. That is a retained finding, not a
    remark, because it bounds what any pass of these checkers can mean.

    An entry matching no recognized shape is recorded verbatim and carries its
    own fail-closed finding, so the counts can never read as covering the whole
    specification when they do not.
    """
    findings: list[Finding] = []
    per_bundle: list[dict[str, Any]] = []
    unclassifiable: list[dict[str, Any]] = []
    totals = dict.fromkeys(DIVERGENCE_CLASSES, 0)

    for bundle in bundles_of(base):
        spec = interface_spec(bundle)
        probes = golden_probes(bundle)
        checkers = committed_checkers(bundle)
        classified = [
            dict(classify_interface_entry(row["entry"]), issue=row["issue"])
            for row in spec["entries"]
        ]
        counts = dict.fromkeys(DIVERGENCE_CLASSES, 0)
        for row in classified:
            name = row["divergence_class"]
            if name in counts:
                counts[name] += 1
                totals[name] += 1
            else:
                unclassifiable.append(
                    {"uuid": bundle.name, "issue": row["issue"], "entry": row["entry"]}
                )
        loci = _harness_loci(bundle, probes, checkers)
        loci["invented-or-assumed-interface"]["count"] = counts["invented-or-assumed-interface"]
        per_bundle.append(
            {
                "uuid": bundle.name,
                "interface_mode": spec["mode"],
                "entry_count": spec["entry_count"],
                "per_class_counts": counts,
                "classified_entries": classified,
                "implicated_harness_locations": loci,
                "shape_histogram": {
                    shape: sum(1 for row in classified if row["shape"] == shape)
                    for shape in (*INTERFACE_SHAPES, "unclassifiable")
                },
            }
        )

        if spec["mode"] == "names-only" and spec["entry_count"]:
            findings.append(
                Finding(
                    finding_id=f"REF-NAMES-ONLY-INTERFACE-{bundle.name}",
                    instrument=DIVERGENCE,
                    critical_class=CRITICAL_CLASS,
                    severity=Severity.HIGH,
                    caps=Disposition.HOLD,
                    bucket=Bucket.D,
                    subject=bundle.name,
                    statement=(
                        f"The committed interface specification declares mode {spec['mode']!r} "
                        f"over {spec['entry_count']} entries, and every entry asserts an "
                        "identifier without asserting behaviour. A checker built on such an "
                        "entry is satisfied by any implementation carrying the name, including "
                        "a stub that returns immediately, so it cannot distinguish a real "
                        "implementation from an invented or assumed one. This is the shape "
                        "that produces invented-or-assumed-interface divergence against a real "
                        "upstream artifact, and it bounds what a pass of these checkers can mean."
                    ),
                    evidence={
                        "uuid": bundle.name,
                        "interface_mode": spec["mode"],
                        "issue_keys": spec["issue_keys"],
                        "entry_count": spec["entry_count"],
                        "per_class_counts": counts,
                        "manifest_digest": _digest_or_none(bundle / "task.toml"),
                        "classification_mode": "static-specification",
                    },
                )
            )

    if unclassifiable:
        findings.append(
            Finding(
                finding_id="REF-DIVERGENCE-UNCLASSIFIABLE",
                instrument=DIVERGENCE,
                critical_class=CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject="project",
                statement=(
                    f"{len(unclassifiable)} committed interface-specification entries match no "
                    "recognized shape and therefore fall into none of the four divergence "
                    "classes. They are recorded verbatim below. The taxonomy fails closed on "
                    "them rather than dropping them, because a per-class count that silently "
                    "omits an entry reads as covering the whole specification when it does not."
                ),
                evidence={"verbatim_entries": unclassifiable},
            )
        )

    gaps = [
        CoverageGap(
            gap_id="D-REF-DIVERGENCE-UNMEASURED",
            instrument=DIVERGENCE,
            surface="reference_emulation",
            reason="real-artifact-failures-unavailable",
            caps=Disposition.HOLD,
            subject="project",
            statement=(
                "No real-artifact check failure was classified, because no real artifact was "
                "obtained and no replay produced failures to classify. The per-class counts "
                "recorded by this instrument are a static classification of the committed "
                "interface specification and are labelled as such; they are not a measured "
                "classification of real-artifact failures and must never be read as one. A "
                "taxonomy reporting zero measured failures would read as a clean result, and "
                "this instrument has no result of that kind to report."
            ),
        )
    ]

    return InstrumentResult(
        instrument=DIVERGENCE,
        ran=True,
        findings=findings,
        gaps=gaps,
        artifacts=[],
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes={
            "classification_mode": "static-specification",
            "measured_classification_available": False,
            "divergence_classes": list(DIVERGENCE_CLASSES),
            "per_class_counts_over_specification": totals,
            "unclassifiable_entries": unclassifiable,
            "bundles": per_bundle,
        },
    )


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
    """Execute the step 8d reference-fidelity family and return every result.

    The reconnaissance record is accepted because crucible.py's dispatch passes
    it to every family. The recorded bundle roster is carried into the obtain
    instrument's notes so a later reader can see which corpus the run reasoned
    over, while the upstream identities themselves are re-derived from committed
    bytes, because consuming a pre-derived answer would make the derivation
    vacuous.
    """
    results = [
        _guard(OBTAIN, run_obtain, base),
        _guard(REPLAY, run_replay, base),
        _guard(DISCRIMINATION, run_discrimination, base),
        _guard(DIVERGENCE, run_divergence, base),
    ]
    recorded = getattr(reconnaissance, "bundles", None)
    if isinstance(recorded, list):
        results[0].notes["recon_bundle_roster"] = [
            str(row.get("uuid", "")) for row in recorded if isinstance(row, dict)
        ]
    return results


__all__ = [
    "DISCRIMINATION",
    "DIVERGENCE",
    "DIVERGENCE_CLASSES",
    "OBTAIN",
    "REPLAY",
    "UPSTREAM_UNOBTAINABLE_REASON",
    "bundles_of",
    "classify_interface_entry",
    "committed_checkers",
    "committed_rollout_rewards",
    "golden_probes",
    "interface_spec",
    "noop_baseline",
    "run_discrimination",
    "run_divergence",
    "run_family",
    "run_obtain",
    "run_replay",
    "scope_reference_block",
    "upstream_identity",
]
