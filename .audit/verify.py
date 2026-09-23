"""Verifier rules for submitted findings, per Phase 1 item 10 of trinity/CRUCIBLE.md.

Phase 1 item 10 names eleven rule families this module implements: recall, span
resolution, completed-run evidence, CVSS recomputation, vocabulary, provenance,
scope integrity, command integrity, config integrity, source integrity, and
trusted external signature. The rationale lives here rather than in the contract
because the contract is prompt-only and the house rules place descriptions and
runbooks inside the .audit/ harness.

This module is the only success gate in the harness. Phase 1 item 11 fixes that
``crucible verify`` is the sole command whose success means the gate passed, so
every rule below fails closed: an input this module cannot resolve produces a
violation that caps, never a silent pass.

The rules divide into two directions. Recall, span resolution, completed-run
evidence, CVSS and vocabulary grade the submitted findings document against the
recorded evidence, which is the direction the Phase 2 negative controls probe.
Scope, command, config, source integrity and the external signature grade the
evidence document itself against the live tree, which is the direction the
disposition vocabulary names as the SHIP preconditions.

Bucket N never raises above Bucket D here. The returned disposition is the
minimum of the evidence document's own recorded disposition and every violation
cap this module derives, so a submitted findings document can only ever lower
the gate, never lift it.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any

import yaml

import core
import evidence as evidence_mod
from core import Disposition, Severity

RECALL_RULE = "V-RECALL"
SPAN_RULE = "V-SPAN-RESOLUTION"
COMPLETED_RUN_RULE = "V-COMPLETED-RUN-EVIDENCE"
CVSS_RULE = "V-CVSS-RECOMPUTATION"
VOCABULARY_RULE = "V-VOCABULARY"
PROVENANCE_RULE = "V-PROVENANCE"
SCOPE_RULE = "V-SCOPE-INTEGRITY"
COMMAND_RULE = "V-COMMAND-INTEGRITY"
CONFIG_RULE = "V-CONFIG-INTEGRITY"
SOURCE_RULE = "V-SOURCE-INTEGRITY"
SIGNATURE_RULE = "V-EXTERNAL-SIGNATURE"
ALL_CLEAR_RULE = "V-EMPTY-ALL-CLEAR"
CAP_RULE = "V-DISPOSITION-CAP"

RULES = (
    RECALL_RULE,
    SPAN_RULE,
    COMPLETED_RUN_RULE,
    CVSS_RULE,
    VOCABULARY_RULE,
    PROVENANCE_RULE,
    SCOPE_RULE,
    COMMAND_RULE,
    CONFIG_RULE,
    SOURCE_RULE,
    SIGNATURE_RULE,
    ALL_CLEAR_RULE,
    CAP_RULE,
)

FORBIDDEN_ARGV_TOKENS = ("--config=auto",)
FORBIDDEN_ARGV_PAIRS = (("--config", "auto"),)

_CVSS_PREFIX = "CVSS:3.1/"

_AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
_AC = {"L": 0.77, "H": 0.44}
_PR_UNCHANGED = {"N": 0.85, "L": 0.62, "H": 0.27}
_PR_CHANGED = {"N": 0.85, "L": 0.68, "H": 0.50}
_UI = {"N": 0.85, "R": 0.62}
_CIA = {"H": 0.56, "L": 0.22, "N": 0.0}

_VECTOR_METRIC = re.compile(r"^(AV|AC|PR|UI|S|C|I|A)$")


def _ascii_text(raw: str) -> str:
    return raw.encode("ascii", "backslashreplace").decode("ascii")


def _violation(rule: str, statement: str, caps: Disposition) -> dict[str, Any]:
    """One machine-readable violation row.

    crucible.py echoes ``rule`` and ``statement`` verbatim, so both stay short
    and self-contained: a reviewer reading stderr alone must be able to act.
    """
    return {"rule": rule, "statement": _ascii_text(statement), "caps": caps.token}


def _load_yaml(path: Path) -> tuple[dict[str, Any], str]:
    """Read a YAML mapping, failing closed on anything that is not one."""
    if not path.exists():
        return {}, "absent"
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return {}, f"unparseable: {exc}"
    if not isinstance(loaded, dict):
        return {}, "not-a-mapping"
    return loaded, ""


def roundup(value: float) -> float:
    """CVSS 3.1 roundup, the specification's integer form.

    Floating point rounding is not interchangeable with this operation: the
    specification fixes an integer computation precisely so two implementations
    agree at the boundary, and a naive round() disagrees on values such as
    4.0000000000000005.
    """
    scaled = int(round(value * 100000))
    if scaled % 10000 == 0:
        return scaled / 100000.0
    return (math.floor(scaled / 10000) + 1) / 10.0


def parse_cvss_vector(vector: str) -> tuple[dict[str, str], str]:
    """Split a CVSS 3.1 base vector into its eight base metrics."""
    text = (vector or "").strip()
    if not text.startswith(_CVSS_PREFIX):
        return {}, "vector does not carry the CVSS:3.1 prefix"
    metrics: dict[str, str] = {}
    for part in text[len(_CVSS_PREFIX) :].split("/"):
        if not part:
            continue
        if ":" not in part:
            return {}, f"metric {part} is not name:value"
        name, _, raw = part.partition(":")
        if not _VECTOR_METRIC.match(name):
            return {}, f"metric {name} is outside the base vocabulary"
        metrics[name] = raw
    missing = [name for name in ("AV", "AC", "PR", "UI", "S", "C", "I", "A") if name not in metrics]
    if missing:
        return {}, f"base metrics absent: {','.join(missing)}"
    return metrics, ""


def cvss_base_score(vector: str) -> tuple[float | None, str]:
    """Recompute a CVSS 3.1 base score from its vector.

    Phase 1 item 10 requires recomputation rather than acceptance because a
    declared score is a claim and the vector is the evidence. A vector this
    function cannot parse yields None and a reason, never a default score.
    """
    metrics, reason = parse_cvss_vector(vector)
    if reason:
        return None, reason
    scope_changed = metrics["S"] == "C"
    try:
        av = _AV[metrics["AV"]]
        ac = _AC[metrics["AC"]]
        pr = (_PR_CHANGED if scope_changed else _PR_UNCHANGED)[metrics["PR"]]
        ui = _UI[metrics["UI"]]
        conf = _CIA[metrics["C"]]
        integ = _CIA[metrics["I"]]
        avail = _CIA[metrics["A"]]
    except KeyError as exc:
        return None, f"metric value {exc} is outside the base vocabulary"
    if metrics["S"] not in ("U", "C"):
        return None, f"scope value {metrics['S']} is outside the base vocabulary"

    iss = 1.0 - ((1.0 - conf) * (1.0 - integ) * (1.0 - avail))
    if scope_changed:
        impact = 7.52 * (iss - 0.029) - 3.25 * ((iss - 0.02) ** 15)
    else:
        impact = 6.42 * iss
    if impact <= 0:
        return 0.0, ""
    exploitability = 8.22 * av * ac * pr * ui
    if scope_changed:
        return roundup(min(1.08 * (impact + exploitability), 10.0)), ""
    return roundup(min(impact + exploitability, 10.0)), ""


def _evidence_subjects(document: dict[str, Any]) -> set[str]:
    """Every subject the evidence document actually cites.

    Span resolution is defined against this set rather than against the live
    tree, because Phase 2 item 6 forbids the findings model from citing raw
    files or live code outside evidence.yaml.
    """
    subjects: set[str] = set()
    for row in document.get("findings", []) or []:
        if isinstance(row, dict) and row.get("subject"):
            subjects.add(str(row["subject"]))
    for row in document.get("coverage_gaps", []) or []:
        if isinstance(row, dict) and row.get("subject"):
            subjects.add(str(row["subject"]))
    for result in document.get("instruments", []) or []:
        if not isinstance(result, dict):
            continue
        for row in (result.get("findings") or []) + (result.get("coverage_gaps") or []):
            if isinstance(row, dict) and row.get("subject"):
                subjects.add(str(row["subject"]))
    for bundle in (document.get("recon") or {}).get("bundles", []) or []:
        if isinstance(bundle, dict) and bundle.get("uuid"):
            subjects.add(str(bundle["uuid"]))
    subjects.add("project")
    return subjects


def _evidence_instruments(document: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for result in document.get("instruments", []) or []:
        if isinstance(result, dict) and result.get("instrument"):
            names.add(str(result["instrument"]))
    return names


def _evidence_findings(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in document.get("findings", []) or []:
        if isinstance(row, dict) and row.get("finding_id"):
            rows[str(row["finding_id"])] = row
    return rows


def _blocked_artifacts(document: dict[str, Any]) -> dict[str, str]:
    """Artifact ids that did not complete, keyed to why.

    A blocked or timed out run cited as evidence is a BLOCK in the disposition
    vocabulary, so the reason is carried through to the violation statement
    rather than collapsed to a boolean.
    """
    blocked: dict[str, str] = {}
    for result in document.get("instruments", []) or []:
        if not isinstance(result, dict):
            continue
        for artifact in result.get("raw_artifacts", []) or []:
            if not isinstance(artifact, dict):
                continue
            identifier = str(artifact.get("artifact_id", ""))
            if not identifier:
                continue
            if artifact.get("blocked_reason"):
                blocked[identifier] = str(artifact["blocked_reason"])
            elif artifact.get("timed_out"):
                blocked[identifier] = "timeout"
    return blocked


def _cited_artifacts(row: dict[str, Any]) -> list[str]:
    evidence = row.get("evidence")
    if not isinstance(evidence, dict):
        return []
    cited = evidence.get("raw_artifacts") or evidence.get("artifact_ids") or []
    if isinstance(cited, str):
        return [cited]
    if isinstance(cited, list):
        return [str(item) for item in cited]
    return []


def check_recall(
    submitted: list[dict[str, Any]], recorded: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Every recorded deterministic finding must appear in the submission.

    Omission is the first negative control the contract names. A findings
    document that drops a Bucket-D finding has removed evidence, not judged it,
    so the rule caps at BLOCK exactly as a negative-control failure does.
    """
    submitted_ids = {str(row.get("finding_id", "")) for row in submitted}
    violations: list[dict[str, Any]] = []
    for finding_id, row in sorted(recorded.items()):
        if finding_id in submitted_ids:
            continue
        violations.append(
            _violation(
                RECALL_RULE,
                f"recorded finding {finding_id} from {row.get('instrument', 'unknown')} "
                "is absent from the submitted findings",
                Disposition.BLOCK,
            )
        )
    return violations


