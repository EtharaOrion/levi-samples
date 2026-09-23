"""Upstream-provenance family, discharging CRUCIBLE contract step 8c.

Step 8c requires reconciling the upstream-provenance record each resident bundle
carries. This module is the one instrument that does it, G-PROV-UPSTREAM, and it
reconciles across both carriers rather than trusting either alone: the structured
record in solution/provenance.yaml and the span record in the task.toml
[span_provenance] table. Reading only one carrier would let the other contradict
it silently, which is exactly the failure this step exists to catch.

The checks are the ones the contract names. Exactly one upstream provenance
record must be expressed, so two carriers asserting upstream changes of different
scope count as more than one record and not as corroboration. A per-instance
train-cutoff date must parse. A record declaring origin derived must name a
non-empty upstream identity, a license, and a modification list. No declared
origin may contradict the asset license chain or the prose in instruction.md.

An unresolved license on a derived record is a defect of the delivered asset and
not a limit on what this harness could measure, so it is emitted as a retained
domain-integrity finding rather than as a coverage gap. The distinction is
load-bearing: a gap says the audit could not look, and here the audit looked and
found the field reading unresolved in committed bytes.
"""

from __future__ import annotations

import datetime
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
    Severity,
    Standing,
)
from registry import REGISTRY, Category, EvidenceClass, Instrument

PROVENANCE_INSTRUMENT = "G-PROV-UPSTREAM"

PROVENANCE_CARRIER = "solution/provenance.yaml"
MANIFEST_CARRIER = "task.toml"
INSTRUCTION_CARRIER = "instruction.md"
LICENSE_CARRIER = "LICENSE"

SOURCE_BLOCK = "source"
SPAN_BLOCK = "span_provenance"

DERIVED_ORIGIN = "derived"

MODIFICATION_KEYS = ("modifications", "modification_list", "modifications_applied", "changes")

UNRESOLVED_TOKENS = frozenset(
    {"", "unresolved", "unknown", "none", "null", "unsupplied", "undetermined", "tbd"}
)

SPAN_SHA_PREFIX = "span:"

KNOWN_LICENSE_TOKENS = ("mit", "apache-2.0", "apache 2.0", "bsd-3-clause", "bsd-2-clause", "gpl")

PROVENANCE_CRITICAL_CLASS = "domain-integrity-upstream-provenance"

FREEZE_TABLE_GAP_ID = "D-PROV-FREEZE-TABLE-UNRESOLVED"
CARRIER_UNPARSEABLE_GAP_ID = "D-PROV-CARRIER-UNPARSEABLE"
INTERNAL_ERROR_GAP_ID = "D-PROV-INTERNAL-ERROR"
NO_BUNDLE_GAP_ID = "D-PROV-NO-RESIDENT-BUNDLE"

PROVENANCE_SURFACE = "upstream_provenance_record"


def _register_declaration() -> None:
    """Register G-PROV-UPSTREAM with the twelve required declaration fields.

    Registration is idempotent so that a second import of this family module
    cannot raise and thereby convert a re-import into a broken instrument.
    """
    if PROVENANCE_INSTRUMENT in REGISTRY:
        return
    REGISTRY.register(
        Instrument(
            name=PROVENANCE_INSTRUMENT,
            category=Category.PROVENANCE,
            binary="python",
            ecosystems=("*",),
            timeout_seconds=300.0,
            required_conditions=(
                "provenance-carrier-readable",
                "task-manifest-readable",
                "instruction-prose-readable",
            ),
            critical_capability="upstream-record-reconciliation-across-both-carriers",
            evidence_class=EvidenceClass.SCHEMA_VALIDATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.BLOCK,
            bucket=Bucket.D,
            database_pin="",
            notes="Reconciles solution/provenance.yaml against task.toml [span_provenance].",
        )
    )


_register_declaration()


def _ascii_text(raw: str) -> str:
    """Force a statement into the ASCII the emitted YAML is restricted to."""
    return raw.encode("ascii", "backslashreplace").decode("ascii")


def _token(value: Any) -> str:
    """Reduce a declared scalar to a comparable lowercase token."""
    if value is None:
        return ""
    return " ".join(str(value).split()).strip().lower()


def is_unresolved(value: Any) -> bool:
    """Report whether a declared field carries no usable value.

    A field reading one of the unresolved tokens is treated exactly as a field
    left empty, because a producer writing the word unresolved has declared the
    same absence a blank would have declared.
    """
    return _token(value) in UNRESOLVED_TOKENS


