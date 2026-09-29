# TRUTH.md - reflex-dev__reflex-977cc6990f22

GENERATED SECTION. DO NOT HAND-EDIT.

# FORGE canary block. Derived from the canonical content hash.
# FORGE-CANARY[00]=E553CE85A6EB1F7D4A7659959DEDB7A0
# FORGE-CANARY[01]=A9641C2DD6753F65E328BF2EBA5300DC
# FORGE-CANARY[02]=31FE7C963D6FB908C38453B641ADF0E7
# FORGE-CANARY[03]=3B134102F505CD43087B73B2BFADFFCF

## Defect

When a Pynecone application is launched in production mode on Windows, the backend server fails to start at all because the framework unconditionally invokes a process manager that cannot run on that platform. The same production command works correctly on Linux and other Unix-like systems. Additionally, the pre-start port-cleanup step crashes with a permission error when the operating system refuses to let the framework terminate the process currently holding the target port, a situation that is especially common on Windows.

The reference change touches 3 source file(s) in python across 104 hunk(s). 8 target test(s) observe the result and 150 preserve target(s) must keep passing.

## Load-bearing work

The reference change lands in these files:

- `README.md`
- `poetry.lock`
- `pynecone/.templates/app/tutorial.py`
- `pynecone/.templates/web/package.json`
- `pynecone/.templates/web/pynecone.json`
- `pynecone/.templates/web/utils/state.js`
- `pynecone/__init__.py`
- `pynecone/app.py`
- `pynecone/compiler/compiler.py`
- `pynecone/compiler/templates.py`
- `pynecone/compiler/utils.py`
- `pynecone/components/__init__.py`
- `pynecone/components/base/__init__.py`
- `pynecone/components/base/meta.py`
- `pynecone/components/component.py`
- `pynecone/components/datadisplay/table.py`
- `pynecone/components/forms/__init__.py`
- `pynecone/components/forms/upload.py`
- `pynecone/components/layout/__init__.py`
- `pynecone/components/layout/cond.py`
- `pynecone/components/layout/responsive.py`
- `pynecone/components/media/icon.py`
- `pynecone/components/overlay/alertdialog.py`
- `pynecone/components/overlay/drawer.py`
- `pynecone/components/overlay/modal.py`
- `pynecone/components/tags/tag.py`
- `pynecone/config.py`
- `pynecone/constants.py`
- `pynecone/event.py`
- `pynecone/middleware/hydrate_middleware.py`
- `pynecone/pc.py`
- `pynecone/route.py`
- `pynecone/state.py`
- `pynecone/utils.py`
- `pyproject.toml`

What each file must end up doing is declared in `rubrics.json`, which is what the deterministic channel reads. This section names the files so a reader knows the shape of the work, not the text to type.

## Verification

Apply the committed test patch, run the target set recorded in `tests/config.json` (8), and confirm the preserve set (150) still passes.

## Ordered plan

1. Add a constant to pynecone/constants.py naming the Windows-capable backend server command, alongside the existing Unix production server constant.
2. In pynecone/utils.py, import or confirm access to the platform module and branch run_backend_prod on platform.system() == 'Windows'.
3. On the Windows branch, build the command using the new constant with host, port, the module:app entry point, and the server's native argument style; on the non-Windows branch keep the exact prior Unix invocation including bind, threads, and the factory-style entry point.
4. Append the shared log level and worker count arguments after the branch so both servers receive them in a correct form, preserving the original values.
5. Wrap the kill() call in kill_process_on_port with contextlib.suppress against the process library's permission-denied exception, and ensure contextlib and the process library are imported.
6. Regenerate any template and manifest output under .templates and any lock or generated files that the broader change alters, so freshly built apps are consistent.
7. Run the eight target tests to confirm they pass and the platform branching and cleanup tolerance behave as expected.
8. Run the full preserved suite to confirm the Unix command line and all other behaviour remain byte-for-byte unchanged.

## Human-review residue

Item 10f requires every human-review item to name the semantic residue that blocks compilation. The rubric item schema is closed at eight fields, so the residue is recorded here rather than as a ninth field the schema does not admit.

- `R1`: The compiled surface is keyed on load-bearing sites and fair-play gates rather than on rubric item identifiers, so this item has no compiled counterpart to reduce to. The residue is the whole judgment.
- `R2`: The compiled surface is keyed on load-bearing sites and fair-play gates rather than on rubric item identifiers, so this item has no compiled counterpart to reduce to. The residue is the whole judgment.
- `R3`: The compiled surface is keyed on load-bearing sites and fair-play gates rather than on rubric item identifiers, so this item has no compiled counterpart to reduce to. The residue is the whole judgment.
- `R4`: The compiled surface is keyed on load-bearing sites and fair-play gates rather than on rubric item identifiers, so this item has no compiled counterpart to reduce to. The residue is the whole judgment.
- `R5`: The compiled surface is keyed on load-bearing sites and fair-play gates rather than on rubric item identifiers, so this item has no compiled counterpart to reduce to. The residue is the whole judgment.
- `R6`: The compiled surface is keyed on load-bearing sites and fair-play gates rather than on rubric item identifiers, so this item has no compiled counterpart to reduce to. The residue is the whole judgment.

## Rejected routes

- {'bound_control': 'controls.check_empty_submission', 'route': 'submit nothing and let the preserve suite carry the score', 'why_rejected': 'An empty submission leaves every fail-to-pass target unresolved and must score exactly zero under the bound reward schema.'}
- {'bound_control': 'controls.check_oracle_submission', 'route': 'submit a change that only appears to differ from no change', 'why_rejected': 'The oracle submission and the empty submission must differ; a bundle where they do not has a reward channel that cannot tell them apart.'}
- {'bound_control': 'controls.check_judged_inputs', 'route': 'reach the graded outcome by reading a judged input rather than by changing world state', 'why_rejected': 'Judged inputs are checked for the private carriers they must never contain, so a route that answers from them rather than from the environment is rejected.'}

## Provenance

```json
{
  "attestation_state": "attestation-unavailable",
  "base_commit_sha": "977cc6990f22cbd1f11049aef6f9b9bb63af7f3f",
  "instance_identity": "reflex-dev/reflex v0.1.18..v0.1.19",
  "license": "unresolved",
  "number_interval": "570-571-583-588-589-591-593-594-596-601-614-615-616-617-618-622-624-625-626-629-630",
  "origin": "derived",
  "provenance_date": "2023-02-21T07:33:08Z",
  "repository": "reflex-dev/reflex",
  "repository_canonical_identity": "R_kgDOITROHQ",
  "source_kind": "public_repository",
  "span_label": "v0.1.18..v0.1.19"
}
```