def check_spans(submitted: list[dict[str, Any]], subjects: set[str]) -> list[dict[str, Any]]:
    """Every submitted subject must resolve to a subject the evidence cites."""
    violations: list[dict[str, Any]] = []
    for row in submitted:
        subject = str(row.get("subject", ""))
        finding_id = str(row.get("finding_id", "unnamed"))
        if not subject:
            violations.append(
                _violation(
                    SPAN_RULE,
                    f"submitted finding {finding_id} carries no subject",
                    Disposition.BLOCK,
                )
            )
            continue
        if subject in subjects:
            continue
        if any(subject.startswith(f"{known}/") for known in subjects if known != "project"):
            continue
        violations.append(
            _violation(
                SPAN_RULE,
                f"submitted finding {finding_id} cites subject {subject} "
                "which the recorded evidence does not carry",
                Disposition.BLOCK,
            )
        )
    return violations


def check_completed_run_evidence(
    submitted: list[dict[str, Any]], blocked: dict[str, str]
) -> list[dict[str, Any]]:
    """A finding may not rest on a run that did not complete."""
    violations: list[dict[str, Any]] = []
    for row in submitted:
        finding_id = str(row.get("finding_id", "unnamed"))
        for artifact_id in _cited_artifacts(row):
            reason = blocked.get(artifact_id)
            if reason is None:
                continue
            violations.append(
                _violation(
                    COMPLETED_RUN_RULE,
                    f"submitted finding {finding_id} cites artifact {artifact_id} "
                    f"which did not complete: {reason}",
                    Disposition.BLOCK,
                )
            )
    return violations