def load_provenance(bundle: Path) -> tuple[dict[str, Any], str]:
    """Parse solution/provenance.yaml, returning the document and any parse error."""
    path = bundle / PROVENANCE_CARRIER
    if not path.is_file():
        return {}, f"{PROVENANCE_CARRIER} is absent"
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return {}, f"{PROVENANCE_CARRIER} did not parse: {error}"
    if not isinstance(document, dict):
        return {}, f"{PROVENANCE_CARRIER} did not parse as a mapping"
    return document, ""


def load_manifest(bundle: Path) -> tuple[dict[str, Any], str]:
    """Parse task.toml, returning the document and any parse error."""
    path = bundle / MANIFEST_CARRIER
    if not path.is_file():
        return {}, f"{MANIFEST_CARRIER} is absent"
    try:
        with path.open("rb") as handle:
            document = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as error:
        return {}, f"{MANIFEST_CARRIER} did not parse: {error}"
    return document, ""


def parse_cutoff(value: Any) -> datetime.datetime | None:
    """Parse a declared per-instance train-cutoff date, or return None.

    Returns None rather than raising so that an unparseable date becomes a
    finding with the offending value recorded, not an aborted family.
    """
    if not isinstance(value, datetime.datetime):
        if isinstance(value, datetime.date):
            return datetime.datetime.combine(value, datetime.time.min, tzinfo=datetime.UTC)
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            return datetime.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    return value


def modification_list(source: dict[str, Any], document: dict[str, Any]) -> list[Any]:
    """Return the declared modification list from either the source block or the root."""
    for container in (source, document):
        for key in MODIFICATION_KEYS:
            candidate = container.get(key)
            if isinstance(candidate, list) and candidate:
                return candidate
            if isinstance(candidate, str) and not is_unresolved(candidate):
                return [candidate]
    return []


def _finding(
    subject: str,
    suffix: str,
    severity: Severity,
    statement: str,
    evidence: dict[str, Any],
) -> Finding:
    return Finding(
        finding_id=f"{PROVENANCE_INSTRUMENT}-{subject}-{suffix}",
        instrument=PROVENANCE_INSTRUMENT,
        critical_class=PROVENANCE_CRITICAL_CLASS,
        severity=severity,
        caps=Disposition.HOLD,
        bucket=Bucket.D,
        subject=subject,
        statement=_ascii_text(statement),
        evidence=evidence,
    )


def _license_chain(base: Path) -> dict[str, str]:
    """Record the license the containing repository redistributes these assets under."""
    path = base / LICENSE_CARRIER
    if not path.is_file():
        return {"present": "false", "headline": ""}
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {"present": "true", "headline": lines[0] if lines else ""}


def _check_record_multiplicity(
    subject: str, source: dict[str, Any], span: dict[str, Any], document: dict[str, Any]
) -> list[Finding]:
    """Verify that the two carriers express exactly one upstream provenance record.

    The structured carrier names an upstream change by sha and the manifest names
    it by span label and pull-request count. Where the manifest declares a span of
    more than one pull request, the structured carrier must name a span-shaped
    upstream change; where it instead names a single commit that is also the base
    commit, the two carriers describe upstream changes of different scope and the
    bundle expresses two records rather than one.
    """
    findings: list[Finding] = []
    upstream_sha = str(source.get("upstream_change_sha") or "")
    base_sha = str(source.get("base_commit_sha") or "")
    pr_count = span.get("pr_count")
    span_label = str(span.get("span_label") or "")
    instance_identity = str(span.get("instance_identity") or "")
    declares_span = upstream_sha.startswith(SPAN_SHA_PREFIX) or SPAN_SHA_PREFIX in str(
        document.get("instance_id") or ""
    )
    multi = isinstance(pr_count, int) and pr_count > 1

    if multi and not declares_span:
        findings.append(
            _finding(
                subject,
                "UPSTREAM-IDENTITY-DIVERGENT",
                Severity.HIGH,
                f"Bundle {subject} expresses two upstream provenance records of different scope "
                f"where exactly one is required. {MANIFEST_CARRIER} declares span {span_label!r} "
                f"over {pr_count} pull requests as instance identity {instance_identity!r}, while "
                f"{PROVENANCE_CARRIER} names a single upstream_change_sha {upstream_sha!r}"
                + (
                    " that is byte-identical to base_commit_sha, so that carrier locates no "
                    "distinct upstream change at all."
                    if upstream_sha and upstream_sha == base_sha
                    else "."
                ),
                {
                    "bundle": subject,
                    "manifest_span_label": span_label,
                    "manifest_pr_count": pr_count,
                    "manifest_instance_identity": instance_identity,
                    "provenance_upstream_change_sha": upstream_sha,
                    "provenance_base_commit_sha": base_sha,
                    "upstream_equals_base": bool(upstream_sha and upstream_sha == base_sha),
                },
            )
        )
    return findings


