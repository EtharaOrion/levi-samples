"""Unit tests over the harness invariants the contract makes load-bearing.

These are not a restatement of the instruments. Each test pins one invariant the
rest of the harness relies on and that would fail silently if it drifted: the
disposition lattice never rises, a coverage gap can never cap at SHIP, an
unknown severity fails closed, a registered instrument is always Bucket D, the
ledger vocabularies stay closed, and a finding fingerprint survives formatting
drift while still distinguishing a different anchor.
"""

from __future__ import annotations

import pytest

import core
import evidence
import normalize
import registry
from core import Bucket, Disposition, Outcome, Severity


def test_cap_never_rises():
    assert core.cap(Disposition.SHIP, Disposition.HOLD) is Disposition.HOLD
    assert core.cap(Disposition.HOLD, Disposition.BLOCK) is Disposition.BLOCK
    assert core.cap_all([]) is Disposition.SHIP


def test_coverage_gap_cannot_cap_at_ship():
    with pytest.raises(ValueError):
        core.CoverageGap(
            gap_id="D-FIXTURE",
            instrument="FIXTURE",
            surface="project",
            reason="fixture",
            caps=Disposition.SHIP,
            statement="a gap that caps at ship would be no gap at all",
        )


@pytest.mark.parametrize("raw", ["not-a-severity", "", None, 7])
def test_unknown_severity_fails_closed_to_medium(raw):
    assert core.normalize_severity(raw) is Severity.MEDIUM


def test_known_severity_is_preserved():
    assert core.normalize_severity("low") is Severity.LOW
    assert core.normalize_severity("CRITICAL") is Severity.CRITICAL


def test_instrument_result_without_run_or_gap_is_blocked():
    result = core.InstrumentResult(instrument="FIXTURE", ran=False)
    assert result.disposition is Disposition.BLOCK


def test_registered_instrument_must_be_bucket_d():
    with pytest.raises(ValueError):
        registry.Instrument(
            name="FIXTURE",
            category=registry.Category.SCANNER,
            binary="fixture",
            ecosystems=("*",),
            timeout_seconds=1,
            required_conditions=(),
            critical_capability="fixture",
            evidence_class=registry.EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
            bucket=Bucket.N,
        )


def test_absence_can_never_cap_at_ship():
    with pytest.raises(ValueError):
        registry.Instrument(
            name="FIXTURE",
            category=registry.Category.SCANNER,
            binary="fixture",
            ecosystems=("*",),
            timeout_seconds=1,
            required_conditions=(),
            critical_capability="fixture",
            evidence_class=registry.EvidenceClass.SET_RELATION,
            requires_parser=False,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.SHIP,
        )


def test_parsed_instrument_must_retain_raw_bytes():
    with pytest.raises(ValueError):
        registry.Instrument(
            name="FIXTURE",
            category=registry.Category.SCANNER,
            binary="fixture",
            ecosystems=("*",),
            timeout_seconds=1,
            required_conditions=(),
            critical_capability="fixture",
            evidence_class=registry.EvidenceClass.RAW_TOOL_OUTPUT,
            requires_parser=True,
            requires_raw_artifact=False,
            disposition_cap_on_absence=Disposition.HOLD,
        )


def test_ledger_vocabularies_are_closed():
    assert len(evidence.REWARD_THREATS) == 29
    assert len(evidence.CAPABILITY_CHANNELS) == 9
    assert len(evidence.REWARD_BOUNDARIES) == 8
    with pytest.raises(ValueError):
        evidence.LedgerRow(
            threat="not-a-threat",
            channel="read",
            boundary="input",
            resolution="gap",
        )


def test_not_applicable_requires_a_crucible_derivation():
    with pytest.raises(ValueError):
        evidence.LedgerRow(
            threat="replay-or-duplication",
            channel="read",
            boundary="input",
            resolution="not_applicable",
        )


def test_detected_requires_a_named_atom():
    with pytest.raises(ValueError):
        evidence.LedgerRow(
            threat="replay-or-duplication",
            channel="read",
            boundary="input",
            resolution="detected",
        )


def test_fingerprint_survives_formatting_drift():
    original = normalize.NormalizedIssue(
        rule="fixture-rule",
        anchor=normalize.Anchor(path="src/app.py", symbol="handler", excerpt="12: return x"),
        severity=Severity.HIGH,
        message="fixture",
        tool="fixture-tool",
    )
    drifted = normalize.NormalizedIssue(
        rule="fixture-rule",
        anchor=normalize.Anchor(path="src/app.py", symbol="handler", excerpt="312:\treturn x  "),
        severity=Severity.HIGH,
        message="fixture",
        tool="fixture-tool",
    )
    assert original.fingerprint == drifted.fingerprint


def test_fingerprint_distinguishes_a_different_anchor():
    left = normalize.NormalizedIssue(
        rule="fixture-rule",
        anchor=normalize.Anchor(path="src/app.py", symbol="handler", excerpt="return x"),
        severity=Severity.HIGH,
        message="fixture",
        tool="fixture-tool",
    )
    right = normalize.NormalizedIssue(
        rule="fixture-rule",
        anchor=normalize.Anchor(path="src/other.py", symbol="handler", excerpt="return x"),
        severity=Severity.HIGH,
        message="fixture",
        tool="fixture-tool",
    )
    assert left.fingerprint != right.fingerprint


def test_selfcheck_row_proving_only_the_clean_half_is_inert():
    row = core.SelfcheckRow(
        check_id="SC-FIXTURE",
        instrument="fixture",
        argv=["fixture"],
        exit_code=0,
        elapsed_seconds=0.0,
        clean_half=Outcome.CLEAN,
        positive_half=Outcome.CLEAN,
        required=True,
    )
    assert row.outcome is Outcome.INERT
    assert row.caps is Disposition.BLOCK
