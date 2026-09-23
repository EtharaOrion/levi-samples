"""Single command line entry point for the CRUCIBLE audit harness.

Phase 1 item 11 of trinity/CRUCIBLE.md requires exactly one Typer application
carrying provision, run, selfcheck, verify, and all. This module is that
application. The rationale lives here rather than in the contract because the
contract is prompt-only and the house rules place runbooks and descriptions
inside the .audit/ harness.

Command semantics fixed by the contract:

provision
    Resolves scanner binaries and pinned databases without grading anything.
    A provisioning failure is recorded as a coverage gap, never as a pass.

run
    Executes every registered instrument and writes .audit/evidence.yaml, the
    sole evidence source a downstream reviewer or model may cite.

selfcheck
    Runs every deterministic self verification check and writes
    .audit/selfcheck.yaml with one row per check carrying argv, exit code,
    elapsed seconds, and the both halves outcome. A required row reading inert
    or unrun caps the gate at BLOCK under verifier principle 7.

verify
    The only command whose success means the gate passed. Exit 0 means the
    submitted findings reconcile against the recorded evidence with no cap.

all
    provision, run, selfcheck, verify in that order, stopping at the first
    command that caps the gate below SHIP.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer

import core
import evidence as evidence_mod
import recon as recon_mod
from core import Disposition

app = typer.Typer(
    name="crucible",
    help="CRUCIBLE deterministic audit harness.",
    no_args_is_help=True,
    add_completion=False,
)

EXIT_SHIP = 0
EXIT_HOLD = 2
EXIT_BLOCK = 3

_EXIT_FOR_DISPOSITION = {
    Disposition.SHIP: EXIT_SHIP,
    Disposition.HOLD: EXIT_HOLD,
    Disposition.BLOCK: EXIT_BLOCK,
}


def exit_code_for(disposition: Disposition) -> int:
    """Map a disposition onto the process exit code the gate reads.

    The mapping matches trinity/tools/gate.py so an orchestrating run reads one
    vocabulary across both tools.
    """
    return _EXIT_FOR_DISPOSITION[disposition]


def verify_scope_binding(root: Path | None = None) -> dict:
    """Recompute the live scope digest and compare it to the approved digest.

    Phase 1 item 1 requires this before any harness file acts, and Phase 2 item
    2 requires the refusal itself to appear as a selfcheck row. Returning the
    comparison as data lets both callers share one implementation.
    """
    return recon_mod.scope_binding(root)


def _refuse_on_scope_mismatch(binding: dict) -> None:
    if not binding.get("scope_present"):
        typer.echo("SCOPE_MISSING: .audit/scope.yaml is absent", err=True)
        raise typer.Exit(EXIT_BLOCK)
    if not binding.get("approved_present"):
        typer.echo("APPROVAL_DIGEST_MISSING: .audit/scope.approved is absent", err=True)
        raise typer.Exit(EXIT_BLOCK)
    if not binding.get("matches"):
        typer.echo(
            "APPROVAL_DIGEST_MISMATCH: live "
            f"{binding.get('live_digest')} approved {binding.get('approved_digest')}",
            err=True,
        )
        raise typer.Exit(EXIT_BLOCK)


def _new_document(
    run_id: str, principal: str, recon: recon_mod.Recon
) -> evidence_mod.EvidenceDocument:
    return evidence_mod.EvidenceDocument(
        run_id=run_id,
        principal=principal,
        scope_digest=recon.scope.get("live_digest") or "",
        recon=recon.to_row(),
    )


@app.command()
def provision(
    root: Path = typer.Option(None, help="Project root. Defaults to the parent of .audit."),
) -> None:
    """Resolve scanner binaries and pinned databases without grading anything.

    Provisioning never raises a disposition. It reports what is present so the
    run command can record an absent required tool as a coverage gap rather
    than silently skipping it.
    """
    base = root or core.project_root()
    binding = verify_scope_binding(base)
    _refuse_on_scope_mismatch(binding)

    binaries = recon_mod.collect_binaries()
    databases = recon_mod.collect_scanner_databases(base)

    missing = sorted(name for name, row in binaries.items() if not row["present"])
    unpinned = sorted(name for name, row in databases.items() if row["pin_state"] != "pinned")

    typer.echo(f"binaries present: {len(binaries) - len(missing)} of {len(binaries)}")
    if missing:
        typer.echo("absent binaries: " + ", ".join(missing))
    typer.echo(f"scanner databases pinned: {len(databases) - len(unpinned)} of {len(databases)}")
    if unpinned:
        typer.echo("unpinned databases: " + ", ".join(unpinned))
    raise typer.Exit(EXIT_SHIP)


@app.command()
def run(
    run_id: str = typer.Option(..., help="Run identifier recorded in evidence.yaml."),
    principal: str = typer.Option(..., help="Principal recorded in evidence.yaml."),
    root: Path = typer.Option(None, help="Project root. Defaults to the parent of .audit."),
) -> None:
    """Execute every registered instrument and write .audit/evidence.yaml.

    Phase 1 item 9 makes the emitted file the only evidence source a downstream
    reviewer or model may cite, so every instrument result, coverage gap, raw
    artifact reference, and normalized issue lands in it.
    """
    base = root or core.project_root()
    binding = verify_scope_binding(base)
    _refuse_on_scope_mismatch(binding)

    reconnaissance = recon_mod.collect(base)
    document = _new_document(run_id, principal, reconnaissance)

    results = _execute_instruments(base, reconnaissance)
    for result in results:
        document.add(result)
    ledger_result, ledger_rows = _ledger_outcome(base, results)
    if ledger_result is not None:
        document.add(ledger_result)
    document.ledger.extend(ledger_rows)

    path = document.write()
    typer.echo(f"wrote {path}")
    typer.echo(f"disposition: {document.disposition.token}")
    raise typer.Exit(exit_code_for(document.disposition))


def _ledger_outcome(
    base: Path, results: list[core.InstrumentResult]
) -> tuple[core.InstrumentResult | None, list]:
    """Derive the step 8q reward coverage ledger from the executed families.

    The ledger resolves a pair as detected only when the covering atom actually
    ran in this gate, so it runs once, after every family has reported, with the
    reconciled results in hand. Running it inside the family loop would see no
    live atoms and emit a false did-not-run gap for every covered pair, so the
    ledger is excluded from that loop and both its instrument result and its
    rows come from this single post-family invocation. A ledger module failure
    yields nothing, which leaves every applicable pair unresolved rather than
    asserting coverage the run cannot witness.
    """
    try:
        import ledger as ledger_mod
    except ImportError:
        return None, []
    result, rows = ledger_mod._run_ledger(base, results)
    return result, rows


def _execute_instruments(
    base: Path, reconnaissance: recon_mod.Recon
) -> list[core.InstrumentResult]:
    """Dispatch each instrument family and collect its result.

    Families register themselves lazily so a module that fails to import
    surfaces as an explicit coverage gap rather than silently shrinking the
    instrument set.
    """
    results: list[core.InstrumentResult] = []
    for module_name, entry in _FAMILY_ENTRYPOINTS:
        try:
            module = __import__(module_name)
            runner = getattr(module, entry)
        except (ImportError, AttributeError) as exc:
            results.append(
                core.InstrumentResult(
                    instrument=module_name,
                    ran=False,
                    gaps=[
                        core.CoverageGap(
                            gap_id=f"D-FAMILY-UNAVAILABLE-{module_name.upper()}",
                            instrument=module_name,
                            surface="harness_code",
                            reason="family-module-unavailable",
                            caps=Disposition.HOLD,
                            statement=(
                                f"The instrument family module {module_name} did not import, "
                                f"so its atoms produced no determination: {exc}"
                            ),
                        )
                    ],
                )
            )
            continue
        results.extend(runner(base, reconnaissance))
    return results


_FAMILY_ENTRYPOINTS: tuple[tuple[str, str], ...] = (
    ("scanners", "run_family"),
    ("leakgate", "run_family"),
    ("provenance", "run_family"),
    ("delivery", "run_family"),
    ("verifier", "run_family"),
    ("rubric", "run_family"),
    ("contamination", "run_family"),
    ("reward", "run_family"),
    ("adversary", "run_family"),
    ("fidelity", "run_family"),
    ("reference", "run_family"),
    ("calibration", "run_family"),
    ("lineage", "run_family"),
    ("attestation", "run_family"),
)


@app.command()
def selfcheck(
    root: Path = typer.Option(None, help="Project root. Defaults to the parent of .audit."),
) -> None:
    """Run every deterministic self verification check and write selfcheck.yaml.

    Verifier principle 7 makes this the gate that proves each required check is
    live. A required row whose outcome reads inert or unrun caps at BLOCK, and
    a row proving only the clean half is itself a coverage gap.
    """
    base = root or core.project_root()
    try:
        import selfcheck as selfcheck_mod
    except ImportError as exc:
        typer.echo(f"SELFCHECK_UNAVAILABLE: {exc}", err=True)
        raise typer.Exit(EXIT_BLOCK) from exc

    rows = selfcheck_mod.run_all(base)
    path = selfcheck_mod.write(rows, base)
    disposition = core.cap_all(row.caps for row in rows)
    broken = [row.check_id for row in rows if row.required and row.outcome in core.BROKEN_OUTCOMES]

    typer.echo(f"wrote {path}")
    typer.echo(f"rows: {len(rows)}")
    if broken:
        typer.echo("broken required checks: " + ", ".join(sorted(broken)))
    typer.echo(f"disposition: {disposition.token}")
    raise typer.Exit(exit_code_for(disposition))


@app.command()
def verify(
    findings: Path = typer.Option(..., help="Path to .audit/findings.yaml."),
    context: Path = typer.Option(..., help="Path to .audit/evidence.yaml."),
    root: Path = typer.Option(None, help="Project root. Defaults to the parent of .audit."),
) -> None:
    """Reconcile submitted findings against recorded evidence.

    This is the only command whose success means the gate passed. Exit 0 is
    reached only when every verifier rule of Phase 1 item 10 holds and no cap
    stands.
    """
    base = root or core.project_root()
    try:
        import verify as verify_mod
    except ImportError as exc:
        typer.echo(f"VERIFY_UNAVAILABLE: {exc}", err=True)
        raise typer.Exit(EXIT_BLOCK) from exc

    report = verify_mod.verify_findings(findings, context, base)
    for violation in report.get("violations", []):
        typer.echo(f"{violation['rule']}: {violation['statement']}", err=True)
    disposition = report.get("disposition", Disposition.BLOCK)
    typer.echo(f"disposition: {disposition.token}")
    raise typer.Exit(exit_code_for(disposition))


@app.command("all")
def run_all(
    run_id: str = typer.Option(..., help="Run identifier recorded in evidence.yaml."),
    principal: str = typer.Option(..., help="Principal recorded in evidence.yaml."),
    root: Path = typer.Option(None, help="Project root. Defaults to the parent of .audit."),
) -> None:
    """Execute provision, run, selfcheck, verify in order, stopping at the first cap.

    Ordering matters: provisioning resolves what the run may cite, the run emits
    the evidence selfcheck proves live, and verification reads both.
    """
    base = root or core.project_root()
    worst = Disposition.SHIP
    for name, invoke in (
        ("provision", lambda: provision(root=base)),
        ("run", lambda: run(run_id=run_id, principal=principal, root=base)),
        ("selfcheck", lambda: selfcheck(root=base)),
    ):
        try:
            invoke()
        except typer.Exit as exit_signal:
            code = exit_signal.exit_code or 0
            stage = {EXIT_SHIP: Disposition.SHIP, EXIT_HOLD: Disposition.HOLD}.get(
                code, Disposition.BLOCK
            )
            worst = core.cap(worst, stage)
            typer.echo(f"{name}: {stage.token}")
            if stage is Disposition.BLOCK:
                break
    typer.echo(f"disposition: {worst.token}")
    raise typer.Exit(exit_code_for(worst))


def main() -> int:
    """Entry point used by the console script declared in pyproject.toml."""
    try:
        app()
    except SystemExit as exit_signal:
        return int(exit_signal.code or 0)
    return EXIT_SHIP


if __name__ == "__main__":
    sys.exit(main())
