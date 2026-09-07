# TRUTH.md - dgtlmoon__changedetection.io-594

## Defect

The milestone bundles 7 announced issue(s):
1. (#593): ModuleNotFoundError: No module named 'changedetectionio.model'
2. (#599): Fix PLAYWRIGHT_DRIVER_URL default value
3. (#214): [feature] Add configurable delay to WebDriver interface to allow pages to fully load before extracting text
4. (#608): Option to control if pages with no renderable content are a change (like JS webapps that dont render any text sometimes etc)
5. (#610): Proxy list settings on watch should have a "[ ] default" option
6. (#611): Input field tidyup
7. (#617): API Interface

The reference change touches 23 file(s) in python. 37 target test(s) observe the result and 19 preserve test(s) must keep passing.

## Load-bearing work

The reference change lands in 8 file(s):

- `changedetectionio/api/api_v1.py`
- `changedetectionio/__init__.py`
- `changedetectionio/static/js/global-settings.js`
- `changedetectionio/api/auth.py`
- `changedetectionio/templates/settings.html`
- `changedetectionio/templates/edit.html`
- `changedetectionio/static/styles/styles.scss`
- `changedetectionio/content_fetcher.py`

What each file must end up doing is declared in `rubrics.json`, which is what the deterministic channel reads. This section names the files so a reader knows the shape of the work, not the text to type.

## Verification

Run the target test(s) recorded in `tests/config.json` (37) and confirm the preserve set (19) still passes.

## Root cause

The application ships several pieces of behaviour that are either broken or missing, and the test suite exercises them together.

First, the entire test suite fails to import or run because of a broken module reference: something in the import chain refers to a `changedetectionio.model` package that does not exist, which raises `ModuleNotFoundError` at collection time. Until that import resolves, *every* test in the suite errors out — which is why tests unrelated to the new features (encoding detection, whitespace, CSS filters, etc.) are all listed as needing to go from failing to passing. They are collateral of a single import break.

Second, there is no programmatic HTTP interface. The new API tests expect to fetch a single watch's metadata, trigger a recheck, read/delete history, create a watch, and delete a watch, all over `/api/v1/...` endpoints, with an optional `x-api-key` header enforcing access. None of that machinery exists, and there is no token-based gate, so requests either 404 or succeed unauthenticated.

Third, the WebDriver fetcher has no per-watch configurable delay. The delay before extracting text is hardcoded to an environment variable only, so a page that renders content late cannot be given extra settle time from the UI, and there is no notion of "fall back to the global default when the watch has none."

Fourth, pages that return HTML but no renderable text are silently treated as unchanged, because the fetcher never distinguishes "empty rendered content" from "content we should compare." A JS webapp that intermittently renders nothing produces a blank extraction that gets compared as if it were real. The nonrenderable-pages test needs the fetcher to raise on genuinely empty content and needs a settings toggle that decides whether an empty page counts as a change.

Fifth, the proxy selector on a watch has no way to express "use the global default." The current logic forces a concrete proxy value, so there is no neutral/default option and no way to clear an override back to the system setting.

## Solution shape

The fix must give the code these properties:

- **Imports resolve.** Whatever reference points at the nonexistent `model` package must be corrected so the package imports cleanly; the suite cannot even start otherwise. This is the precondition for all other tests.

- **A versioned REST surface exists** under `/api/v1/watch...` mounted on the Flask app, using a REST framework layered on top. Endpoints must cover: GET a single watch (returning its data but *not* the potentially huge history list — return a count instead and strip the history), a query-parameter that queues a recheck and returns success, DELETE a watch, plus create-watch and history read/delete resources. The resource objects need access to the datastore and the recheck queue, injected at registration time.

- **An auth gate** wraps the protected endpoints. Its behaviour: if token enforcement is disabled in settings, allow through; if enabled and the request lacks the expected header, respond 403; if the header is present but does not match the configured token, respond 403; otherwise proceed. `test_access_denied` pins the 403 path and `test_api_simple` pins the allowed path.

- **A configurable per-watch render delay.** Add a numeric field on both the per-watch edit form and the global settings form. The fetcher gains an attribute for extra seconds to add *on top of* the existing env-derived minimum wait, applied at both places the fetcher currently sleeps/waits. When a watch's delay is unset, the code must treat it as "use the global default" — and the edit UI should indicate when the global default is in effect.

- **Empty-render handling.** The fetcher must detect when rendered page content is effectively empty and raise a dedicated exception rather than returning blank text. A settings toggle decides whether such an empty page is recorded as a change. The nonrenderable test asserts the default treatment.

- **A "default" proxy choice.** The proxy dropdown must offer a neutral option representing "use system/global proxy," rendered as the first choice. When the stored proxy value is empty or names a proxy that no longer exists, normalise it to that neutral option; when the user selects it, persist the watch's proxy as absent (None) rather than an empty string.

- **The CSRF exemption** for the API must be arranged so token-header clients are not blocked by form CSRF.

Pseudocode for the auth gate:

```
def gate(view):
    def wrapped(self, *a, **k):
        settings = self.datastore application settings
        if not token_enforcement_enabled(settings):
            return view(self, *a, **k)
        header = request header for the api key, or missing
        if header missing:            return 403 json
        if header != configured token: return 403 json
        return view(self, *a, **k)
    return wrapped
```

Note the reference gate returns nothing (implicit None) when enforcement is off; a cleaner variant that proceeds to the view is equally acceptable as long as `test_api_simple` still gets its data.

## Ordered plan

1. **Fix the broken `model` import first.** Nothing else can be observed until collection succeeds. Run the suite; if it errors at import with `ModuleNotFoundError: changedetectionio.model`, correct the offending import path. When the bulk of unrelated tests (encoding, whitespace, filters) start passing, you know this was the sole blocker for them.

2. **Introduce the datastore fields** the new features depend on: a per-watch render delay, a global default render delay, an application-level token, a token-enforcement flag, and an "empty page is a change" toggle. These must exist before forms or the fetcher can reference them.

3. **Build the auth decorator and the REST resources**, then register them on the app with the datastore and recheck queue injected. Register the CSRF exemption so header-only clients pass. Do the GET-single-watch shape carefully: strip history and expose a count, or the payload balloons. This makes `test_api_simple`, `test_access_denied`, and the delete/history paths reachable.

4. **Add the render-delay field to both forms and wire the fetcher** to add that delay on top of the env minimum, at every point it currently waits. Make an unset per-watch value fall back to the global default, and surface that state in the edit UI.

5. **Add empty-content detection in the fetcher** (raise a dedicated exception when rendered text is blank) and the settings toggle governing whether that is a change. Verify against the nonrenderable test.

6. **Rework the proxy choices** to include a leading neutral "default" option, normalise stale/empty values to it, and persist the selection as None when neutral. This is independent of the API work and can be done any time after step 1.

7. **Rename the old form-handler routes** consistently (the templates reference the delete/clone endpoints by name via `url_for`) so template links and route names still match. If you rename a route, update its template references in the same pass or the pages 500.

Steps 3–6 are independent of each other but all depend on 1 and 2.

## Pitfalls

- **Applying the render delay in only one place.** The fetcher waits in two spots (an extra-wait computation and a sleep). Patching one and not the other passes a naive smoke test but leaves late-rendering pages under-waited in the other code path.

- **Leaking the full history through the single-watch GET.** Returning the raw watch dict makes the endpoint slow and the test may still pass on small fixtures; the requirement is to omit the history list and return only its length.

- **Getting the auth gate's "disabled" branch wrong.** If token enforcement is off, the gate must not block; if you accidentally require the header unconditionally, `test_api_simple` breaks. Conversely, if you never check the token when enforcement is on, `test_access_denied` breaks. Both branches are pinned.

- **Forgetting the CSRF exemption on the API.** The site uses form CSRF protection; without exempting the API resources, header-based clients get rejected before auth even runs, and the failure looks like an auth bug.

- **Treating empty rendered content as valid text.** If you compare a blank extraction directly, a JS page that rendered nothing looks identical to a previous blank and never flags — or worse, flips state noisily. The empty case must be its own signal, and whether it counts as a change must be governed by the new toggle, not hardcoded.

- **Persisting the neutral proxy as an empty string.** The datastore expects absence (None) for "use global proxy." Storing `''` will not match "no override" logic elsewhere and can cause the dropdown to re-render as a stale/invalid selection. Normalise empty selection to None on save and normalise unknown/empty values to the neutral choice on render.

- **Renaming routes without updating template `url_for` calls.** The edit template links to the delete and clone handlers by route name. Rename the Python endpoints and the old names in the templates will raise a build error at render time.

## Provenance

```yaml
uuid: 5fee266c-fa53-41c7-bdbd-285e188670ac
instance_id: dgtlmoon__changedetection.io-594
fix_patch_sha256: ff24e3f980495f3712cde6a8281f9533e2be3eb69260ca61c46775fdb32f248f
language: python
targets_total: 37
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
