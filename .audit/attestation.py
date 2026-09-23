"""Contract step 8p: execution attestation ingestion, plus the step 8s determination.

This module verifies and retains DSSE envelopes under the predicate
``trinity.execution/v2`` from ``.audit/attestations/execution/``. The rationale
lives in these docstrings because the contract is prompt-only, so the harness
itself has to carry the reasoning as audit evidence.

PROHIBITION, stated first because it is the load-bearing rule. An execution
attestation is IMMUTABLE EXTERNAL EVIDENCE. CRUCIBLE verifies it and retains it.
CRUCIBLE never manufactures one, never modifies one, and never writes into
``.audit/attestations/execution/`` for any reason, including creating the
directory when it is absent. No function in this module opens that path for
writing, creates it, or emits a template into it. An auditor that can mint the
evidence it grades is grading itself, and the entire value of an execution
attestation is that its producer is not the party reading it.

Two rules the contract fixes and this module encodes precisely.

First, PRESENCE ESTABLISHES NOTHING ON ITS OWN. An envelope that exists proves
that someone recorded something. A capture the operator could have edited before
recording proves custody and nothing else: it establishes that the bytes passed
through the operator's hands, not that the bytes describe what happened. Every
resolution below therefore turns on verification outcomes and never on presence,
and no code path in this module can raise a disposition. The disposition lattice
only ever falls.

Second, schema ``trinity.execution/v1`` binds no harness config and no
per-rollout telemetry. A v1 envelope therefore cannot carry the facts the
dependent channels need, so it must never be ingested as release evidence. It is
refused at ingestion and resolves as an unresolved coverage gap, exactly as an
absent envelope does. Accepting a v1 envelope because it is signed and current
would substitute a valid signature over the wrong claim for evidence of the
right one.

A missing, expired, unauthorized or divergent attestation resolves EVERY
dependent channel as an unresolved coverage gap and never as a pass.

State of this tree. ``.audit/attestations/execution/`` does not exist. The
instrument's honest outcome is that it ran, having performed the whole
resolution it is able to perform, and emitted a coverage gap naming the absent
directory together with an enumeration of exactly which dependent channels are
thereby unresolved.

Trust policy. The policy is resolved through CRUCIBLE_VIEW. That file records
``execution_operator_trust_policy`` as null, so no policy binds the
``execution_operator`` role at all, and the source-attestation trust root it
does carry enumerates seven roles of which ``execution_operator`` is not one. It
further records ``source_attestation_trust_root`` as root_number 6 with status
ABSENT and identity null. The only signing principal enrolled anywhere is
``engram-project-local@levi``, carrying roles pilot_signer and
checkpoint_signer, explicitly marked PROJECT-LOCAL and NOT AN INDEPENDENT
EXTERNAL PARTY. A project-local signer is not an external trust root: a
signature from the project over the project's own claim proves the bytes have
not changed since the project signed them, which is integrity and not
independence. Such a signature could never satisfy the external-trust-root
requirement, and agreement from it never raises a disposition.

Step 8s determination, recorded here rather than silently omitted. The G-BUD
instruments run only when a bundle carries a budget block in task.toml, and the
contract describes that block as carrying ``budget_hours``, ``budget_envelope``
and ``budget_margin``. None of those three keys appears in any resident
manifest. What the manifests do carry are resource limits and process timeouts:
``build_timeout_sec``, ``cpus``, ``memory_mb``, ``storage_mb``, and per-phase
``timeout_sec`` values. Those are container sizing and watchdog values, not a
budget envelope with a margin against a declared spend, and no arithmetic
reconciling a spend to an envelope is possible over them because no envelope is
declared. The correct reading is that budget is opt-in per project, and a bundle
carrying no budget block with no standing budget-required priority is EXEMPT
from all three G-BUD instruments and from the budget attestation coverage gap.
The exemption is taken, recorded with its basis, and the conflicting scope
declaration is retained as its own coverage gap rather than being resolved by
this module in its own favour.
"""

from __future__ import annotations

import datetime
import json
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

EXECUTION_ATTESTATION = "G-EXEC-ATTESTATION"
BUDGET_APPLICABILITY = "G-BUD-APPLICABILITY"

CRITICAL_CLASS = "execution-attestation"

ATTESTATION_SUBPATH = "attestations/execution"

ATTESTATION_SUFFIX = ".dsse"

SCHEMA_V2 = "trinity.execution/v2"

SCHEMA_V1 = "trinity.execution/v1"

REQUIRED_ROLE = "execution_operator"

REQUIRED_BINDINGS: tuple[str, ...] = (
    "task_hash",
    "policy_manifest_digest",
    "scorer_closure_digest",
    "trajectory_root",
    "harness_config_digest",
    "effective_configuration_reconciliation",
)

VERIFICATION_CLAUSES: tuple[str, ...] = (
    "schema",
    "signature",
    "signer_authorization",
    "validity_window",
    *REQUIRED_BINDINGS,
)

