I've uploaded a Python code repository in the directory /workspace/changedetection.io. Consider the following issue description:

<issue_description>

## Issue 1 (#593): ModuleNotFoundError: No module named 'changedetectionio.model'

ModuleNotFoundError: No module named 'changedetectionio.model'

Just updated to changedetection.io-0.39.13-py3-none-any.whl
Running on Ubuntu via pip3 install.

## Issue 2 (#599): Fix PLAYWRIGHT_DRIVER_URL default value

cf. #587

## Issue 3 (#214): [feature] Add configurable delay to WebDriver interface to allow pages to fully load before extracting text

Some sites take a time to load JavaScript content (e.g. eshop has content filtering JS code). At times I get detection before JS runs and sometimes after, so I'm constantly getting detections, but these are false. Now, do I have to increase [this](https://github.com/dgtlmoon/changedetection.io/blob/05f7e123edb46858c3a98e7a281f30600957ba87/changedetectionio/content_fetcher.py#L89) and then finally make my custom rebuilt Docker image? 
Thank you so much for your help and tool. 
Ďěkuji.

## Issue 4 (#608): Option to control if pages with no renderable content are a change (like JS webapps that dont render any text sometimes etc)

## Issue 5 (#610): Proxy list settings on watch should have a "[ ] default" option

## Issue 6 (#611): Input field tidyup

## Issue 7 (#617): API Interface

Maybe https://github.com/python-restx/flask-restx is better than RESTful - I'de like to learn how to use https://swagger.io/ and make better documentation https://flask-restx.readthedocs.io/en/latest/swagger.html

Think I'll get the tests passing using RESTful then upgrade to restx/swagger

- [x] Complete API
- [x] ~~Add token generator for auth header?~~ or just use an apiKey in the requests header?
- [x] Tests

Update the wiki after merge https://github.com/dgtlmoon/changedetection.io/wiki/API-Reference

# API Access

A new API key section is added in global config

<img src="https://user-images.githubusercontent.com/275001/169546445-3e9e18fa-9649-4867-9cd7-6bb5f6d87ffe.png"  height="200">

Always include `x-api-key` header value if enabled, copy/paste the key from the global settings page

# API Overview

**`http://localhost/api/v1/watch`**
**GET** - Get a list of existing watches, append `recheck_all=1` to force recheck of all
**POST** - Create a new watch `'{"url": "https://my-nice.com", "tag": "optional one, optional two" , "title": "optional title"}'`

**`http://localhost/api/v1/watch/<string:uuid>`**
**GET** - Get information about a single watch, excluding the history list (can be large) , append `recheck=1` to force recheck
**DELETE** - Delete a single watch by UUID

**`http://localhost//api/v1/watch/<string:uuid>/history`**
**GET** - List all history (timestamps) of watch by UUID

**`http://localhost/api/v1/watch/<string:uuid>/history/<string:timestamp>`**
**GET** - Retrieve a snapshot by `timestamp` or `latest` for latest

## Repository Information

- **Repository**: dgtlmoon/changedetection.io
</issue_description>

Can you help me implement the necessary changes to the repository so that the requirements specified in the <issue_description> are met?
The <issue_description> above usually describes MANY separate issues, not one. Every issue listed in it is in scope. There is no single "real" issue hidden among the others, and you cannot tell which one matters most by inspecting the repository — so do not guess, and do not stop after fixing one.
I've already taken care of all changes to any of the test files described in the <issue_description>. This means you MUST NOT modify the testing logic or any of the tests in any way!
Also the development Python environment is already set up for you (i.e., all dependencies are already installed). Do not download or install a different, newer, or "fixed" version of the package(s) under test, and do not fetch any external source, release, or patch to obtain the solution. Reinstalling an already-declared dependency to repair a broken environment is fine.
Your task is to make thorough, complete changes to non-test files in the /workspace/changedetection.io directory so that EVERY issue described in the <issue_description> is satisfied. Do not optimise for a small diff. Scope each edit to what its own issue actually requires — do not refactor unrelated code for style.

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

- ONLY modify files within the /workspace/changedetection.io directory
- DO NOT navigate outside this directory (no `cd ..` or absolute paths to other locations)
- DO NOT create, modify, or delete any files outside the repository
- All your changes must be trackable by `git diff` within the repository
- If you need to create test files, create them inside the repository directory
- Solve ONLY from the code already present in /workspace/changedetection.io. Do NOT obtain, view, or reconstruct the reference solution from any external source: do not clone/fetch/pull the upstream repository or a mirror; do not download or install a different/newer/"fixed" version of the package(s) under test; do not fetch pull-request or commit diffs (GitHub/GitLab APIs, patch/diff endpoints); and do not read post-baseline git history, tags, stashes, or remotes to locate the change. A patch derived from a retrieved reference solution is invalid and will not be scored.