def _check_origin_consistency(
    subject: str, source: dict[str, Any], instruction: str, chain: dict[str, str]
) -> list[Finding]:
    """Verify the declared origin against the instruction prose and the license chain."""
    findings: list[Finding] = []
    repository = str(source.get("repository") or "")
    tail = repository.rsplit("/", 1)[-1].lower() if repository else ""
    folded = core.normalize_text(instruction)
    if tail and tail not in folded:
        findings.append(
            _finding(
                subject,
                "ORIGIN-PROSE-CONTRADICTION",
                Severity.HIGH,
                f"Bundle {subject} declares origin {source.get('origin')!r} from repository "
                f"{repository!r}, but the agent-visible prose in {INSTRUCTION_CARRIER} never names "
                f"{tail!r}, so the declared origin is not corroborated by the surface the agent "
                "actually reads.",
                {
                    "bundle": subject,
                    "declared_repository": repository,
                    "instruction_names_repository": False,
                    "license_chain": chain,
                },
            )
        )
    return findings


def _check_derived_record(
    subject: str,
    source: dict[str, Any],
    document: dict[str, Any],
    chain: dict[str, str],
) -> list[Finding]:
    """Verify the three fields a record declaring origin derived is required to name."""
    findings: list[Finding] = []
    repository = str(source.get("repository") or "")
    base_sha = str(source.get("base_commit_sha") or "")

    if is_unresolved(repository) or is_unresolved(base_sha):
        findings.append(
            _finding(
                subject,
                "UPSTREAM-IDENTITY-ABSENT",
                Severity.HIGH,
                f"Bundle {subject} declares origin derived but names no non-empty upstream "
                f"identity: repository {repository!r}, base_commit_sha {base_sha!r}.",
                {"bundle": subject, "repository": repository, "base_commit_sha": base_sha},
            )
        )

    declared_license = source.get("license")
    if is_unresolved(declared_license):
        headline = chain.get("headline") or "no recorded license"
        findings.append(
            _finding(
                subject,
                "LICENSE-UNRESOLVED",
                Severity.HIGH,
                f"Bundle {subject} declares origin derived from the public repository "
                f"{repository!r} with license {declared_license!r}, so the upstream terms the "
                "derived asset is redistributed under are not established by committed bytes. The "
                f"containing repository redistributes under {headline}, which cannot stand in for "
                "an upstream grant that the record itself leaves unresolved. This is a property "
                "of the delivered asset and not a limit on what this instrument could measure.",
                {
                    "bundle": subject,
                    "declared_license": str(declared_license),
                    "declared_origin": str(source.get("origin") or ""),
                    "repository": repository,
                    "repository_license_chain": chain,
                },
            )
        )

    modifications = modification_list(source, document)
    if not modifications:
        findings.append(
            _finding(
                subject,
                "MODIFICATION-LIST-ABSENT",
                Severity.MEDIUM,
                f"Bundle {subject} declares origin derived but carries no modification list under "
                f"any of {', '.join(MODIFICATION_KEYS)} in {PROVENANCE_CARRIER}, so what was "
                "changed relative to the named upstream is not recoverable from the record.",
                {
                    "bundle": subject,
                    "searched_keys": list(MODIFICATION_KEYS),
                    "source_keys": sorted(str(key) for key in source),
                    "document_keys": sorted(str(key) for key in document),
                },
            )
        )
    return findings


def _freeze_table_gap(subject: str, roots: dict[str, Any], cutoff: str) -> CoverageGap:
    """Record that a parseable cutoff date exists without a pinned table to anchor it."""
    table = roots.get("freeze_date_table") if isinstance(roots, dict) else {}
    state = str(table.get("state") if isinstance(table, dict) else "") or "unrecorded"
    return CoverageGap(
        gap_id=FREEZE_TABLE_GAP_ID,
        instrument=PROVENANCE_INSTRUMENT,
        surface=PROVENANCE_SURFACE,
        subject=subject,
        reason="freeze-date-table-root-unresolved",
        caps=Disposition.HOLD,
        statement=_ascii_text(
            f"Bundle {subject} carries a parseable per-instance cutoff date {cutoff}, but the "
            f"freeze date table it would be compared against is recorded state {state!r} with an "
            "unresolved identity and digest, so whether that date falls inside or outside a "
            "training freeze is undecidable from committed bytes. The date check passed; the "
            "comparison the date exists for did not run."
        ),
    )