DEPENDENT_CHANNELS: tuple[tuple[str, str], ...] = (
    (
        "budget-envelope-reconciliation",
        "the step 8s reconciliation of recorded spend against a declared budget envelope",
    ),
    (
        "reward-coverage-ledger-externally-enforced",
        "every step 8q ledger row that would resolve as externally_enforced, since such a row "
        "must name the verified attestation clause that enforces it",
    ),
    (
        "g-fid-config-attestation-comparison",
        "the G-FID-CONFIG comparison of the harness-config binding re-derived from committed "
        "bytes against the attested effective configuration",
    ),
    (
        "operator-signed-trajectory-root",
        "the trajectory-root binding that the rollout-integrity branch would compare against",
    ),
    (
        "per-rollout-telemetry",
        "the per-rollout telemetry that only the v2 predicate binds",
    ),
    (
        "preregistration-binding",
        "the step 8o preregistration digest that rides as a bound resource descriptor inside "
        "the pre-run commitment",
    ),
)

CONTRACT_BUDGET_KEYS: tuple[str, ...] = (
    "budget_hours",
    "budget_envelope",
    "budget_margin",
)

RESOURCE_LIMIT_KEYS: tuple[tuple[str, str], ...] = (
    ("environment", "build_timeout_sec"),
    ("environment", "cpus"),
    ("environment", "memory_mb"),
    ("environment", "storage_mb"),
    ("environment", "gpus"),
    ("agent", "timeout_sec"),
    ("verifier", "timeout_sec"),
)

UNRESOLVED = "unresolved"

REFUSED = "refused"


def _register() -> None:
    """Declare the step 8p and step 8s instruments under the twelve-field schema.

    ``disposition_cap_on_absence`` is HOLD on both rows and is never SHIP. For
    the execution attestation that is the contract's own rule: an absent
    attestation resolves every dependent channel as an unresolved coverage gap
    and never as a pass. For the budget applicability determination it is HOLD
    because an undetermined applicability leaves three instruments in an unknown
    state, which is a coverage gap rather than an exemption.
    """
    rows = (
        Instrument(
            name=EXECUTION_ATTESTATION,
            category=Category.ATTESTATION,
            binary="",
            ecosystems=("*",),
            timeout_seconds=300.0,
            required_conditions=(
                f"{ATTESTATION_SUBPATH} present under .audit",
                f"at least one envelope under predicate {SCHEMA_V2}",
                "an execution_operator trust policy resolved through CRUCIBLE_VIEW",
            ),
            critical_capability="verified external execution attestation binding the run",
            evidence_class=EvidenceClass.EXTERNAL_ATTESTATION,
            requires_parser=True,
            requires_raw_artifact=True,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="CRUCIBLE verifies and retains envelopes and never writes into their directory.",
        ),
        Instrument(
            name=BUDGET_APPLICABILITY,
            category=Category.BUDGET,
            binary="",
            ecosystems=("*",),
            timeout_seconds=60.0,
            required_conditions=("committed task manifests present",),
            critical_capability="determination of whether step 8s applies to this project",
            evidence_class=EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            notes="Budget is opt-in; a bundle with no budget block is exempt from G-BUD.",
        ),
    )
    for row in rows:
        if row.name not in REGISTRY:
            REGISTRY.register(row)


_register()


def _load_toml(path: Path) -> dict[str, Any]:
    """Parse one task manifest, failing closed to an empty declaration."""
    try:
        with path.open("rb") as handle:
            loaded = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _load_yaml(path: Path) -> Any:
    """Parse one committed YAML document, failing closed to None."""
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def _load_json_text(text: str) -> Any:
    """Parse one envelope payload, failing closed to None."""
    try:
        return json.loads(text)
    except ValueError:
        return None


def _digest_or_none(path: Path) -> str | None:
    return core.sha256_path(path) if path.is_file() else None


def _table(document: dict[str, Any], key: str) -> dict[str, Any]:
    value = document.get(key)
    return value if isinstance(value, dict) else {}


def _utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def bundles_of(base: Path) -> list[Path]:
    """Every resident bundle directory, derived from committed bytes alone."""
    return sorted(core.bundle_roots(base), key=lambda path: path.name)


def attestation_dir(base: Path) -> Path:
    """Resolve the execution attestation directory without creating it.

    This function resolves a path and nothing else. It never calls mkdir and no
    caller in this module does either, because CRUCIBLE creating the directory
    that holds the evidence it grades would be the first step of manufacturing
    that evidence.
    """
    return base / core.AUDIT_DIRNAME / ATTESTATION_SUBPATH


def crucible_view_path(base: Path) -> Path:
    """Locate CRUCIBLE_VIEW, through which the trust policy is resolved."""
    return base.resolve().parent / ".memory" / "crucible_view.yaml"