def check_cvss(submitted: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Any declared CVSS score must recompute from its own vector."""
    violations: list[dict[str, Any]] = []
    for row in submitted:
        finding_id = str(row.get("finding_id", "unnamed"))
        evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
        vector = row.get("cvss_vector") or evidence.get("cvss_vector")
        declared = row.get("cvss_score")
        if declared is None:
            declared = evidence.get("cvss_score")
        if vector is None and declared is None:
            continue
        if vector is None:
            violations.append(
                _violation(
                    CVSS_RULE,
                    f"submitted finding {finding_id} declares a CVSS score with no vector",
                    Disposition.BLOCK,
                )
            )
            continue
        recomputed, reason = cvss_base_score(str(vector))
        if reason:
            violations.append(
                _violation(
                    CVSS_RULE,
                    f"submitted finding {finding_id} carries an unrecomputable vector: {reason}",
                    Disposition.BLOCK,
                )
            )
            continue
        if declared is None:
            continue
        try:
            declared_value = float(declared)
        except (TypeError, ValueError):
            violations.append(
                _violation(
                    CVSS_RULE,
                    f"submitted finding {finding_id} declares a non-numeric CVSS score",
                    Disposition.BLOCK,
                )
            )
            continue
        if abs(declared_value - float(recomputed or 0.0)) > 1e-9:
            violations.append(
                _violation(
                    CVSS_RULE,
                    f"submitted finding {finding_id} declares CVSS {declared_value} "
                    f"but its vector recomputes to {recomputed}",
                    Disposition.BLOCK,
                )
            )
    return violations


def check_vocabulary(submitted: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Severity, cap and bucket tokens must be inside their closed vocabularies.

    An unknown severity is not rejected outright: core.normalize_severity fails
    closed to MEDIUM, so the rule records that the token was unrecognized and
    that the harness read it at no less than MEDIUM.
    """
    severities = {member.value for member in Severity}
    caps_tokens = {member.token for member in Disposition}
    buckets = {member.value for member in core.Bucket}
    violations: list[dict[str, Any]] = []
    for row in submitted:
        finding_id = str(row.get("finding_id", "unnamed"))
        severity = row.get("severity")
        if severity is not None and str(severity) not in severities:
            fallback = core.normalize_severity(severity)
            violations.append(
                _violation(
                    VOCABULARY_RULE,
                    f"submitted finding {finding_id} carries severity {severity} "
                    f"outside the closed vocabulary; read as {fallback.value}",
                    Disposition.HOLD,
                )
            )
        caps_token = row.get("caps")
        if caps_token is not None and str(caps_token) not in caps_tokens:
            violations.append(
                _violation(
                    VOCABULARY_RULE,
                    f"submitted finding {finding_id} carries cap {caps_token} "
                    "outside the closed disposition vocabulary",
                    Disposition.BLOCK,
                )
            )
        bucket = row.get("bucket")
        if bucket is not None and str(bucket) not in buckets:
            violations.append(
                _violation(
                    VOCABULARY_RULE,
                    f"submitted finding {finding_id} carries bucket {bucket} "
                    "outside the closed bucket vocabulary",
                    Disposition.BLOCK,
                )
            )
    return violations


def check_provenance(
    submitted: list[dict[str, Any]], instruments: set[str]
) -> list[dict[str, Any]]:
    """Every submitted finding must name an instrument that actually reported."""
    violations: list[dict[str, Any]] = []
    for row in submitted:
        finding_id = str(row.get("finding_id", "unnamed"))
        instrument = str(row.get("instrument", ""))
        if not instrument:
            violations.append(
                _violation(
                    PROVENANCE_RULE,
                    f"submitted finding {finding_id} names no instrument",
                    Disposition.BLOCK,
                )
            )
            continue
        if instrument in instruments:
            continue
        violations.append(
            _violation(
                PROVENANCE_RULE,
                f"submitted finding {finding_id} attributes itself to {instrument}, "
                "which did not report in the recorded evidence",
                Disposition.BLOCK,
            )
        )
    return violations


def check_scope_integrity(document: dict[str, Any], base: Path) -> list[dict[str, Any]]:
    """The evidence must bind the scope digest a human approved."""
    import recon as recon_mod

    binding = recon_mod.scope_binding(base)
    violations: list[dict[str, Any]] = []
    if not binding.get("scope_present"):
        return [_violation(SCOPE_RULE, "the approved scope file is absent", Disposition.BLOCK)]
    if not binding.get("approved_present"):
        violations.append(
            _violation(SCOPE_RULE, "the scope approval digest is absent", Disposition.BLOCK)
        )
    if binding.get("approved_present") and not binding.get("matches"):
        violations.append(
            _violation(
                SCOPE_RULE,
                f"live scope digest {binding.get('live_digest')} does not match the "
                f"approved digest {binding.get('approved_digest')}",
                Disposition.BLOCK,
            )
        )
    recorded = str(document.get("scope_digest", ""))
    live = str(binding.get("live_digest") or "")
    if recorded and live and recorded != live:
        violations.append(
            _violation(
                SCOPE_RULE,
                f"the evidence document binds scope digest {recorded} but the live "
                f"scope reads {live}, so the evidence was produced under different scope",
                Disposition.BLOCK,
            )
        )
    if not recorded:
        violations.append(
            _violation(
                SCOPE_RULE,
                "the evidence document binds no scope digest",
                Disposition.BLOCK,
            )
        )
    return violations


def check_command_integrity(document: dict[str, Any]) -> list[dict[str, Any]]:
    """No recorded invocation may carry a forbidden argument.

    Phase 1 item 5 forbids the auto rule selection form by name. The check is a
    token match plus an adjacent-window match because a legal pinned invocation
    legitimately contains the flag on its own.
    """
    violations: list[dict[str, Any]] = []
    for result in document.get("instruments", []) or []:
        if not isinstance(result, dict):
            continue
        for artifact in result.get("raw_artifacts", []) or []:
            if not isinstance(artifact, dict):
                continue
            argv = [str(item) for item in (artifact.get("argv") or [])]
            identifier = str(artifact.get("artifact_id", "unnamed"))
            if not argv:
                violations.append(
                    _violation(
                        COMMAND_RULE,
                        f"artifact {identifier} records no argv, so its invocation "
                        "cannot be reproduced",
                        Disposition.HOLD,
                    )
                )
                continue
            for token in FORBIDDEN_ARGV_TOKENS:
                if token in argv:
                    violations.append(
                        _violation(
                            COMMAND_RULE,
                            f"artifact {identifier} carries forbidden argument {token}",
                            Disposition.BLOCK,
                        )
                    )
            for flag, value in FORBIDDEN_ARGV_PAIRS:
                for index, item in enumerate(argv[:-1]):
                    if item == flag and argv[index + 1] == value:
                        violations.append(
                            _violation(
                                COMMAND_RULE,
                                f"artifact {identifier} carries forbidden argument "
                                f"pair {flag} {value}",
                                Disposition.BLOCK,
                            )
                        )
    return violations


def check_config_integrity(document: dict[str, Any], base: Path) -> list[dict[str, Any]]:
    """Recorded scanner config digests must still match the live bytes.

    An unpinned scanner database cited as evidence is a BLOCK. A database that
    is unpinned and whose scanner consequently declined to run is a coverage gap
    the recon layer already carries, so this rule grades drift and citation, not
    mere absence.
    """
    violations: list[dict[str, Any]] = []
    databases = (document.get("recon") or {}).get("scanner_databases") or {}
    if not isinstance(databases, dict):
        return [
            _violation(
                CONFIG_RULE,
                "the evidence document records no scanner database map",
                Disposition.HOLD,
            )
        ]
    for name in sorted(databases):
        entry = databases[name]
        if not isinstance(entry, dict):
            continue
        config_path = str(entry.get("config_path") or "")
        recorded_digest = entry.get("config_digest")
        if not config_path:
            continue
        live_path = base / config_path
        if not live_path.exists():
            violations.append(
                _violation(
                    CONFIG_RULE,
                    f"scanner {name} records config {config_path} which is absent from the tree",
                    Disposition.BLOCK,
                )
            )
            continue
        live_digest = core.sha256_path(live_path)
        if recorded_digest and live_digest != recorded_digest:
            violations.append(
                _violation(
                    CONFIG_RULE,
                    f"scanner {name} config {config_path} digest drifted from "
                    f"{recorded_digest} to {live_digest}",
                    Disposition.BLOCK,
                )
            )
        if entry.get("runs") and str(entry.get("pin_state")) != "pinned":
            violations.append(
                _violation(
                    CONFIG_RULE,
                    f"scanner {name} ran with pin state {entry.get('pin_state')}, "
                    "so an unpinned database would be cited as evidence",
                    Disposition.BLOCK,
                )
            )
    return violations


def check_source_integrity(document: dict[str, Any], base: Path) -> list[dict[str, Any]]:
    """The recorded tree state must be non-null and honestly reported.

    A dirty tree presented as clean is a BLOCK in the disposition vocabulary, so
    this rule re-derives the dirty bit live rather than trusting the record.
    """
    import recon as recon_mod

    recorded = document.get("recon") or {}
    violations: list[dict[str, Any]] = []
    git_sha = recorded.get("git_sha")
    if not git_sha:
        violations.append(
            _violation(
                SOURCE_RULE,
                "the evidence document records no git SHA, which SHIP requires to be non-null",
                Disposition.BLOCK,
            )
        )
    recorded_dirty = recorded.get("dirty_bit")
    live = recon_mod.collect(base)
    if recorded_dirty is False and live.dirty_bit:
        violations.append(
            _violation(
                SOURCE_RULE,
                "the evidence document records a clean tree while the live tree is dirty",
                Disposition.BLOCK,
            )
        )
    if live.dirty_bit:
        violations.append(
            _violation(
                SOURCE_RULE,
                f"the tree is dirty at verification time with {len(live.dirty_entries)} "
                "entries, so no manifest over it can be presented as clean",
                Disposition.HOLD,
            )
        )
    if git_sha and live.git_sha and str(git_sha) != live.git_sha:
        violations.append(
            _violation(
                SOURCE_RULE,
                f"the evidence binds git SHA {git_sha} but the tree now reads {live.git_sha}",
                Disposition.HOLD,
            )
        )
    return violations


def check_external_signature(document: dict[str, Any], base: Path) -> list[dict[str, Any]]:
    """SHIP requires a detached signature over the manifest from an external root.

    The absence of such a signature never blocks by itself, because an absent
    control is a coverage gap rather than a demonstrated defect, but it does
    cap: the disposition vocabulary makes the detached external signature a SHIP
    precondition with no waiver.
    """
    audit = base / core.AUDIT_DIRNAME
    candidates = [
        audit / "evidence.yaml.dsse.json",
        audit / f"{core.SCOPE_APPROVED_FILENAME}.dsse.json",
    ]
    present = [path for path in candidates if path.exists()]
    if not present:
        return [
            _violation(
                SIGNATURE_RULE,
                "no detached signature over the manifest from an external trust root "
                "is present, so SHIP is unreachable",
                Disposition.HOLD,
            )
        ]
    return []


def check_all_clear(
    submitted: list[dict[str, Any]],
    document: dict[str, Any],
    submitted_document: dict[str, Any],
) -> list[dict[str, Any]]:
    """An all-clear submission over non-empty evidence is a negative control."""
    recorded_findings = document.get("findings") or []
    recorded_gaps = document.get("coverage_gaps") or []
    if submitted or not (recorded_findings or recorded_gaps):
        return []
    claimed = str(submitted_document.get("disposition", "")) or "unstated"
    return [
        _violation(
            ALL_CLEAR_RULE,
            f"the submitted findings document is empty and claims {claimed} while the "
            f"evidence records {len(recorded_findings)} findings and "
            f"{len(recorded_gaps)} coverage gaps",
            Disposition.BLOCK,
        )
    ]


def check_disposition_cap(
    document: dict[str, Any], submitted_document: dict[str, Any]
) -> list[dict[str, Any]]:
    """A submitted disposition may never exceed what the evidence supports."""
    tokens = {member.token: member for member in Disposition}
    recorded = tokens.get(str(document.get("disposition", "")))
    claimed = tokens.get(str(submitted_document.get("disposition", "")))
    if recorded is None:
        return [
            _violation(
                CAP_RULE,
                "the evidence document records no disposition",
                Disposition.BLOCK,
            )
        ]
    if claimed is None:
        return []
    if claimed > recorded:
        return [
            _violation(
                CAP_RULE,
                f"the submitted findings claim {claimed.token} while the recorded "
                f"evidence caps at {recorded.token}",
                Disposition.BLOCK,
            )
        ]
    return []


def _submitted_findings(submitted_document: dict[str, Any]) -> list[dict[str, Any]]:
    rows = submitted_document.get("findings")
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    return []


def verify_findings(
    findings_path: Path, context_path: Path, base: Path | None = None
) -> dict[str, Any]:
    """Reconcile a submitted findings document against recorded evidence.

    This is the signature crucible.py's verify command calls. The returned
    mapping carries every violation as a rule and statement pair plus the
    resulting disposition, which is the minimum of the evidence document's own
    disposition and every violation cap. Exit 0 is reachable only when the
    disposition is SHIP and no violation stands.
    """
    root = base or core.project_root()
    violations: list[dict[str, Any]] = []

    document, context_reason = _load_yaml(Path(context_path))
    if context_reason:
        return {
            "violations": [
                _violation(
                    RECALL_RULE,
                    f"the evidence context at {context_path} is {context_reason}",
                    Disposition.BLOCK,
                )
            ],
            "disposition": Disposition.BLOCK,
            "rules_run": [],
        }

    submitted_document, findings_reason = _load_yaml(Path(findings_path))
    if findings_reason:
        violations.append(
            _violation(
                RECALL_RULE,
                f"the submitted findings at {findings_path} are {findings_reason}",
                Disposition.BLOCK,
            )
        )

    submitted = _submitted_findings(submitted_document)
    recorded = _evidence_findings(document)
    subjects = _evidence_subjects(document)
    instruments = _evidence_instruments(document)
    blocked = _blocked_artifacts(document)

    violations.extend(check_recall(submitted, recorded))
    violations.extend(check_spans(submitted, subjects))
    violations.extend(check_completed_run_evidence(submitted, blocked))
    violations.extend(check_cvss(submitted))
    violations.extend(check_vocabulary(submitted))
    violations.extend(check_provenance(submitted, instruments))
    violations.extend(check_scope_integrity(document, root))
    violations.extend(check_command_integrity(document))
    violations.extend(check_config_integrity(document, root))
    violations.extend(check_source_integrity(document, root))
    violations.extend(check_external_signature(document, root))
    violations.extend(check_all_clear(submitted, document, submitted_document))
    violations.extend(check_disposition_cap(document, submitted_document))

    tokens = {member.token: member for member in Disposition}
    recorded_disposition = tokens.get(str(document.get("disposition", "")), Disposition.BLOCK)
    caps = [recorded_disposition]
    caps.extend(tokens.get(str(row.get("caps", "")), Disposition.BLOCK) for row in violations)

    return {
        "violations": violations,
        "disposition": core.cap_all(caps),
        "rules_run": list(RULES),
        "recorded_disposition": recorded_disposition.token,
        "submitted_finding_count": len(submitted),
        "recorded_finding_count": len(recorded),
        "evidence_schema": str(document.get("schema", "")) or evidence_mod.EVIDENCE_SCHEMA,
    }


__all__ = [
    "ALL_CLEAR_RULE",
    "CAP_RULE",
    "COMMAND_RULE",
    "COMPLETED_RUN_RULE",
    "CONFIG_RULE",
    "CVSS_RULE",
    "FORBIDDEN_ARGV_PAIRS",
    "FORBIDDEN_ARGV_TOKENS",
    "PROVENANCE_RULE",
    "RECALL_RULE",
    "RULES",
    "SCOPE_RULE",
    "SIGNATURE_RULE",
    "SOURCE_RULE",
    "SPAN_RULE",
    "VOCABULARY_RULE",
    "check_all_clear",
    "check_command_integrity",
    "check_completed_run_evidence",
    "check_config_integrity",
    "check_cvss",
    "check_disposition_cap",
    "check_external_signature",
    "check_provenance",
    "check_recall",
    "check_scope_integrity",
    "check_source_integrity",
    "check_spans",
    "check_vocabulary",
    "cvss_base_score",
    "parse_cvss_vector",
    "roundup",
    "verify_findings",
]
