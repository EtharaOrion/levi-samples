I've uploaded a Python code repository in the directory /workspace/changedetection.io. Consider the following issue description:

<issue_description>

## Issue 1 (#3433): Re #3393 #3419 Implementation of unread counter along with realtime updates

- [ ] needs a test for the `?unread=1` flag (or maybe it exists?)

## Issue 2 (#3434): `downloads/octet-streams` / attachments should be checked for their text (or HTML) content type and processed for changedetection

**Describe the bug**
I noticed that a watched website can be monitored fine as long as the server sends `content-type: text/plain; charset=utf-8`, but once the server sends `content-type: application/octet-stream` (which is usually done to force the browser to show the Download dialog), changedetection somehow ignores all line breaks and treats the document file as if everything is on one line.

**Version**
v0.50.13

**How did you install?**
Docker:
`image: ghcr.io/dgtlmoon/changedetection.io`

**To Reproduce**
Monitor this url: `https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml`
Check the preview.

**Expected behavior**
Document should break after each linebreak character in the file (i.e. whenever a 0x0A character appears in the file).

**Screenshots**
<img width="2366" height="342" alt="Image" src="https://github.com/user-attachments/assets/a5b4ebcf-e566-488b-852a-8d01592db0c8" />

**Desktop (please complete the following information):**
not really relevant, but:
 - OS: Windows
 - Browser Firefox
 - Version 142

**Smartphone (please complete the following information):**
N/A

**Additional context**
Same file works fine when `content-type: text/plain; charset=utf-8` is set, you can check out this URL for comparison: `https://github.com/immich-app/immich/raw/refs/heads/main/docker/docker-compose.yml`

## Issue 3 (#3443): Apprise 1.9.4

## Issue 4 (#3446): Attempt to fix socks test server test

## Issue 5 (#1411): Add healthcheck in Docker

Hi, it would be nice to have a simple, built-in healthcheck in the Docker image.

It has neither curl nor wget installed so it's not as trivial as just adding `curl -f http://localhost:5000 || exit 1` as the healthcheck.

Thank you.

## Issue 6 (#1412): `Accept-Language` header gets ignored by Playwright

**Describe the bug**
I am trying to force a specific language version of a website, which they determine based on the `Accept-Language` header. However, Playwright seems to ignore it altogether. I tested independently using my desktop browser and setting the `Accept-Language` there works as expected: the specific language version of a website is shown depending on the header's content.

**Version**
v0.40.1.1

**To Reproduce**

Steps to reproduce the behavior:
1. Go to any website that serves different language based on `Accept-Language` (i.e. outside of any cookie that could store that information)
3. Set the `Accept-Language` to an arbitrary language that would request a said version of the website
4. Notice that it has no effect

**Expected behavior**
`Accept-Language` should be passed and applied to every Playwright request.

## Issue 7 (#3449): Adding "Strip ignored lines" options to filters

## Issue 8 (#3455): fixing build test

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