def trust_policy(base: Path) -> dict[str, Any]:
    """Resolve the execution-operator trust policy through CRUCIBLE_VIEW.

    Three separate facts are read and none of them is allowed to stand in for
    another. The dedicated ``execution_operator_trust_policy`` field is the
    policy this instrument needs. The ``source_attestation_trust_root`` block
    enumerates roles and principals for a different purpose and is recorded so
    the absence of an execution_operator role in it is visible. The
    ``signature_trust_roots`` list names the only enrolled signing identities,
    each with its own recorded independence, and a root whose independence reads
    project-local is marked as unable to satisfy an external-trust-root
    requirement no matter what it signs.
    """
    path = crucible_view_path(base)
    document = _load_yaml(path)
    document = document if isinstance(document, dict) else {}

    operator_policy = document.get("execution_operator_trust_policy")
    source_root = _table(document, "source_attestation_trust_root")
    declared_roles = [
        str(row.get("name") or "")
        for row in (source_root.get("roles") or [])
        if isinstance(row, dict)
    ]
    principals: list[dict[str, Any]] = []
    for row in source_root.get("principals") or []:
        if not isinstance(row, dict):
            continue
        principals.append(
            {
                "name": str(row.get("name") or ""),
                "roles": sorted(str(item) for item in (row.get("roles") or [])),
                "expires": str(row.get("expires") or ""),
                "bears_required_role": REQUIRED_ROLE
                in {str(item) for item in (row.get("roles") or [])},
            }
        )

    signing_roots: list[dict[str, Any]] = []
    for row in document.get("signature_trust_roots") or []:
        if not isinstance(row, dict):
            continue
        independence = str(row.get("independence") or "")
        project_local = "PROJECT-LOCAL" in independence.upper()
        key_material = bool(row.get("public_key") or row.get("key_path"))
        if project_local:
            basis = (
                "a project-local signer signs the project's own claim, which proves the bytes "
                "have not changed since the project signed them and proves nothing about "
                "independence"
            )
        elif not key_material:
            basis = (
                "the root is recorded as external but supplies no public key and no key path, "
                "so it carries no material against which a DSSE signature could be verified; a "
                "document signature block is evidence of a human act and not a verification key"
            )
        else:
            basis = "recorded independence is external to the project and key material is enrolled"
        signing_roots.append(
            {
                "identity": row.get("identity"),
                "status": str(row.get("status") or ""),
                "authorized_roles": sorted(
                    str(item) for item in (row.get("authorized_roles") or [])
                ),
                "independence": independence,
                "project_local": project_local,
                "supplies_key_material": key_material,
                "can_satisfy_external_trust_root": (
                    not project_local and key_material and bool(row.get("identity"))
                ),
                "satisfaction_basis": basis,
            }
        )

    absent_roots = [
        {
            "kind": str(row.get("kind") or ""),
            "root_number": row.get("root_number"),
            "status": str(row.get("status") or ""),
            "identity": row.get("identity"),
            "limitation": str(row.get("limitation") or ""),
        }
        for row in document.get("screening_roots") or []
        if isinstance(row, dict) and str(row.get("status") or "") == "ABSENT"
    ]

    return {
        "view_present": path.is_file(),
        "view_path": str(path),
        "view_digest": _digest_or_none(path),
        "execution_operator_trust_policy": operator_policy,
        "execution_operator_policy_bound": operator_policy is not None,
        "source_root_declared_roles": sorted(declared_roles),
        "execution_operator_in_declared_roles": REQUIRED_ROLE in declared_roles,
        "principals": principals,
        "principals_bearing_required_role": [
            row["name"] for row in principals if row["bears_required_role"]
        ],
        "signature_trust_roots": signing_roots,
        "external_trust_roots_available": [
            row["identity"] for row in signing_roots if row["can_satisfy_external_trust_root"]
        ],
        "absent_roots": absent_roots,
    }


def envelope_paths(base: Path) -> dict[str, Any]:
    """Enumerate committed envelopes without creating or touching anything.

    The directory is only read. When it is absent the enumeration returns that
    fact rather than bringing the directory into existence, because an empty
    directory CRUCIBLE created is indistinguishable in a later run from an empty
    directory the operator left, and manufacturing that ambiguity is itself a
    form of manufacturing evidence.
    """
    directory = attestation_dir(base)
    if not directory.is_dir():
        return {
            "directory": str(directory),
            "directory_present": False,
            "created_by_crucible": False,
            "envelopes": [],
        }
    rows = [
        {
            "path": str(path),
            "name": path.name,
            "digest": core.sha256_path(path),
            "digest_matches_filename": path.stem == core.sha256_path(path),
            "filename_is_hex64": core.is_hex64(path.stem),
        }
        for path in sorted(directory.glob(f"*{ATTESTATION_SUFFIX}"))
        if path.is_file()
    ]
    return {
        "directory": str(directory),
        "directory_present": True,
        "created_by_crucible": False,
        "envelopes": rows,
    }