def _reconcile_bundle(
    bundle: Path, base: Path, chain: dict[str, str]
) -> tuple[list[Finding], list[CoverageGap], dict[str, Any]]:
    """Reconcile one bundle's upstream provenance across both carriers."""
    subject = bundle.name
    findings: list[Finding] = []
    gaps: list[CoverageGap] = []

    document, provenance_error = load_provenance(bundle)
    manifest, manifest_error = load_manifest(bundle)
    row: dict[str, Any] = {"bundle": subject, "lane": core.lane_of(bundle, base)}

    for error in (provenance_error, manifest_error):
        if error:
            gaps.append(
                CoverageGap(
                    gap_id=CARRIER_UNPARSEABLE_GAP_ID,
                    instrument=PROVENANCE_INSTRUMENT,
                    surface=PROVENANCE_SURFACE,
                    subject=subject,
                    reason="provenance-carrier-unreadable",
                    caps=Disposition.HOLD,
                    statement=_ascii_text(
                        f"Bundle {subject} could not be reconciled because {error}, so the checks "
                        "that carrier supports produced no determination."
                    ),
                )
            )

    source = document.get(SOURCE_BLOCK) if isinstance(document.get(SOURCE_BLOCK), dict) else {}
    span = manifest.get(SPAN_BLOCK) if isinstance(manifest.get(SPAN_BLOCK), dict) else {}
    row["carriers"] = {
        "provenance_source_block": bool(source),
        "manifest_span_provenance_block": bool(span),
    }

    if not source or not span:
        missing = []
        if not source:
            missing.append(f"{PROVENANCE_CARRIER} [{SOURCE_BLOCK}]")
        if not span:
            missing.append(f"{MANIFEST_CARRIER} [{SPAN_BLOCK}]")
        findings.append(
            _finding(
                subject,
                "RECORD-CARRIER-ABSENT",
                Severity.HIGH,
                f"Bundle {subject} does not express one complete upstream provenance record: "
                f"{', '.join(missing)} is absent, so the record cannot be reconciled across both "
                "carriers.",
                {"bundle": subject, "missing_carriers": missing},
            )
        )
        row["reconciled"] = False
        return findings, gaps, row

    origin = _token(source.get("origin"))
    row["declared_origin"] = origin
    row["declared_license"] = str(source.get("license") or "")
    row["repository"] = str(source.get("repository") or "")
    row["upstream_change_sha"] = str(source.get("upstream_change_sha") or "")
    row["base_commit_sha"] = str(source.get("base_commit_sha") or "")
    row["manifest_pr_count"] = span.get("pr_count")
    row["manifest_span_label"] = str(span.get("span_label") or "")

    raw_cutoff = source.get("upstream_change_committed_at")
    cutoff = parse_cutoff(raw_cutoff)
    row["upstream_change_committed_at"] = str(raw_cutoff or "")
    row["cutoff_parsed"] = cutoff.isoformat() if cutoff else None
    if cutoff is None:
        findings.append(
            _finding(
                subject,
                "CUTOFF-UNPARSEABLE",
                Severity.HIGH,
                f"Bundle {subject} carries no parseable per-instance train-cutoff date: "
                f"upstream_change_committed_at reads {raw_cutoff!r}.",
                {"bundle": subject, "declared": str(raw_cutoff or "")},
            )
        )
    else:
        roots = document.get("screening_roots")
        table = roots.get("freeze_date_table") if isinstance(roots, dict) else None
        table_state = _token(table.get("state")) if isinstance(table, dict) else ""
        row["freeze_date_table_state"] = table_state or "unrecorded"
        if table_state not in {"resolved", "supplied", "pinned"}:
            gaps.append(
                _freeze_table_gap(
                    subject, roots if isinstance(roots, dict) else {}, cutoff.isoformat()
                )
            )

    findings.extend(_check_record_multiplicity(subject, source, span, document))

    if origin == DERIVED_ORIGIN:
        findings.extend(_check_derived_record(subject, source, document, chain))
    else:
        findings.append(
            _finding(
                subject,
                "ORIGIN-NOT-DERIVED",
                Severity.MEDIUM,
                f"Bundle {subject} declares origin {origin!r} rather than {DERIVED_ORIGIN!r} while "
                f"naming public repository {row['repository']!r} as its source, so the derived "
                "record obligations were not evaluated against a record that claims them.",
                {"bundle": subject, "declared_origin": origin, "repository": row["repository"]},
            )
        )

    instruction_path = bundle / INSTRUCTION_CARRIER
    if instruction_path.is_file():
        instruction = instruction_path.read_text(encoding="utf-8", errors="replace")
        findings.extend(_check_origin_consistency(subject, source, instruction, chain))
        row["instruction_present"] = True
    else:
        row["instruction_present"] = False
        gaps.append(
            CoverageGap(
                gap_id=CARRIER_UNPARSEABLE_GAP_ID,
                instrument=PROVENANCE_INSTRUMENT,
                surface=PROVENANCE_SURFACE,
                subject=subject,
                reason="instruction-prose-absent",
                caps=Disposition.HOLD,
                statement=_ascii_text(
                    f"Bundle {subject} carries no {INSTRUCTION_CARRIER}, so the declared origin "
                    "could not be checked against the prose the agent reads."
                ),
            )
        )

    row["reconciled"] = True
    row["attestation_state"] = str(source.get("attestation_state") or "unrecorded")
    return findings, gaps, row


