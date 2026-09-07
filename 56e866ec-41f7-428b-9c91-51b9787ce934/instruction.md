I've uploaded a Python code repository in the directory /workspace/reflex. Consider the following issue description:

<issue_description>

## Issue 1 (#1351): Expose SQLALCHEMY_ECHO like sqlalchemy-flask

For debugging, it should be simple to set this common environment variable to allow creation of the engine with `echo=True`

## Issue 2 (#1342): Websocket namespace routing fails when not root directory

**Describe the bug**
The websocket event namespaces in the frontend and backend can get out of sync when api_url is set to a non-root directory such as `https://www.domain.com/api/` even if everything is correctly proxied via nginx or similar. Note, this occurs AFTER the websocket connection is established and once an event occurs.

**To Reproduce**
- have the backend running at `https://www.domain.com/api` or 'http://localhost/api' or similar
- setup the config as such:

```
config = pc.Config(
...
    api_url="https://www.domain.com/api",
)
```
**Expected behavior**
The frontend and backend should be in sync in regards to websocket event namespace. Either the frontend needs changes to send `/event/` even if api_url is set to something non-standard or the backend should be changed to expect `api_path + /event/`

**Screenshots**
Logs showing the websocket connection can successfully establish, but once its established the requested event handler is out of sync with that is hardcoded into the `pc.App.__init()`.
```
DEBUG:    > HTTP/1.1 101 Switching Protocols
DEBUG:    > Upgrade: websocket
DEBUG:    > Connection: Upgrade
DEBUG:    > Sec-WebSocket-Accept: ktcaYTD1OHahZUTx095a4PE4AMc=
DEBUG:    > Sec-WebSocket-Extensions: permessage-deflate
DEBUG:    > date: Thu, 13 Jul 2023 03:16:43 GMT
DEBUG:    > server: uvicorn
INFO:     connection open
DEBUG:    = connection is OPEN
DEBUG:    > TEXT '0{"sid":"...","upgrades":[],"p...0,"pingInterval":25000}' [87 bytes]
DEBUG:    < TEXT '40/api/event,' [13 bytes]
DEBUG:    > TEXT '44/api/event,"Unable to connect"' [32 bytes]
DEBUG:    < CLOSE 1005 (no status code [internal]) [0 bytes]
DEBUG:    = connection is CLOSING
DEBUG:    > CLOSE 1005 (no status code [internal]) [0 bytes]
DEBUG:    x half-closing TCP connection
DEBUG:    = connection is CLOSED
INFO:     connection closed
```

**Additional context**

For my specific case, these changes seemed to work by changing the namespace on the backend, but likely could make some adjustments to the frontend to fix this alternatively:
``` 
# Configure app with main state class
app = pc.App(state=State)

# Fix for the FastAPI OpenAPI/docs page
app.api.root_path = "/api"

# Fix for websocket namespace
event_namespace = pc.app.EventNamespace("/api/event", app)
app.sio.register_namespace(event_namespace)
```

## Issue 3 (#1374): table: allow rows to be a Var

render the table correctly when rows is a Var, rather than some static data

Here's an example app I was playing with

```python
import reflex as rx


class Thing(rx.Model, table=True):
    a: str = "alpha"
    b: str = "bravo"
    c: str = "charlie"


class State(rx.State):
    _refresh: int = 0

    def on_submit(self, form_data):
        if any(form_data.values()):
            with rx.session() as session:
                session.add(Thing(**form_data))
                session.commit()
        yield self.do_refresh

    def do_refresh(self):
        self._refresh += 1

    @rx.cached_var
    def table_rows(self) -> list[list]:
        if self._refresh > 0:
            with rx.session() as session:
                return [
                    [getattr(t, field) for field in Thing.__fields__]
                    for t in session.exec(Thing.select.order_by(Thing.id.desc())).all()
                ]
        return []


def index() -> rx.Component:
    return rx.fragment(
        rx.color_mode_button(rx.color_mode_icon(), float="right"),
        rx.vstack(
            rx.form(
                *[
                    rx.input(placeholder=field, id=field)
                    for field in Thing.__fields__
                    if field != "id"
                ],
                rx.button("Save", type_="submit"),
                on_submit=[
                    State.on_submit,
                    *[
                        rx.set_value(field, "")
                        for field in Thing.__fields__
                        if field != "id"
                    ],
                ],
            ),
            rx.button("Reload", on_click=State.do_refresh),
            rx.table(
                headers=list(Thing.__fields__),
                rows=State.table_rows,
            ),
            padding_top="10%",
        ),
    )


app = rx.App(state=State)
app.add_page(index, on_load=State.do_refresh)
app.compile()
```

## Issue 4 (#1329): on_change event sent twice when on_key_down is also used

**Describe the bug**
When an `input` or `text_area` has both `on_change` and `on_key_down` handlers defined (even if they do _nothing_), typing into the component causes `on_change` to be sent twice.

**To Reproduce**
```python
import reflex as rx


class State(rx.State):
    def on_key_down(self, key):
        print(f"on_key_down: {key}")

    def on_change(self, value):
        print(f"on_change: {value}")


def index() -> rx.Component:
    return rx.vstack(
        rx.input(
            placeholder="Double on_change box",
            on_change=State.on_change,
            on_key_down=State.on_key_down,
        ),
        rx.input(placeholder="Single on_change box", on_change=State.on_change),
        padding_top="5%",
    )


app = rx.App(state=State)
app.add_page(index)
app.compile()
```