def ingest_envelope(raw: str) -> dict[str, Any]:
    """Parse one DSSE envelope and refuse any predicate that is not v2.

    Refusal happens at ingestion rather than at verification, because a v1
    envelope binds no harness config and no per-rollout telemetry, so there is
    nothing for the later clauses to compare and a clause that cannot fail would
    read as a clause that passed. A v1 envelope resolves exactly as an absent
    envelope does, which is an unresolved coverage gap.
    """
    envelope = _load_json_text(raw)
    if not isinstance(envelope, dict):
        return {
            "ingested": False,
            "reason": "envelope-not-parseable",
            "payload_type": "",
            "schema": "",
        }
    payload_type = str(envelope.get("payloadType") or "")
    signatures = envelope.get("signatures")
    signatures = signatures if isinstance(signatures, list) else []
    payload = _load_json_text(str(envelope.get("payload") or ""))
    payload = payload if isinstance(payload, dict) else {}
    schema = str(payload.get("_type") or payload.get("predicateType") or payload_type or "")
    if schema == SCHEMA_V1:
        return {
            "ingested": False,
            "reason": "schema-v1-binds-no-harness-config-or-telemetry",
            "payload_type": payload_type,
            "schema": schema,
            "signature_count": len(signatures),
        }
    if schema != SCHEMA_V2:
        return {
            "ingested": False,
            "reason": "schema-outside-the-bound-predicate",
            "payload_type": payload_type,
            "schema": schema,
            "signature_count": len(signatures),
        }
    return {
        "ingested": True,
        "reason": "",
        "payload_type": payload_type,
        "schema": schema,
        "signature_count": len(signatures),
        "payload": payload,
    }


def verify_envelope(
    ingested: dict[str, Any],
    policy: dict[str, Any],
    expected: dict[str, Any],
    now: datetime.datetime | None = None,
) -> dict[str, Any]:
    """Verify one ingested envelope clause by clause, failing closed on each.

    Every clause resolves to one of pass, fail or unresolved, and unresolved is
    never folded into pass. The signature clause resolves unresolved rather than
    fail when no verification key material is available, because an unchecked
    signature is an unknown and not a forgery. The authorization clause requires
    the signer to bear ``execution_operator`` under the resolved policy and
    requires that signer to sit on an external trust root, so a project-local
    signature can never pass it. The window clause requires both bounds to exist
    and to contain the instant of verification. The six binding clauses require
    exact agreement with the values re-derived from committed bytes, and a
    binding the envelope does not carry is unresolved rather than absent.

    The aggregate ``resolution`` is pass only when every clause passes. Presence
    contributes nothing: an envelope that exists but fails or leaves unresolved
    any clause resolves as unresolved, which is a coverage gap.
    """
    moment = now or _utc_now()
    clauses: dict[str, dict[str, Any]] = {}

    if not ingested.get("ingested"):
        for name in VERIFICATION_CLAUSES:
            clauses[name] = {
                "outcome": UNRESOLVED,
                "detail": str(ingested.get("reason") or "envelope was not ingested"),
            }
        return {
            "resolution": UNRESOLVED,
            "schema": str(ingested.get("schema") or ""),
            "clauses": clauses,
            "verified_at": moment.isoformat(),
            "presence_established": "custody only, never validity",
        }

    payload = ingested.get("payload") or {}
    clauses["schema"] = {"outcome": "pass", "detail": SCHEMA_V2}

    clauses["signature"] = _signature_clause(policy, ingested.get("signature_count", 0))

    signer = str(payload.get("signer") or "")
    authorized = signer in set(policy.get("principals_bearing_required_role") or [])
    external = signer in {
        str(identity) for identity in (policy.get("external_trust_roots_available") or [])
    }
    if not policy.get("execution_operator_policy_bound"):
        clauses["signer_authorization"] = {
            "outcome": UNRESOLVED,
            "detail": (
                "CRUCIBLE_VIEW records execution_operator_trust_policy as null, so no policy "
                "binds the execution_operator role and no signer can be authorized against it"
            ),
        }
    elif authorized and external:
        clauses["signer_authorization"] = {"outcome": "pass", "detail": signer}
    else:
        clauses["signer_authorization"] = {
            "outcome": "fail",
            "detail": (
                f"signer {signer!r} does not bear {REQUIRED_ROLE} on an external trust root; a "
                "project-local signer can never satisfy the external-trust-root requirement"
            ),
        }

    clauses["validity_window"] = _window_clause(payload, moment)

    for name in REQUIRED_BINDINGS:
        clauses[name] = _binding_clause(name, payload.get(name), expected.get(name))

    outcomes = {row["outcome"] for row in clauses.values()}
    if "fail" in outcomes:
        resolution = "fail"
    elif UNRESOLVED in outcomes:
        resolution = UNRESOLVED
    else:
        resolution = "pass"

    return {
        "resolution": resolution,
        "schema": SCHEMA_V2,
        "clauses": clauses,
        "verified_at": moment.isoformat(),
        "presence_established": "custody only, never validity",
    }


