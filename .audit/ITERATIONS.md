# CRUCIBLE iteration log

This log carries one dated differential per Phase 0 pass, per Phase 0 step 3. Each entry states the surfaces that were unchanged, newly present or changed, and removed, measured against the `.audit/` ledger as it stood at the start of that pass.

## 2026-09-23, run crucible-ankitporwal04-20260923t005222z-dba1b1

Cold run. Phase 0 step 1 found no prior CRUCIBLE harness under `.audit/`: the directory carries only `research.md` from Phase R and this run's records under `.audit/runs/`. No `scope.yaml`, no `crucible.py`, no instrument registry, no drift ledger, no negative controls, no custom rules and no waivers exist to preserve, so this is a NEW run and not an UPDATE run, and nothing is migrated.

Unchanged surfaces: none. There is no prior ledger to compare against, so no surface can be classified unchanged.

Newly present surfaces: the whole audited tree. Three committed task bundles at `4c7b8d6f-c500-585d-b7b2-3519df55b1b3`, `6bf0c918-e9ad-5397-bb76-cf3e238f2df1` and `873914cf-93b2-57a0-a5c8-264bfa2d3b66`, each carrying `environment/`, `instruction.md`, `solution/`, `tests/`, `trajectories/` and `task.toml`. Repository-level surfaces `README.md`, `LICENSE`, `images/`, `TRACKING.md`, `.gitmodules`, `.gitignore` and the full git history of seventeen commits. The vendored `trinity/` gitlink at its pinned commit. The gate surfaces `.github/`, `.githooks/`, `.opencode/` and `.agents/` written by `gate.py install`.

Removed surfaces: none.

Rule 5 differential: `requirements/`, `brief/`, `touchstones/`, `samples/` and `delivery/` are all absent at this root. Under invocation item 9 this checkout is a verification root, so those roster-forbidden surfaces are recorded OUT OF SCOPE in `scope.yaml` and are never coverage gaps. No digest is recorded for an absent input and no binding input change is detected, so nothing in this pass re-triggers a prior Phase 0.5 sign-off.

Direction differential: the parent ENGRAM root at the outer checkout published epoch 1 during this run, clearing the `VERIFICATION_ROOT_UNPUBLISHED` stop that halted the previous invocation before Phase 0. `CRUCIBLE_VIEW` is now bound to that epoch and its manifest digest recomputes.
