You are working in the Python repository at `/workspace/reflex`.

Reflex applications build interactive UIs by attaching event handlers to component event triggers, and those triggers ultimately fire from DOM events in the browser. Today an application author has no supported way to control how the underlying DOM event propagates or whether its default browser behavior runs. A handler attached to a nested element cannot prevent its event from bubbling up to a parent element that also has a handler, and a handler attached to something like a link cannot suppress the browser's built-in navigation. The objective of this change is to give authors that control by exposing two composable event actions that instruct the frontend to call the DOM event's stopPropagation and preventDefault, respectively, when the event is processed.

These actions must be available on the objects that users already work with when wiring up events: the event handler that a state method becomes, the event specification produced by calling a handler with arguments, and the event chain that a trigger is compiled into. Each action must be accessible as a chainable property that returns an equivalent event object carrying the requested action, so that expressions such as a handler followed by stop_propagation and then prevent_default read naturally and can be combined in any order. Accessing an action must not mutate the original object; it must yield a new object that behaves identically except for the added action. When a handler carrying an action is called with arguments to produce a spec, the action must carry through to that spec, and when specs are assembled into a chain, the union of their actions must apply to the chain.

The library must also offer two new top-level attributes that can be assigned directly to an event trigger to request stopPropagation or preventDefault without triggering any state update of their own. These are useful when an interactive element sits on top of a clickable parent and clicks should not reach the parent, even though the element itself needs no explicit handler because its behavior is implicit. Assigning one of these to a trigger must result in an event chain that performs only the requested DOM action.

For the deprecated list-based event chain form, where multiple handlers are supplied as a list, an action declared on any entry cannot be scoped to that single entry because of how the chain executes; in that case the action must apply to the entire chain. This is the only sensible behavior for that legacy form and should be treated as intended, not as a defect.

As part of this work the special handling that previously forced preventDefault for form submit events in the frontend runtime must be removed from that generic location and instead expressed through the same new mechanism at the point where the form component itself is defined, so that form submission continues to prevent the default browser submit exactly as it does now. Any generated or stub output that mirrors the public surface of components touched by this change must be regenerated so that it stays consistent with the updated definitions. This is an additive feature and not a breaking change: existing applications that do not use the new actions must continue to compile and behave exactly as before, event triggers and chains without any action must be unaffected, and all previously working event wiring must keep functioning unchanged.

The description below carries several separate issues. Every issue in it is in scope. Work through all of them.

## Issue 1

Pull request #1621: [REF-675] Stop click propagation

Is there a way of stopping the propagation of "onClick" events?

I have a button that sits on top of a clickable hstack, when I click  the button, the hstack also gets clicked.

My current workaround is to have a variable to prevent the double click but this obviously makes the code messier than it has to be.

Any way of preventing the double click?