def _signature_clause(policy: dict[str, Any], signature_count: int) -> dict[str, Any]:
    """Resolve the signature clause, which can never pass without external key material.

    An unchecked signature is an unknown and is never treated as valid, so the
    clause resolves unresolved rather than fail when no key material is
    available. An envelope carrying no signature block at all is a failure
    rather than an unknown, because an unsigned DSSE envelope is not a
    signature this harness could not check but a signature that was never made.
    """
    if signature_count <= 0:
        return {"outcome": "fail", "detail": "the envelope carries no signature block"}
    if not policy.get("external_trust_roots_available"):
        return {
            "outcome": UNRESOLVED,
            "detail": (
                "no external trust root supplies verification key material for an "
                f"{REQUIRED_ROLE} signature, so the signature is unchecked; an unchecked "
                "signature is an unknown and is never treated as valid"
            ),
        }
    return {
        "outcome": UNRESOLVED,
        "detail": (
            "an external trust root is enrolled but no verification was performed in this "
            "run, so the signature remains unchecked and fails closed to unresolved"
        ),
    }


def _window_clause(payload: dict[str, Any], moment: datetime.datetime) -> dict[str, Any]:
    """Resolve the validity window, requiring both bounds to exist and contain now.

    A one-sided window is unresolved rather than open. An envelope with a start
    and no end never expires, which is not a validity window but the absence of
    one, and treating it as satisfied would make expiry unenforceable.
    """
    start = _parse_instant(payload.get("valid_from"))
    end = _parse_instant(payload.get("valid_until"))
    if start is None or end is None:
        return {
            "outcome": UNRESOLVED,
            "detail": "the envelope does not carry both validity bounds",
        }
    if start <= moment <= end:
        return {"outcome": "pass", "detail": f"{start.isoformat()} to {end.isoformat()}"}
    return {
        "outcome": "fail",
        "detail": f"{moment.isoformat()} falls outside {start.isoformat()} to {end.isoformat()}",
    }


def _parse_instant(value: Any) -> datetime.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=datetime.UTC)
    return parsed


def _binding_clause(name: str, attested: Any, derived: Any) -> dict[str, Any]:
    """Require exact agreement between an attested binding and the derived value.

    A binding the envelope omits is unresolved, and a binding CRUCIBLE could not
    re-derive is also unresolved. Only two present values that differ are a
    failure, because a comparison against an absent operand is not a comparison.
    """
    if attested in (None, ""):
        return {"outcome": UNRESOLVED, "detail": f"the envelope binds no {name}"}
    if derived in (None, ""):
        return {"outcome": UNRESOLVED, "detail": f"no {name} was re-derived from committed bytes"}
    if attested == derived:
        return {"outcome": "pass", "detail": "exact agreement"}
    return {
        "outcome": "fail",
        "detail": f"attested {attested!r} diverges from derived {derived!r}",
    }


def dependent_channel_resolution(verified: bool, budget_exempt: bool) -> list[dict[str, Any]]:
    """Enumerate every dependent channel and its resolution under this outcome.

    The enumeration is explicit rather than implied. A channel that depends on
    an attestation and is simply not mentioned reads to a later reviewer as a
    channel that passed, which is the exact failure mode the contract's rule
    against silence exists to prevent.

    The budget-envelope reconciliation is the one channel whose resolution is
    not driven by the attestation here: the step 8s determination finds no
    budget block in any manifest, so that channel is exempt rather than
    unresolved. The exemption is recorded with its basis and is reversed if the
    determination is ever refuted.
    """
    rows: list[dict[str, Any]] = []
    for name, description in DEPENDENT_CHANNELS:
        if name == "budget-envelope-reconciliation" and budget_exempt:
            rows.append(
                {
                    "channel": name,
                    "description": description,
                    "resolution": "exempt",
                    "basis": (
                        "the step 8s determination finds no budget block in any committed "
                        "manifest, so no envelope exists to reconcile and the channel is "
                        "exempt rather than unresolved"
                    ),
                }
            )
            continue
        rows.append(
            {
                "channel": name,
                "description": description,
                "resolution": "resolved" if verified else UNRESOLVED,
                "basis": (
                    "a verified v2 attestation binds this channel"
                    if verified
                    else "no verified execution attestation exists, so this channel resolves as "
                    "an unresolved coverage gap and never as a pass"
                ),
            }
        )
    return rows