**Specifics (please complete the following information):**
 - Python Version: 3.11.4
 - Reflex Version: 0.2.0
 - OS: macOS 13.4.1
 - Browser (Optional): firefox

## Issue 5 (#1382): Fix sitemap output dir

Fix the output dir of the sitemap

## Issue 6 (#1389): Fix foreach index type

Make sure the type of the index is `int` to make type checking happy.

## Repository Information

- **Repository**: reflex-dev/reflex
</issue_description>

Can you help me implement the necessary changes to the repository so that the requirements specified in the <issue_description> are met?
The <issue_description> above usually describes MANY separate issues, not one. Every issue listed in it is in scope. There is no single "real" issue hidden among the others, and you cannot tell which one matters most by inspecting the repository — so do not guess, and do not stop after fixing one.
I've already taken care of all changes to any of the test files described in the <issue_description>. This means you MUST NOT modify the testing logic or any of the tests in any way!
Also the development Python environment is already set up for you (i.e., all dependencies are already installed). Do not download or install a different, newer, or "fixed" version of the package(s) under test, and do not fetch any external source, release, or patch to obtain the solution. Reinstalling an already-declared dependency to repair a broken environment is fine.
Your task is to make thorough, complete changes to non-test files in the /workspace/reflex directory so that EVERY issue described in the <issue_description> is satisfied. Do not optimise for a small diff. Scope each edit to what its own issue actually requires — do not refactor unrelated code for style.

Follow these phases to resolve the issue:

Phase 1. READING: read the problem and reword it in clearer terms
   1.1 If there are code or config snippets. Express in words any best practices or conventions in them.
   1.2 Highlight message errors, method names, variables, file names, stack traces, and technical details.
   1.3 Explain the problem in clear terms.
   1.4 Enumerate the steps to reproduce the problem.
   1.5 Highlight any best practices to take into account when testing and fixing the issue.

Phase 2. RUNNING: run the existing tests on the repository
   2.1 Follow the readme.
   2.2 The environment and dependencies are already installed; if something reports missing, repair it using only locally available packages.
   2.3 Iterate and figure out how to run the tests.

Phase 3. EXPLORATION: find the files that are related to the problem and possible solutions
   3.1 Use `grep` to search for relevant methods, classes, keywords and error messages.
   3.2 Identify all files related to the problem statement.
   3.3 Propose the methods and files to fix the issue and explain why.
   3.4 From the possible file locations, select the most likely location to fix the issue.

Phase 4. TEST CREATION: before implementing any fix, create a script to reproduce and verify the issue
   4.1 Look at existing test files in the repository to understand the test format/structure.
   4.2 Create a minimal reproduction script that reproduces the located issue.
   4.3 Run the reproduction script with `python <filename.py>` to confirm you are reproducing the issue.
   4.4 Adjust the reproduction script as necessary.

Phase 5. FIX ANALYSIS: state clearly the problem and how to fix it
   5.1 State clearly what the problem is.
   5.2 State clearly where the problem is located.
   5.3 State clearly how the test reproduces the issue.
   5.4 State clearly the best practices to take into account in the fix.
   5.5 State clearly how to fix the problem.

Phase 6. FIX IMPLEMENTATION: Edit the source code to implement your chosen solution.
   6.1 Make focused changes that fully address the issue you are currently working on.

Phase 7. VERIFICATION: Test your implementation thoroughly.
   7.1 Run your reproduction script to verify the fix works.
   7.2 Add edge cases to your test script to ensure comprehensive coverage.
   7.3 Run existing tests related to the modified code with `pytest` to ensure you haven't broken anything.

Phase 8. FINAL REVIEW: Carefully re-read the problem description and review your own changes with `git diff`.
   8.1 Ensure you've fully addressed all requirements.
   8.2 Run any tests in the repository related to:
      8.2.1 The issue you are fixing
      8.2.2 The files you modified
      8.2.3 The functions you changed
   8.3 If any tests fail, revise your implementation until all tests pass.

Be thorough in your exploration, testing, and reasoning. It's fine if your thinking process is lengthy - quality and completeness are more important than brevity.

IMPORTANT CONSTRAINTS:

- ONLY modify files within the /workspace/reflex directory
- DO NOT navigate outside this directory (no `cd ..` or absolute paths to other locations)
- DO NOT create, modify, or delete any files outside the repository
- All your changes must be trackable by `git diff` within the repository
- If you need to create test files, create them inside the repository directory
- Solve ONLY from the code already present in /workspace/reflex. Do NOT obtain, view, or reconstruct the reference solution from any external source: do not clone/fetch/pull the upstream repository or a mirror; do not download or install a different/newer/"fixed" version of the package(s) under test; do not fetch pull-request or commit diffs (GitHub/GitLab APIs, patch/diff endpoints); and do not read post-baseline git history, tags, stashes, or remotes to locate the change. A patch derived from a retrieved reference solution is invalid and will not be scored.
