# TRUTH.md - reflex-dev__reflex-1369

## Defect

The milestone bundles 6 announced issue(s):
1. (#1351): Expose SQLALCHEMY_ECHO like sqlalchemy-flask
2. (#1342): Websocket namespace routing fails when not root directory
3. (#1374): table: allow rows to be a Var
4. (#1329): on_change event sent twice when on_key_down is also used
5. (#1382): Fix sitemap output dir
6. (#1389): Fix foreach index type

The reference change touches 10 file(s) in python. 5 target test(s) observe the result and 8 preserve test(s) must keep passing.

## Load-bearing work

The reference change lands in 8 file(s):

- `reflex/components/tags/iter_tag.py`
- `reflex/utils/build.py`
- `reflex/config.py`
- `reflex/components/datadisplay/table.py`
- `reflex/app.py`
- `reflex/constants.py`
- `reflex/model.py`
- `pyproject.toml`

What each file must end up doing is declared in `rubrics.json`, which is what the deterministic channel reads. This section names the files so a reader knows the shape of the work, not the text to type.

## Verification

Run the target test(s) recorded in `tests/config.json` (5) and confirm the preserve set (8) still passes.

## Root cause

The websocket event namespace is hardcoded to a fixed root-relative path (`/event`) when the app installs its socket handler. This path is baked in with no reference to how the application is actually served. When the frontend and backend are mounted under a non-root prefix (e.g. the API is exposed at `/api/event` rather than `/event`), the server registers the socket namespace at the literal root path while the client attempts to connect at the configured, prefixed path. The two disagree, so websocket connection/routing fails: the handler is bound to a namespace that the client never targets.

Nothing in the configuration layer computes what the namespace ought to be. There is no accessor that derives the namespace from either an explicit user setting or from the configured event endpoint URL, so the app has no way to align the registered namespace with the real serving path. The five failing tests all assert that, given various configuration inputs, a single computed namespace value comes out normalized (leading slash, no trailing slash, defaulting sensibly to the event endpoint's path).

## Solution shape

The configuration object must gain a way to report the correct websocket namespace, and the app must register its socket handler at that value instead of a literal constant.

The namespace resolution needs this behavior:
- If the user supplied an explicit namespace setting, normalize it: strip surrounding slashes and re-prefix with exactly one leading slash. So `event`, `/event`, `event/` all collapse to `/event`; a prefixed value like `api/event` becomes `/api/event`.
- If no explicit setting is given, fall back to the path component of the configured event endpoint's URL.

```
def resolve_namespace(config):
    if config.explicit_namespace:
        return "/" + config.explicit_namespace.strip("/")
    return url_path_of(event_endpoint_url())
```

The explicit setting itself should be a new config field, populated from an environment-driven value, defaulting to unset.

At app construction, replace the hardcoded namespace string with the resolved value; if resolution yields nothing usable, fail loudly rather than binding an empty namespace.

The five named tests only exercise the config-level resolution across input variants (default, prefixed, and the various slash-normalization forms), so the config accessor is the part under direct test; the app wiring must be updated for the fix to actually take effect at runtime.

## Ordered plan

1. Add the environment-backed configuration constant and the config field that holds an optional explicit namespace. This has to come first because the accessor reads from it and the tests construct the config with these kwargs.

2. Implement the namespace accessor on the config object with the normalization-and-fallback rules above. This is the unit directly observed by the failing tests; once it correctly handles the "explicit value → single-leading-slash, no trailing slash" and "unset → endpoint path" cases, all five parametrized cases pass. Verify against the test's expected outputs for the plain, prefixed, and slash-decorated inputs.

3. Rewire the app to call the accessor instead of using the literal namespace, and reject an empty result. This is what makes the fix real at runtime; it depends on step 2 existing. It is not covered by the named tests but is required for the milestone's actual bug.

The remaining milestone items (sitemap output directory, SQL echo flag, foreach index typing, table rows-as-Var, double on_change) are independent and can be done in any order relative to the namespace work, since none shares state with it.

## Pitfalls

- **Normalization asymmetry**: it is tempting to only add a leading slash without stripping a trailing one, or to strip only one side. The tests feed inputs decorated on both ends and with internal path segments; a fix that mishandles `event/` or `api/event/` passes some parametrized cases and fails others. Strip both ends, then prepend exactly one slash.

- **Forgetting the fallback path extraction**: when no explicit namespace is set, the correct default is the *path* of the event endpoint URL, not the whole URL. Returning the full URL (with scheme/host) or a bare constant string will diverge from the expected default output.

- **Fixing only the config and not the app**: the named tests pass once the accessor is correct, but the milestone's real bug (websocket routing under a non-root prefix) is unfixed unless the app actually consumes the accessor. A change that leaves the hardcoded namespace in the socket handler makes the tests green while the reported failure persists.

- **Binding an empty namespace silently**: if resolution can return nothing (empty explicit value plus an endpoint whose path is empty), passing that straight to the socket handler produces a subtly broken registration. Guard against the empty result rather than trusting it.

- **Over-broad normalization of the endpoint fallback**: the strip-and-prefix logic should apply to the explicit setting only; the endpoint-derived path is already a proper path and re-normalizing it can drop or duplicate slashes incorrectly.

## Provenance

```yaml
uuid: 56e866ec-41f7-428b-9c91-51b9787ce934
instance_id: reflex-dev__reflex-1369
fix_patch_sha256: d1920c6735d784c4e166c177719015039466554b2304f8513bddb0809b9373db
language: python
targets_total: 5
authored_by: generated
status: verified_reference
golden_score_measured: 1.0
golden_score_runs: 1
golden_score_verified_by: recorded_test_results
caveat: >
  Probes are literal substrings of the reference hunks, so the
  golden-patch probe gate passes by construction and is not
  evidence of probe quality for this bundle.
```