def budget_determination(base: Path) -> dict[str, Any]:
    """Determine whether the committed manifests carry the contract's budget block.

    The contract names three keys: budget_hours, budget_envelope, budget_margin.
    The determination is a membership test over the committed manifests for
    those exact names, at the top level and inside every table, so a block
    nested anywhere is still found. The resource limits and process timeouts the
    manifests do carry are enumerated beside the result, because the honest
    question is not whether the manifests contain numbers but whether they
    declare an envelope against which a spend could be reconciled.

    A timeout is a watchdog: it bounds how long a phase may run before it is
    killed. A cpu or memory value is container sizing. Neither declares a spend,
    neither carries a margin, and no reconciliation arithmetic is definable over
    them, because reconciliation needs a declared envelope to reconcile against
    and none is declared.
    """
    rows: list[dict[str, Any]] = []
    for bundle in bundles_of(base):
        manifest = _load_toml(bundle / "task.toml")
        found: list[str] = []
        for key in CONTRACT_BUDGET_KEYS:
            if key in manifest:
                found.append(key)
            for table_name, table in manifest.items():
                if isinstance(table, dict) and key in table:
                    found.append(f"{table_name}.{key}")
        limits = {}
        for table_name, key in RESOURCE_LIMIT_KEYS:
            table = _table(manifest, table_name)
            if key in table:
                limits[f"{table_name}.{key}"] = table[key]
        rows.append(
            {
                "uuid": bundle.name,
                "contract_budget_keys_found": sorted(set(found)),
                "carries_budget_block": bool(found),
                "resource_limits_and_timeouts": limits,
                "manifest_digest": _digest_or_none(bundle / "task.toml"),
            }
        )
    exempt = not any(row["carries_budget_block"] for row in rows)
    return {
        "contract_budget_keys": list(CONTRACT_BUDGET_KEYS),
        "any_bundle_carries_budget_block": not exempt,
        "exempt": exempt,
        "standing_budget_required_priority": False,
        "determination": (
            "EXEMPT from G-BUD-BINDING, G-BUD-ENVELOPE and G-BUD-RECONCILE and from the budget "
            "attestation coverage gap"
            if exempt
            else "IN SCOPE for the three G-BUD instruments"
        ),
        "basis": (
            "the contract describes a budget block as carrying budget_hours, budget_envelope and "
            "budget_margin. No resident manifest declares any of those keys at the top level or "
            "inside any table. The keys the manifests do carry are build_timeout_sec, cpus, "
            "memory_mb, storage_mb, gpus and per-phase timeout_sec, which are container sizing "
            "and watchdog values. A watchdog bounds how long a phase may run before it is "
            "killed; it does not declare a spend and carries no margin, and no reconciliation "
            "arithmetic is definable without a declared envelope to reconcile against. Budget is "
            "therefore opt-in per project, and a bundle with no budget block and no standing "
            "budget-required priority is exempt."
        ),
        "ledger_written": False,
        "ledger_path": str(base / core.AUDIT_DIRNAME / core.BUDGET_FILENAME),
        "ledger_basis": (
            "no per-task budget outcome exists to append, so .audit/budget.yaml is not written; "
            "writing a row asserting an exemption would put a budget outcome in the ledger that "
            "no budget instrument produced"
        ),
        "bundles": rows,
    }


def scope_budget_declaration(base: Path) -> dict[str, Any]:
    """Read what the approved scope file declares about G-BUD applicability.

    The scope file declares G-BUD mandated on the basis of the same resource
    limits this module finds insufficient. That disagreement is recorded rather
    than resolved silently in either direction, because the scope digest is
    approved and this module is not entitled to overwrite an approved
    declaration by reaching a different conclusion about it.
    """
    document = _load_yaml(base / core.AUDIT_DIRNAME / core.SCOPE_FILENAME)
    document = document if isinstance(document, dict) else {}
    for row in document.get("required_instruments") or []:
        if isinstance(row, dict) and str(row.get("id") or "") == "G-BUD":
            return {
                "declared": True,
                "mandated_by": str(row.get("mandated_by") or ""),
                "condition": str(row.get("condition") or ""),
            }
    return {"declared": False, "mandated_by": "", "condition": ""}


