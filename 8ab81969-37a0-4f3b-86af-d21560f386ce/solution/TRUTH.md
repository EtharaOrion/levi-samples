# TRUTH.md - dgtlmoon__changedetection.io-3433

## Defect

The milestone bundles 8 announced issue(s):
1. (#3433): Re #3393 #3419 Implementation of unread counter along with realtime updates
2. (#3434): `downloads/octet-streams` / attachments should be checked for their text (or HTML) content type and processed for changedetection
3. (#3443): Apprise 1.9.4
4. (#3446): Attempt to fix socks test server test
5. (#1411): Add healthcheck in Docker
6. (#1412): `Accept-Language` header gets ignored by Playwright
7. (#3449): Adding "Strip ignored lines" options to filters
8. (#3455): fixing build test

The reference change touches 22 file(s) in python. 35 target test(s) observe the result and 51 preserve test(s) must keep passing.

## Load-bearing work

The reference change lands in 8 file(s):

- `changedetectionio/static/styles/scss/parts/_watch_table.scss`
- `changedetectionio/processors/text_json_diff/processor.py`
- `changedetectionio/static/js/realtime.js`
- `changedetectionio/static/styles/scss/styles.scss`
- `changedetectionio/blueprint/watchlist/templates/watch-overview.html`
- `changedetectionio/static/styles/scss/parts/_socket.scss`
- `changedetectionio/store.py`
- `changedetectionio/blueprint/settings/templates/settings.html`

What each file must end up doing is declared in `rubrics.json`, which is what the deterministic channel reads. This section names the files so a reader knows the shape of the work, not the text to type.

## Verification

Run the target test(s) recorded in `tests/config.json` (35) and confirm the preserve set (51) still passes.

## Root cause

Two independent gaps produce the failing behaviour.

**Non-HTML/download content is never treated as text.** The text/JSON diff processor decides how to extract comparable content from the response body. As it stands, it only falls into a plain-text handling path when the response's `content-type` header explicitly announces plain text. Servers frequently serve text or HTML documents with `application/octet-stream`, with a `content-disposition` marking the body as a downloadable attachment, or with a content type that omits any HTML hint. In all of those cases the processor takes the HTML-parsing branch (or otherwise mishandles the body), so a body that is really plain text is scraped through an HTML extractor and the resulting comparison text is wrong or empty. There is no attempt to sniff the actual byte content to recover the true type when the declared header is unreliable.

**There is no "strip ignored lines" capability at all.** The processor computes the text used for change-detection and separately applies ignore rules only for the purpose of masking lines during comparison — the ignored lines still appear in the stored/preview output. There is no per-watch or global option that, when enabled, physically removes ignored lines from the output text so that the change-detection text and the visible snapshot are identical. Tests that ask for this option to actually delete matched lines have nothing to toggle.

**The unread accounting is boolean, not a count, and the UI is wired to the wrong signal.** The datastore exposes only a yes/no "is anything unviewed" predicate. The realtime layer and the overview template are built around that boolean plus per-row CSS classes, and the realtime handler listens on a watch-update event and mutates individual tab elements. There is no integer telling the UI how many watches are unread, so a numeric unread counter cannot be rendered or updated live, and the socket test that expects a distinct stats event with a count has no such event to observe.

The failing tests span both areas: the mime/download test and most filter/ignore/json tests exercise the content-type sniffing and text-extraction path (which many of them go through implicitly), the strip test exercises the new removal option, and the socketio test exercises the count-based realtime event.

## Solution shape

Three properties must hold.

**1. Robust content-type resolution in the text/JSON processor.**
Before deciding how to extract text, compute an effective content type. If the declared header signals a download (an octet-stream type, or a content-disposition indicating an attachment) *or* simply does not advertise HTML, sniff the actual body bytes with a magic-number library and, if that yields a plausible mime string (contains a slash), prefer the sniffed value over the header. Then branch on the *resolved* type:

```
declared = headers.content-type (lowercased)
looks_like_download = "attachment" in content-disposition
                      or "octet-stream" in declared
                      or "html" not in declared
if looks_like_download:
    sniffed = magic.from_buffer(body, mime=True)
    if sniffed looks like a real mime type:
        declared = sniffed
if declared starts with "text/" and is not html:
    treat body as plain text  # not HTML scraping
```
Sniffing failures must be caught and logged, never fatal.

**2. Optional removal of ignored lines.**
Add a setting resolvable both globally (application settings) and per-watch, where the per-watch value overrides the global when set. When enabled, the text used for the stored snapshot/preview must equal the text used for checksumming — i.e. the lines matched by ignore rules are physically dropped from the output, not merely skipped during comparison. Expose a checkbox for it in the settings UI.

**3. Count-based unread signal end to end.**
Replace the boolean unviewed predicate on the datastore with a method that returns an integer: the number of watches currently in an unread state. Emit a dedicated realtime "stats" event carrying that count (and the error count); the client handler for that event should render the count into an unread counter element and toggle wrapper-level state classes based on whether the count/error count are non-zero. The overview template should render the initial count and set the wrapper's classes from the initial count/error values, moving the show/hide styling to depend on wrapper-level classes rather than per-element classes.

## Ordered plan

1. **Fix content-type resolution first**, because the largest block of failing tests (filters, ignore, jsonpath/jq, restock, basic detection) only pass once bodies are extracted as the correct type. Implement the sniff-and-branch logic in the processor and confirm the mime/download test and the broad filter suite go green. This is the highest-leverage step and everything else is independent of it.

2. **Add the strip-ignored-lines option** next, since it is self-contained: introduce the setting (global default + per-watch override with override precedence), make the processor set the output text equal to the checksum text when enabled, and add the settings checkbox. Verify the strip test. This depends on nothing from step 1 but shares the same processor file, so doing it here avoids re-touching that code twice.

3. **Convert the unread boolean to a count** in the datastore. Do this before touching the UI/realtime, because both the template and the socket handler consume the new integer.

4. **Emit the count via a dedicated realtime stats event** and update the client to handle it: write the count into a counter element and toggle wrapper classes. This depends on step 3 existing.

5. **Update the overview template and styling** to render the initial count, compute wrapper classes from count/error state, and drive visibility from wrapper-level classes. The socketio test passes once the event and the counter element both exist.

Steps 3–5 form one dependency chain (data → event → markup/style). Step 1 and step 2 are independent of that chain and of each other, but step 1 unblocks the most tests, so it comes first.

## Pitfalls

- **Sniffing gated too narrowly.** If you only sniff when the header is octet-stream, you'll still mishandle HTML/text served with a missing or generic type and with an attachment content-disposition. The trigger must include "not announced as HTML" and the attachment disposition, not just octet-stream, or the download test can pass while ordinary mislabelled text still routes through HTML extraction.

- **Sniffing that overrides a good header.** Only prefer the sniffed value when it is a plausible mime string (has a slash); a blank or garbage result from the magic library must not clobber the declared type, and an import/runtime failure of that library must be caught so it degrades to header-based behaviour rather than crashing the check.

- **Treating HTML text as plain text.** After resolving the type, the plain-text branch must exclude HTML (`text/html`), or you'll skip HTML scraping for real HTML pages and break the css-selector/include-filter tests.

- **Strip option that only masks.** Making the ignore rules skip lines during comparison but leaving them in the snapshot passes nothing new — the test checks the removed lines are actually absent from output. The output text must become the checksum text when enabled.

- **Forgetting the override direction.** A per-watch value of "unset" must fall back to the global setting; a per-watch explicit value must win. Reading only the global, or only the per-watch, will fail one direction of the option.

- **Leaving the boolean predicate live.** If any caller still uses the old yes/no unviewed method after you add the count, or if the realtime event keeps firing on the old watch-update path instead of a distinct stats event, the socket test won't see the numeric counter update it expects. The counter element must exist in the initial markup too, or the client has nothing to write into.

- **Number formatting.** The counts are rendered with locale-aware formatting; a test or UI expectation may depend on the counter element being present and populated, so ensure both the initial server-rendered value and the live-updated value target the same element.

## Provenance

```yaml
uuid: 8ab81969-37a0-4f3b-86af-d21560f386ce
instance_id: dgtlmoon__changedetection.io-3433
fix_patch_sha256: 4cd2c427ff837f37db7a6345a1b6f97ca7fad2976ba6f5f28148639eb06a84e4
language: python
targets_total: 35
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
