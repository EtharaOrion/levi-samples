# TRUTH.md - reflex-dev__reflex-269334014d4d

GENERATED SECTION. DO NOT HAND-EDIT.

# FORGE canary block. Derived from the canonical content hash.
# FORGE-CANARY[00]=24553901DC6282770870EDB77847B933
# FORGE-CANARY[01]=E5E6C24D72D8532B145FBBE50F827476
# FORGE-CANARY[02]=A95995746EB340C766897008A27FF7FC
# FORGE-CANARY[03]=8042888AF71769D13D156A4A17FF2E7A

## Defect

Reflex event objects offer no supported way for application authors to control DOM event propagation or the browser's default behavior. There is no chainable property on the event handler, the event spec, or the event chain that requests stopPropagation or preventDefault, and there are no top-level attributes that can be assigned to a trigger to request those DOM actions without a state update. Additionally, the preventDefault behavior for form submission is hardcoded in the generic frontend runtime rather than expressed through a general, composable mechanism.

The reference change touches 6 source file(s) in python across 192 hunk(s). 18 target test(s) observe the result and 286 preserve target(s) must keep passing.

## Load-bearing work

The reference change lands in these files:

- `.devcontainer/devcontainer.json`
- `CONTRIBUTING.md`
- `README.md`
- `docker-example/Dockerfile`
- `docs/es/README.md`
- `docs/in/README.md`
- `docs/it/README.md`
- `docs/kr/README.md`
- `docs/pt/pt_br/README.md`
- `docs/tr/README.md`
- `docs/zh/zh_cn/README.md`
- `docs/zh/zh_tw/README.md`
- `poetry.lock`
- `pyproject.toml`
- `reflex/.templates/apps/sidebar/code/styles.py`
- `reflex/.templates/apps/sidebar/code/templates/template.py`
- `reflex/.templates/web/utils/helpers/dataeditor.js`
- `reflex/.templates/web/utils/state.js`
- `reflex/__init__.py`
- `reflex/components/component.py`
- `reflex/components/datadisplay/dataeditor.py`
- `reflex/components/datadisplay/dataeditor.pyi`
- `reflex/components/forms/form.py`
- `reflex/components/forms/iconbutton.py`
- `reflex/components/layout/foreach.py`
- `reflex/components/navigation/stepper.py`
- `reflex/components/tags/iter_tag.py`
- `reflex/config.py`
- `reflex/config.pyi`
- `reflex/event.py`
- `reflex/reflex.py`
- `reflex/utils/exec.py`
- `reflex/utils/format.py`
- `reflex/utils/hosting.py`
- `reflex/utils/prerequisites.py`
- `integration/init-test/in_docker_test_script.sh`

What each file must end up doing is declared in `rubrics.json`, which is what the deterministic channel reads. This section names the files so a reader knows the shape of the work, not the text to type.

## Verification

Apply the committed test patch, run the target set recorded in `tests/config.json` (18), and confirm the preserve set (286) still passes.

## Ordered plan

1. Add an EventActionsMixin to reflex/event.py holding an event_actions dict and providing stop_propagation and prevent_default as chainable properties that return copies with the added action and never mutate the receiver.
2. Make EventHandler and EventSpec inherit the mixin, and add an EventSpec.with_args helper that copies the spec with new args while preserving event_actions.
3. Update EventHandler.__call__ to pass a copy of its event_actions into the produced EventSpec, including the upload/special client-handler path.
4. Give EventChain an event_actions field and update _create_event_chain in component.py to rebuild specs via with_args, collect the union of specs' actions, attach them to the chain, and accept a directly passed EventChain.
5. Define two top-level attributes (for stopPropagation and preventDefault) that produce action-only event chains, and export them from reflex/__init__.py.
6. Remove the hardcoded form-submit preventDefault from reflex/.templates/web/utils/state.js and declare prevent_default on the form component's submit trigger in reflex/components/forms/form.py.
7. Regenerate affected stub files (for example dataeditor.pyi) so the public surface stays consistent with the updated definitions.
8. Run the target and preserve tests, confirming action-free triggers and chains behave identically and combined actions apply as specified.

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
  "base_commit_sha": "269334014d4dd717f7a8424e9af2c87ed6e82fb0",
  "instance_identity": "reflex-dev/reflex v0.3.1..v0.3.2",
  "license": "unresolved",
  "number_interval": "1891-2028-2062-2068-2069-2072-2076-2082-2084-2085-2086-2089-2090-2092-2094-2095-2097-2099-2102-2104-2109-2116-2117-2118-2121-2122-2124-2125-2126-2128",
  "origin": "derived",
  "provenance_date": "2023-10-27T23:50:39Z",
  "repository": "reflex-dev/reflex",
  "repository_canonical_identity": "R_kgDOITROHQ",
  "source_kind": "public_repository",
  "span_label": "v0.3.1..v0.3.2"
}
```