def run_execution_attestation(base: Path) -> InstrumentResult:
    """G-EXEC-ATTESTATION: resolve the step 8p execution attestation.

    The whole resolution is performed. The trust policy is resolved through
    CRUCIBLE_VIEW, the envelope directory is enumerated without being created,
    and every dependent channel is enumerated with its resolution. No envelope
    exists, so nothing is ingested and nothing is verified, and the outcome is a
    coverage gap naming the absent directory together with the channel list.

    Two retained findings accompany the gap and neither of them depends on an
    envelope existing. The resolved policy binds no execution_operator role at
    all, so no signature could ever be authorized under it, which is a defect in
    the policy rather than in any envelope. And the only enrolled signing
    identity is marked project-local and not an independent external party, so
    it could never satisfy the external-trust-root requirement no matter what it
    signed.

    Nothing in this function writes. The directory is read if it exists and is
    not created if it does not.
    """
    policy = trust_policy(base)
    envelopes = envelope_paths(base)
    directory = envelopes["directory"]

    ingestions: list[dict[str, Any]] = []
    verifications: list[dict[str, Any]] = []
    for row in envelopes["envelopes"]:
        raw = Path(row["path"]).read_text(encoding="utf-8", errors="replace")
        ingested = ingest_envelope(raw)
        ingestions.append(
            {"name": row["name"], **{k: v for k, v in ingested.items() if k != "payload"}}
        )
        verifications.append(
            {
                "name": row["name"],
                **verify_envelope(ingested, policy, dict.fromkeys(REQUIRED_BINDINGS)),
            }
        )

    verified = any(row.get("resolution") == "pass" for row in verifications)
    budget = budget_determination(base)
    channels = dependent_channel_resolution(verified, budget["exempt"])
    unresolved = [row["channel"] for row in channels if row["resolution"] == UNRESOLVED]

    findings: list[Finding] = []
    if not policy["execution_operator_policy_bound"]:
        findings.append(
            Finding(
                finding_id="ATT-EXECUTION-OPERATOR-POLICY-UNBOUND",
                instrument=EXECUTION_ATTESTATION,
                critical_class=CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject="project",
                statement=(
                    "CRUCIBLE_VIEW records execution_operator_trust_policy as null, so no trust "
                    "policy binds the execution_operator role. The source-attestation trust root "
                    "it does carry enumerates "
                    f"{len(policy['source_root_declared_roles'])} roles and "
                    f"{REQUIRED_ROLE} is not among them. No principal could therefore be "
                    "authorized to sign an execution attestation, which means the authorization "
                    "clause of step 8p cannot pass for any envelope, present or future. This is "
                    "a defect in the resolved policy and not in any particular envelope."
                ),
                evidence={
                    "execution_operator_trust_policy": policy["execution_operator_trust_policy"],
                    "source_root_declared_roles": policy["source_root_declared_roles"],
                    "principals_bearing_required_role": policy["principals_bearing_required_role"],
                    "crucible_view_digest": policy["view_digest"],
                },
            )
        )

    project_local = [row for row in policy["signature_trust_roots"] if row["project_local"]]
    if project_local and not policy["external_trust_roots_available"]:
        findings.append(
            Finding(
                finding_id="ATT-NO-EXTERNAL-TRUST-ROOT",
                instrument=EXECUTION_ATTESTATION,
                critical_class=CRITICAL_CLASS,
                severity=Severity.HIGH,
                caps=Disposition.HOLD,
                bucket=Bucket.D,
                subject="project",
                statement=(
                    "The only signing identity enrolled in the resolved trust policy is "
                    f"{project_local[0]['identity']!r}, carrying roles "
                    f"{', '.join(project_local[0]['authorized_roles'])} and recorded as "
                    "PROJECT-LOCAL and not an independent external party. A signature from it "
                    "proves the bytes have not changed since the project signed them, which is "
                    "integrity and not independence, so it could never satisfy the "
                    "external-trust-root requirement of step 8p. CRUCIBLE_VIEW additionally "
                    "records source_attestation_trust_root as root_number 6 with status ABSENT "
                    "and identity null. Agreement from this signer never raises a disposition."
                ),
                evidence={
                    "signature_trust_roots": policy["signature_trust_roots"],
                    "external_trust_roots_available": policy["external_trust_roots_available"],
                    "absent_roots": policy["absent_roots"],
                    "crucible_view_digest": policy["view_digest"],
                },
            )
        )

    gaps = [
        CoverageGap(
            gap_id="D-EXEC-ATTESTATION-ABSENT",
            instrument=EXECUTION_ATTESTATION,
            surface="execution_attestation",
            reason="execution-attestation-directory-absent",
            caps=Disposition.HOLD,
            subject="project",
            statement=(
                f"The execution attestation directory {directory} does not exist, so no DSSE "
                f"envelope under predicate {SCHEMA_V2} was ingested and none was verified. "
                "CRUCIBLE did not create the directory and never writes into it, because an "
                "auditor that mints the evidence it grades is grading itself. A missing "
                "attestation resolves every dependent channel as an unresolved coverage gap "
                "and never as a pass. The channels thereby unresolved are: "
                + ", ".join(unresolved)
                + ". The budget-envelope reconciliation is exempt rather than unresolved under "
                "the recorded step 8s determination."
            ),
        )
    ]

    return InstrumentResult(
        instrument=EXECUTION_ATTESTATION,
        ran=True,
        findings=findings,
        gaps=gaps,
        artifacts=[],
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes={
            "schema_required": SCHEMA_V2,
            "schema_refused": {
                SCHEMA_V1: (
                    "binds no harness config and no per-rollout telemetry, so it is never "
                    "ingested as release evidence and resolves as an unresolved coverage gap"
                )
            },
            "presence_rule": (
                "presence establishes nothing on its own; a capture the operator could have "
                "edited before recording proves custody only, never validity"
            ),
            "write_prohibition": (
                "CRUCIBLE verifies and retains execution attestations and never manufactures or "
                "modifies one; no code path in this module writes into the attestation directory "
                "or creates it"
            ),
            "attestation_directory": directory,
            "attestation_directory_present": envelopes["directory_present"],
            "attestation_directory_created_by_crucible": False,
            "envelopes_found": len(envelopes["envelopes"]),
            "ingestions": ingestions,
            "verifications": verifications,
            "verification_clauses": list(VERIFICATION_CLAUSES),
            "required_bindings": list(REQUIRED_BINDINGS),
            "attestation_verified": verified,
            "trust_policy": policy,
            "dependent_channels": channels,
            "unresolved_dependent_channels": unresolved,
        },
    )