[https://github.com/reflex-dev/reflex/pull/1891](https://github.com/reflex-dev/reflex/pull/1891)

<sub>From [SyncLinear.com](https://synclinear.com) | [REF-675](https://linear.app/reflex-dev/issue/REF-675/stop-click-propagation)</sub>

Interface (names the hidden tests import; implementation is yours):
- `EventActionState.handler`
- `EventHandler.event_actions`
- `EventActionsMixin.event_actions`
- `EventActionsMixin.prevent_default(self)`
- `EventActionsMixin.stop_propagation(self)`
- `EventHandler.prevent_default`
- `EventHandler.stop_propagation`
- `prevent_default`
- `stop_propagation`

## Issue 2

Pull request #2028: Added Spanish Readme

### All Submissions:

- [ :white_check_mark:] Have you followed the guidelines stated in [CONTRIBUTING.md](https://github.com/reflex-dev/reflex/blob/main/CONTRIBUTING.md) file?
- [:white_check_mark: ] Have you checked to ensure there aren't any other open [Pull Requests](https://github.com/reflex-dev/reflex/pulls ) for the desired changed?

<!-- You can erase any parts of this template not applicable to your Pull Request. -->

### Type of change

Please delete options that are not relevant.

- [ :white_check_mark:] This change requires a documentation update

### Description
Hi! I have added a Spanish translation of the Readme file. 
Will continue fixing typos. Just wanted to translate the main parts of the readme first!

## Issue 3

Pull request #2062: Bump to v0.3.0

## Issue 4

Pull request #2068: pyproject.toml: bump typer to 0.9.0

Upgrade `typer` to 0.9.0 and `poetry update` all other deps.

## Issue 5

Pull request #2069: fix: Typo in README.md

### All Submissions:

- [x] Have you followed the guidelines stated in [CONTRIBUTING.md](https://github.com/reflex-dev/reflex/blob/main/CONTRIBUTING.md) file?
- [x] Have you checked to ensure there aren't any other open [Pull Requests](https://github.com/reflex-dev/reflex/pulls ) for the desired changed?

<!-- You can erase any parts of this template not applicable to your Pull Request. -->

### Type of change

Change in documentation


### New Feature Submission:

- [x] Does your submission pass the tests? 
- [x] Have you linted your code locally prior to submission?

### Changes To Core Features:

- [x] Have you added an explanation of what your changes do and why you'd like us to include them?
- [x] Have you written new tests for your core changes, as applicable?
- [x] Have you successfully ran tests with your changes locally?

### **After** these steps, you're ready to open a pull request.

    a. Give a descriptive title to your PR.

    b. Describe your changes.

    c. Put `closes #XXXX` in your comment to auto-close the issue that your PR fixes (if such).

## Issue 6

Pull request #2072: fix: Grammatical error & typo in CONTRIBUTING.md

### All Submissions:

- [x] Have you followed the guidelines stated in [CONTRIBUTING.md](https://github.com/reflex-dev/reflex/blob/main/CONTRIBUTING.md) file?
- [x] Have you checked to ensure there aren't any other open [Pull Requests](https://github.com/reflex-dev/reflex/pulls ) for the desired changed?

<!-- You can erase any parts of this template not applicable to your Pull Request. -->

### Type of change

- [x] This change requires a documentation update


### New Feature Submission:

- [x] Does your submission pass the tests? 
- [x] Have you linted your code locally prior to submission?

### Changes To Core Features:

- [x] Have you added an explanation of what your changes do and why you'd like us to include them?
- [x] Have you written new tests for your core changes, as applicable?
- [x] Have you successfully ran tests with your changes locally?

### **After** these steps, you're ready to open a pull request.

    a. Give a descriptive title to your PR.

    b. Describe your changes.

    c. Put `closes #XXXX` in your comment to auto-close the issue that your PR fixes (if such).

## Issue 7

Pull request #2076: Added links for Github issues and contributing.md file

Added links for Issues and contributing.md in README.md of the repository.
### All Submissions:

- [x] Have you followed the guidelines stated in [CONTRIBUTING.md](https://github.com/reflex-dev/reflex/blob/main/CONTRIBUTING.md) file?
- [x] Have you checked to ensure there aren't any other open [Pull Requests](https://github.com/reflex-dev/reflex/pulls ) for the desired changed?

<!-- You can erase any parts of this template not applicable to your Pull Request. -->

### Type of change

Please delete options that are not relevant.

- [x] This change requires a documentation update

## Issue 8

Pull request #2082: DALL E and API docs

### All Submissions:

- [✔️] Have you followed the guidelines stated in [CONTRIBUTING.md](https://github.com/reflex-dev/reflex/blob/main/CONTRIBUTING.md) file?
- [✔️] Have you checked to ensure there aren't any other open [Pull Requests](https://github.com/reflex-dev/reflex/pulls ) for the desired changed?

<!-- You can erase any parts of this template not applicable to your Pull Request. -->

### Type of change

Please delete options that are not relevant.

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [✔️] This change requires a documentation update





### **After** these steps, you're ready to open a pull request.

    a. Give a descriptive title to your PR.
This pull request adds a documentation link for the DALL-E model from OpenAI. Additionally, I have included a link to the OpenAI API key documentation, allowing users to navigate directly to the page for information on the architecture and use cases of the API.



    b. Describe your changes.
Certainly! In this pull request, I have made the following changes:

a) Added a documentation link for the DALL-E model from OpenAI.
b) Included a link to the OpenAI API key documentation, which provides information on the architecture and use cases of the API.

    c. Put `closes #XXXX` in your comment to auto-close the issue that your PR fixes (if such).
To auto-close the issue that this pull request fixes, I have added "closes #XXXX" in the comment.
<img width="724" alt="image" src="https://github.com/reflex-dev/reflex/assets/67964054/d8ffc665-c076-4751-86de-b443ddd5e9c6">

## Issue 9

Pull request #2084: Expose gunicorn_worker_class via Config

Rather than plumbing through every possible uvicorn parameter that users might need in production, expose the gunicorn_worker_class in the config, which allows downstream code to completely control the worker configuration as needed.

Most users will not need to set this knob, but the moment one needs to tweak websocket protocol flags, timeout values, or the wealth of uvicorn config knobs for tweaking, then it's straightforward to override the worker class and apply these behavior changes.

Fix #2070

## Issue 10

Pull request #2085: Hosting CLI: use http endpoint to return deploy milestones

### All Submissions:

- [x] Have you followed the guidelines stated in [CONTRIBUTING.md](https://github.com/reflex-dev/reflex/blob/main/CONTRIBUTING.md) file?
- [x] Have you checked to ensure there aren't any other open [Pull Requests](https://github.com/reflex-dev/reflex/pulls ) for the desired changed?

<!-- You can erase any parts of this template not applicable to your Pull Request. -->

### Type of change

Please delete options that are not relevant.

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires a documentation update


### New Feature Submission:

- [x] Does your submission pass the tests? 
- [x] Have you linted your code locally prior to submission?

### Changes To Core Features:

- [x] Have you added an explanation of what your changes do and why you'd like us to include them?
- [ ] Have you written new tests for your core changes, as applicable?
- [x] Have you successfully ran tests with your changes locally?

### **After** these steps, you're ready to open a pull request.
- For users with less ideal internet conditions, it's possible the websocket streaming deploy milestones get disconnected. There was no retry mechanism. Instead, hosting service adds an equivalent endpoint to query these events once. CLI can query this endpoint peridiocally.

Interface (names the hidden tests import; implementation is yours):
- `def poll_deploy_milestones(key: str, from_iso_timestamp: datetime) -> bool | None`

## Issue 11

Pull request #2086: fix docker example

### All Submissions:

- [x] Have you followed the guidelines stated in [CONTRIBUTING.md](https://github.com/reflex-dev/reflex/blob/main/CONTRIBUTING.md) file?
- [x] Have you checked to ensure there aren't any other open [Pull Requests](https://github.com/reflex-dev/reflex/pulls ) for the desired changed?

<!-- You can erase any parts of this template not applicable to your Pull Request. -->

### Type of change

Please delete options that are not relevant.

- [x] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires a documentation update


### New Feature Submission:

- [ ] Does your submission pass the tests? 
- [ ] Have you linted your code locally prior to submission?

### Changes To Core Features:

- [ ] Have you added an explanation of what your changes do and why you'd like us to include them?
- [ ] Have you written new tests for your core changes, as applicable?
- [ ] Have you successfully ran tests with your changes locally?

### **After** these steps, you're ready to open a pull request.

    a. Give a descriptive title to your PR.

    b. Describe your changes.

    c. Put `closes #XXXX` in your comment to auto-close the issue that your PR fixes (if such).

## Issue 12

Pull request #2088: Add orientation prop to `rx.stepper` component

`rx.stepper` component is missing an orientation prop. 

```python
class Stepper(ChakraComponent):
   ...
   orientation: Var[Literal["vertical", "horizontal"]] 
```

https://chakra-ui.com/docs/components/stepper/usage

## Issue 13

Pull request #2090: Typos fixed in multiple files

### All Submissions:

- [x ] Have you followed the guidelines stated in [CONTRIBUTING.md](https://github.com/reflex-dev/reflex/blob/main/CONTRIBUTING.md) file?
- [x ] Have you checked to ensure there aren't any other open [Pull Requests](https://github.com/reflex-dev/reflex/pulls ) for the desired changed?

Typos present in comments fixed in multiple file.

## Issue 14

Pull request #2092: make download work for state vars

`rx.download` now also work when provided with State vars.

## Issue 15

Pull request #2094: fix portal when using multiple dataeditor

Fix the issue when using multiple data_editor in the same page.

## Issue 16

Pull request #2095: cleanup dataeditor js code and hooks

some of the changes from #2091 since they can be merged without being blocked by dataframe stuff.

## Issue 17

Pull request #2096: Broken link of wrapping react in readme file

**Describe the bug**
The link to wrapping react in readme file is broken.

**To Reproduce**
Steps to reproduce the behavior:
 - Code/Link to Repo:
 - Go to Readme file
 - Go to Reflex UI section 
 - Click on 

> it's easy to [create your own components](https://reflex.dev/docs/advanced-guide/wrapping-react).

**Expected behavior**
A clear and concise description of what you expected to happen.
The link should not be broken and redirect correctly.

**Screenshots**
If applicable, add screenshots to help explain your problem.
![Screenshot 2023-10-31 221146](https://github.com/reflex-dev/reflex/assets/70795867/2fe35189-190f-4c94-9b18-52ab56cf7743)

**Specifics (please complete the following information):**
 - Python Version:
 - Reflex Version:
 - OS: 
 - Browser (Optional):
 
**Additional context**
Add any other context about the problem here.

## Issue 18

Pull request #2099: add column resize for data editor

Allow resizing columns with onColumnResize.

How it works: 
```python
data_ = {
    "Column1": [1, 2, 3, 4, 5],
    "Column2": ["A", "B", "C", "D", "E"],
    "Column3": [0.1, 0.2, 0.3, 0.4, 0.5],
}

class State(rx.State):
    columns: list = [
        {"title": "Column1", "id": "column1", "type": "int"},
        {"title": "Column2", "id": "column2", "type": "str"},
        {"title": "Column3", "id": "column3", "type": "float"},
    ]
    data: list = [
        dict((key.lower(), value) for key, value in zip(data_.keys(), values))
        for values in zip(*data_.values())
    ]

    def col_resized(self, column, width):
        print(column, width)
        for col in self.columns:
            if col.get("id") == column.get("id"):
                col["width"] = width


def index():
    return rx.hstack(
        # rx.foreach(["B1", "B2", "B3"], button_stop),
        # on_click=State.outer_click,
        rx.data_editor(
            columns=State.columns,
            data=State.data,
            rows=5,
            on_column_resize=State.col_resized,
            overscroll_x=100,
        )
    )
```

## Issue 19

Pull request #2102: [REF-1042] Hosting CLI: check the user selected app name

### All Submissions:

- [x] Have you followed the guidelines stated in [CONTRIBUTING.md](https://github.com/reflex-dev/reflex/blob/main/CONTRIBUTING.md) file?
- [x] Have you checked to ensure there aren't any other open [Pull Requests](https://github.com/reflex-dev/reflex/pulls ) for the desired changed?

<!-- You can erase any parts of this template not applicable to your Pull Request. -->

### Type of change

Please delete options that are not relevant.

- [x] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires a documentation update


### New Feature Submission:

- [x] Does your submission pass the tests? 
- [x] Have you linted your code locally prior to submission?

### Changes To Core Features:

- [x] Have you added an explanation of what your changes do and why you'd like us to include them?
- [ ] Have you written new tests for your core changes, as applicable?
- [x] Have you successfully ran tests with your changes locally?

### **After** these steps, you're ready to open a pull request.
- Check the user input against any characters not allowed in domain name, raise an error
- Clarify it is domain name safe characters when prompt for app name
- Remove the access token validation in hosting.deploy. It is not the first call to hosting server. Token is already validated. This can improve the speed on user with slow internet. 
- If user input contains upper cases, print message informing user that the name is automatically converted to lower cases
- Example 1:
<img width="1078" alt="image" src="https://github.com/reflex-dev/reflex/assets/15661672/6a751a8c-60dd-4d5e-99bd-988e30693491">
- Example 2: <img width="1521" alt="image" src="https://github.com/reflex-dev/reflex/assets/15661672/9fa5e421-779b-4bb1-a8fd-40e8191b1090">

Interface (names the hidden tests import; implementation is yours):
- `def requires_access_token() -> str`

## Issue 20

Pull request #2104: base: expand template content to right edge of screen

remove the rx.spacer which restricts the template page to its minimal width

add flex grow to the template_page_style to let it fill the remaining width

remove width=100% from template_content_style; that's already the default

## Before
![Screenshot 2023-10-31 at 4 09 13 PM](https://github.com/reflex-dev/reflex/assets/1524005/aa5d1149-7fc5-440e-87dc-2424b7c3db27)

## After
![Screenshot 2023-10-31 at 4 09 49 PM](https://github.com/reflex-dev/reflex/assets/1524005/ca0e6a41-38ae-45e0-bbcb-1de72117ad3a)

## Issue 21

Pull request #2109: Use blank template as default

Switch back to the original blank template. The sidebar template can be accessed through `reflex init --template sidebar`

TODO: I still have to switch the file names from "base" -> "sidebar" before we can merge this.

## Issue 22

Pull request #2116: Do not stop prop is there is no prop to stop

Check that desired event actions are defined on the object passed as the DOM event before calling them to avoid frontend errors.

## Issue 23

Pull request #2117: Compatibility with older typer versions

Allow typer versions that do not understand pretty_exceptions_enable kwarg

## Issue 24

Pull request #2118: Fix readme links

Removed extra space that messed up the links

## Issue 25

Pull request #2121: rx.call_script callback needs to await promises

Otherwise, there is no way to get the result of an async operation executed via `rx.call_script`

## Issue 26

Pull request #2122: Prompt for template on reflex init

Ask the user to specify a template interactively on the first `reflex init`.

## Issue 27

Pull request #2124: components as props

Proper feature to use components as props based on #2017 

Auto detect props annotated with type Optional[Component]

Automatically add the imports required for the component prop to work.

Does NOT work with state Var, only compilation time component props are valid.

As example, see the changes in `iconbutton.py` :  This is all that is needed to have components as props.

## Issue 28

Pull request #698: Websockets in Github Codespaces

I've tried using Github Codespaces to run example code. Codespaces lets me install pynecone and run it. Port 3000/8000 are opened and a link is provided to the view the webpage. Keep in mind, the hostname is a custom hostname generated by Github, it obviously can't use localhost or 192.168.1.1.

However, the site is non-responsive. To make sure my code wasn't the issue, I've cloned the _todo_ project. The website renders. If I _add an item_ it is never added to the list. Marking off an item also has no effect.

Sure enough if I look at the Developer Tools, websockets is pointing to 'localhost' still. `WebSocket connection to 'ws://localhost:8000/event/?EIO=4&transport=websocket' failed: Error in connection establishment: net::ERR_CONNECTION_REFUSED`

Is there a config so websockets knows to use the host given by GitHub and not localhost?

## Issue 29

Pull request #2126: Set unique index vars in rx.foreach

Previously we always set the same index var name, so nested foreach loops would overshadow the index var. This PR introduces a unique index name for every foreach component.

Test code:

```python
from rxconfig import config

import reflex as rx
from typing import Tuple, List

class State(rx.State):

    my_tuple: Tuple[str, int, int] = []
    nested_tuple: List[List[Tuple[str, int, int]]] = []

    def my_function(self):
        first_string = 'hello'
        one_string = '1'
        twostring = '2'


        for _ in range(0, 5):
            mylist = []
            for _ in range(0, 5):
                a_tuple = (first_string, int(one_string), int(twostring))
                mylist.append(a_tuple)
            self.nested_tuple.append(mylist)

def display_tuple(a_list, i):
    return rx.foreach(
        a_list,
        lambda thetuple, j: rx.cond(
            # TypeError: Unsupported Operand type(s) for >: `.at(1) of type str and 10` of type int
            True,
            rx.box(i, j),
        ),
    )

def index() -> rx.Component:
    return rx.fragment(
        rx.foreach(
            State.nested_tuple,
            display_tuple,
        ),
    )

app = rx.App()
app.add_page(index, on_load=State.my_function)
app.compile() 
```

Interface (names the hidden tests import; implementation is yours):
- `_var_type`
- `_var_name`

## Issue 30

Pull request #2128: Bump to v0.3.2



## Paths the verifier owns

The grader applies its own version of the 12 path(s) below. Leave every one of them exactly as
it is, including any file a tool of yours would rewrite as a side effect: a submission that changes
one is rejected before a single test runs, and the whole session scores zero however good the rest
of it is. The issue text does not ask for any of them, and neither does anything else here.

- `integration/test_call_script.py`
- `integration/test_event_actions.py`
- `integration/test_form_submit.py`
- `tests/components/base/test_script.py`
- `tests/components/layout/test_foreach.py`
- `tests/components/test_component.py`
- `tests/test_app.py`
- `tests/test_config.py`
- `tests/test_event.py`
- `tests/test_reflex.py`
- `tests/utils/test_format.py`
- `tests/utils/test_hosting.py`

Everything else the issues ask for still applies, including changes to non-test code these paths
exercise. If a command of yours regenerates one of them, restore it before you finish.
## Working instructions

The issue sections above usually describe MANY separate issues, not one. Your job is to implement the changes required by EVERY issue they contain — not just the one that looks most tractable, most self-contained, or easiest to identify. There is no single "real" issue hidden among the others; treat all of them as in scope.

The tests that grade this task are hidden: the updated test files are applied only when your work is graded. The tests you can see in the repository may be outdated and may contradict the issues above, so when a visible test disagrees with an issue, follow the issue text, not the visible test. You MUST NOT modify the testing logic or any of the tests in any way. This prohibition covers not only `_test` files but also test helper packages, fixtures, fakes, stubs, mocks, and example or integration applications that exist to support tests under the test paths described next. If a visible test fails because it asserts behaviour an issue asks you to change, leave the test as it is and implement what the issue asks.

The prohibition is by path, not by file type. Do not write to anything inside a test directory — for example `tests/`, `test/`, `e2e/`, `testdata/`, or any path nested beneath one — even when the file is a README, a markdown document, a diagram, or a config that plainly cannot affect a test result. A submission that touches any path under the graded test tree is rejected in full and scores nothing, however correct the rest of the work is. If an issue on your checklist asks for a change under such a path, mark it BLOCKED with that reason and move to the next issue.

Leave repository plumbing alone on the same terms unless an issue names the file directly: CI workflow definitions, issue and pull-request templates, Helm charts, container manifests, and dependency lockfiles. Treat dependency manifests such as requirements files, package.json, or go.mod as plumbing too, except that a change an issue explicitly asks for, such as a version bump, is in scope, and if that change cannot be built without downloading anything, mark the issue BLOCKED with that reason.

The development environment is already set up for you (i.e., all dependencies are already installed). Do not download or install any package or dependency, including a different, newer, or "fixed" version of the package(s) under test, and do not fetch any external source, release, or patch to obtain the solution.

Your task is to make thorough, complete changes to non-test files in the repository that address EVERY issue above. Do not optimise for a small diff — breadth of coverage across all the issues matters more than the size of any individual change. At the same time, scope each edit to what its issue actually calls for; do not refactor unrelated code for style.

Solve this using only the code already present in the repository; do not retrieve the reference solution from any external source (do not clone, fetch, or pull the upstream repository or a mirror; do not download or install a different, newer, or "fixed" version of the package(s) under test; do not fetch pull-request or commit diffs; and do not read post-baseline git history, tags, stashes, or remotes to locate the change). A solution derived from a retrieved reference is invalid and will not be scored.

Step 0 — Enumerate before you edit.
Read the issues above from beginning to end and write out a numbered checklist of every distinct issue they describe (one entry per `## Issue N` header). State the total explicitly, for example: "Checklist: 34 issues found." Do not begin editing until this checklist exists. Do not attempt to guess which issue is "the important one" — you cannot tell, and guessing is the single most common way this task is failed.

Then work the checklist in order. For each issue, announce which one you are on ("Working on issue N of M: <short title>") and carry out the following:

1. Explore the repo to locate the code responsible for this issue. On the first issue, take extra time to familiarise yourself with the overall structure.
2. Create a script to reproduce the behavior described and execute it using the appropriate command for the repository's language, to confirm it.
3. Edit the source code of the repo to make the change this issue calls for.
4. Rerun your reproduction and check the behavior.
5. Build or compile every package you touched and confirm it compiles cleanly. A change that does not compile scores nothing, and it can break packages that were passing before you started. If you change a function signature, an interface, or a type, find and update every caller and every implementer of it in non-test code before moving on; visible test files that still use the old form are the exception, since you may not edit them.
6. Think about edge cases, add checks for them in your reproduction script, and run them to see how your change handles them.
7. Mark this issue DONE on your checklist, then move to the next one. If an issue genuinely cannot be worked — because it is a pre-existing environment failure unrelated to your changes, or it would require retrieving external code — mark it BLOCKED, state the specific reason in one sentence, and move to the next issue. A blocked issue never ends the session; it only ends work on that issue.

Do not stop early, and do not end the session without calling the `finish` tool: work that is never submitted with `finish` is discarded unscored. Finishing after addressing only one issue, or only a handful, is the primary failure mode on this task — work every item on the checklist, not just the first tractable one. Do not pad with busywork either: every step should be locating, editing, building, or testing real code for a real checklist item. Do not call the `finish` tool until every item on your checklist is marked either DONE or BLOCKED with a stated reason and you have completed the review pass described below. When you finish, report the final tally: how many issues you addressed, and which ones you marked BLOCKED and why.

Once you have made a first pass over the whole checklist, carefully re-read the issues above and review your own changes with `git diff`. For each issue, check whether the change you made matches what it asked for. Write scratch checks outside every test directory and every `_test` file to probe the correctness of your changes, specifically focusing on checks that may point out remaining gaps. Run the tests in the repo related to what you changed and check whether any fail — pay particular attention to tests that were passing before your changes and are failing now, since breaking working code costs more than leaving an issue unaddressed, unless the failing test asserts behaviour an issue asks you to change. Repeat this process of re-reading, testing, and adjusting until you have attempted every checklist item and the packages you touched build cleanly. Find and run any tests in the repo that are related to:
   - Each issue on your checklist
   - The files you modified
   - The functions you changed

Your thinking should be thorough and so it's fine if it's very long. Think carefully before each edit about which issue it serves and what else it might break.

When the review pass is complete and every checklist item is marked DONE or BLOCKED, call the `finish` tool to end the session.

Calling `finish` is what submits your work. The session is scored only if you call it: a session that stops without calling `finish` is discarded, and every change you made scores nothing, however complete it was. Running out of things to say is not finishing. When the checklist is done, call `finish` as your last action, and if you are ever unsure whether you have more to do, call `finish` rather than stopping silently.