def _internal_error_result(error: Exception) -> InstrumentResult:
    return InstrumentResult(
        instrument=PROVENANCE_INSTRUMENT,
        ran=False,
        gaps=[
            CoverageGap(
                gap_id=INTERNAL_ERROR_GAP_ID,
                instrument=PROVENANCE_INSTRUMENT,
                surface=PROVENANCE_SURFACE,
                reason="instrument-raised-internally",
                caps=Disposition.HOLD,
                statement=_ascii_text(
                    f"{PROVENANCE_INSTRUMENT} raised {type(error).__name__} before producing a "
                    f"determination, so it covered nothing: {error}"
                ),
            )
        ],
        standing=Standing.INSUFFICIENT_EVIDENCE,
    )


def _no_bundle_result() -> InstrumentResult:
    return InstrumentResult(
        instrument=PROVENANCE_INSTRUMENT,
        ran=False,
        gaps=[
            CoverageGap(
                gap_id=NO_BUNDLE_GAP_ID,
                instrument=PROVENANCE_INSTRUMENT,
                surface=PROVENANCE_SURFACE,
                reason="no-resident-bundle-resolved",
                caps=Disposition.HOLD,
                statement=_ascii_text(
                    f"{PROVENANCE_INSTRUMENT} resolved no resident bundle carrying a task "
                    "manifest, so upstream provenance had no substrate and its silence is a gap, "
                    "not a clean result."
                ),
            )
        ],
        standing=Standing.INSUFFICIENT_EVIDENCE,
    )


def run_family(base: Path, reconnaissance: recon.Recon) -> list[InstrumentResult]:
    """Run the step 8c upstream-provenance reconciliation over every resident bundle.

    Returns exactly one InstrumentResult. Nothing here raises: an unreadable
    carrier and an internal failure each become a coverage gap, because an
    instrument that returns silently would read downstream as a pass.
    """
    del reconnaissance
    try:
        bundles = core.bundle_roots(base)
    except OSError as error:
        return [_internal_error_result(error)]
    if not bundles:
        return [_no_bundle_result()]

    findings: list[Finding] = []
    gaps: list[CoverageGap] = []
    rows: list[dict[str, Any]] = []
    try:
        chain = _license_chain(base)
        for bundle in bundles:
            bundle_findings, bundle_gaps, row = _reconcile_bundle(bundle, base, chain)
            findings.extend(bundle_findings)
            gaps.extend(bundle_gaps)
            rows.append(row)
    except Exception as error:
        return [_internal_error_result(error)]

    if findings:
        standing = Standing.OBSERVED_VIOLATION
    elif gaps:
        standing = Standing.INSUFFICIENT_EVIDENCE
    else:
        standing = Standing.DEMONSTRATED_COVERAGE
    return [
        InstrumentResult(
            instrument=PROVENANCE_INSTRUMENT,
            ran=True,
            findings=findings,
            gaps=gaps,
            standing=standing,
            notes={
                "bundles": rows,
                "carriers": [PROVENANCE_CARRIER, MANIFEST_CARRIER, INSTRUCTION_CARRIER],
                "repository_license_chain": chain,
                "modification_keys_searched": list(MODIFICATION_KEYS),
            },
        )
    ]


__all__ = [
    "PROVENANCE_INSTRUMENT",
    "is_unresolved",
    "load_manifest",
    "load_provenance",
    "modification_list",
    "parse_cutoff",
    "run_family",
]