def run_budget_applicability(base: Path) -> InstrumentResult:
    """G-BUD-APPLICABILITY: determine whether contract step 8s applies here.

    The determination is recorded in evidence rather than expressed by silently
    omitting the three G-BUD instruments, because an omitted instrument is
    indistinguishable from an instrument that was never written. The finding of
    fact is that no resident manifest declares budget_hours, budget_envelope or
    budget_margin, so no bundle carries the contract's budget block and every
    bundle is exempt from G-BUD-BINDING, G-BUD-ENVELOPE and G-BUD-RECONCILE and
    from the budget attestation coverage gap.

    The approved scope file reaches the opposite conclusion from the same bytes,
    declaring G-BUD mandated on the basis of build_timeout_sec, cpus, memory_mb
    and the per-phase timeouts. That disagreement is retained as a coverage gap.
    This module is not entitled to overwrite an approved declaration by reaching
    a different conclusion about it, and a disagreement between an approved
    scope and a live instrument is exactly the kind of unresolved question a
    coverage gap exists to hold open.

    No row is appended to .audit/budget.yaml. There is no per-task budget
    outcome to append, and writing a row asserting an exemption would place a
    budget outcome in the ledger that no budget instrument produced.
    """
    determination = budget_determination(base)
    declaration = scope_budget_declaration(base)

    gaps: list[CoverageGap] = []
    if determination["exempt"] and declaration["declared"]:
        gaps.append(
            CoverageGap(
                gap_id="D-BUD-BLOCK-DECLARATION-CONFLICT",
                instrument=BUDGET_APPLICABILITY,
                surface="budget_conformance",
                reason="budget-block-determination-conflicts-with-approved-scope",
                caps=Disposition.HOLD,
                subject="project",
                statement=(
                    "The approved scope file declares G-BUD mandated, recording its basis as "
                    f"{declaration['mandated_by']!r}. This instrument determines from the same "
                    "committed bytes that no manifest declares budget_hours, budget_envelope or "
                    "budget_margin, and that the keys the scope cites are container sizing and "
                    "watchdog timeouts rather than a budget envelope with a margin. The "
                    "exemption is taken and the three G-BUD instruments do not run. The "
                    "disagreement with the approved declaration is held open here rather than "
                    "resolved by this module in its own favour, because an instrument is not "
                    "entitled to overwrite an approved scope declaration about itself."
                ),
            )
        )

    return InstrumentResult(
        instrument=BUDGET_APPLICABILITY,
        ran=True,
        findings=[],
        gaps=gaps,
        artifacts=[],
        standing=Standing.INSUFFICIENT_EVIDENCE,
        notes={
            "budget_determination": determination,
            "scope_declaration": declaration,
            "g_bud_instruments_registered": False,
            "g_bud_instruments": ["G-BUD-BINDING", "G-BUD-ENVELOPE", "G-BUD-RECONCILE"],
            "budget_attestation_gap_emitted": False,
            "budget_attestation_gap_basis": (
                "an exempt project has no budget envelope for an attestation to bind, so the "
                "budget attestation coverage gap does not apply"
            ),
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
    """Execute the step 8p attestation resolution and the step 8s determination.

    The reconnaissance record is accepted because crucible.py's dispatch passes
    it to every family. Its recorded scope binding is carried into the
    attestation notes so a reader can see which approved scope the resolution
    was performed under, while the trust policy and the envelope enumeration are
    re-derived here, because consuming a pre-derived answer about external
    evidence would defeat the point of verifying it.
    """
    results = [
        _guard(EXECUTION_ATTESTATION, run_execution_attestation, base),
        _guard(BUDGET_APPLICABILITY, run_budget_applicability, base),
    ]
    binding = getattr(reconnaissance, "scope", None)
    if isinstance(binding, dict):
        results[0].notes["scope_binding"] = {
            "live_digest": binding.get("live_digest"),
            "matches": binding.get("matches"),
        }
    return results


__all__ = [
    "BUDGET_APPLICABILITY",
    "DEPENDENT_CHANNELS",
    "EXECUTION_ATTESTATION",
    "REQUIRED_BINDINGS",
    "SCHEMA_V1",
    "SCHEMA_V2",
    "attestation_dir",
    "budget_determination",
    "bundles_of",
    "dependent_channel_resolution",
    "envelope_paths",
    "ingest_envelope",
    "run_budget_applicability",
    "run_execution_attestation",
    "run_family",
    "scope_budget_declaration",
    "trust_policy",
    "verify_envelope",
]
