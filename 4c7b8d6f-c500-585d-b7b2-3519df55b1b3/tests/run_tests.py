"""Graded runner for one Trinity task bundle.

Reads the frozen target sets from `config.json`, applies the committed test
patch, runs the fail-to-pass targets and the preserve set, and writes the reward
Harbor reads.

Two properties are load-bearing and both are refusals rather than conveniences.
An empty fail-to-pass set scores zero, never full reward, because the grading
code this task family descends from returns a perfect score for an empty target
list and that turns a suite which never ran into a resolved instance. And the
parsed log is cross-checked against the runner's recorded exit status, because a
patch can print its own passing lines from inside the graded process, so a log
that reports no failure while the runner exited non-zero is not describing the
run that happened.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shlex
import subprocess
import sys

REWARD_JSON = "reward.json"
REWARD_TXT = "reward.txt"
REWARD_REASON_JSON = "reward_reason.json"


# The parsers and the report reader live in the file measurement also imports.
# /tests/harness_core.py is a byte-identical copy of it, so the two sides cannot
# hold different ideas of what passed. They held separate copies and drifted
# three times, the last silently.
from harness_core import PARSERS, collect_reports, resolve_declared  # noqa: E402

# The share of the declared preserve set the preserve run must actually account
# for before a regression verdict means anything. Not 100: a suite legitimately
# skips network-dependent tests under a no-network policy, and refusing those
# would discard sound slots. Not 0 either, which is what the absent check was
# worth -- dozzle accounted for none of its 206 and still reported no
# regressions.
PRESERVE_COVERAGE_FLOOR = 60

_DIFF_PATH = re.compile(r"^diff --git a/(?P<a>.+?) b/(?P<b>.+)$", re.MULTILINE)


def diff_paths(diff_text, modified_only=False):
    """Every post-image path a unified diff touches.

    With ``modified_only``, paths the diff CREATES are excluded. Only a path the
    submission modifies witnesses whether it belongs to this repository: a
    created file is legitimately absent from the base tree, so counting it would
    refuse an honest submission that only adds files.

    Creation is read from the `--- /dev/null` header rather than from the
    `diff --git` line, because git writes `diff --git a/new b/new` for an added
    file too and that line therefore cannot distinguish the two.
    """
    if not modified_only:
        return [m.group("b") for m in _DIFF_PATH.finditer(diff_text or "")]
    out, current, created = [], None, False
    for line in (diff_text or "").splitlines():
        header = _DIFF_PATH.match(line)
        if header:
            if current is not None and not created:
                out.append(current)
            current, created = header.group("b"), False
        elif line.startswith("--- ") and line[4:].strip() == "/dev/null":
            created = True
    if current is not None and not created:
        out.append(current)
    return out


def test_patch_paths(path):
    """The paths the verifier tree owns, read from the test patch itself."""
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        return set()
    owned = set(diff_paths(text))
    owned.update(m.group("a") for m in _DIFF_PATH.finditer(text))
    return owned


def deleted_files(diff_text):
    """Paths a unified diff deletes outright, mapped to their pre-image blob id.

    The mirror of how diff_paths reads creation: deletion is read from the
    `+++ /dev/null` header, because `diff --git a/old b/old` is written for a
    deleted file too. The blob comes from the `index <pre>..<post>` line and is
    None when the diff carries none.
    """
    out, current, blob = {}, None, None
    for line in (diff_text or "").splitlines():
        header = _DIFF_PATH.match(line)
        if header:
            current, blob = header.group("a"), None
        elif current is not None and line.startswith("index "):
            blob = line[6:].split("..", 1)[0].strip() or None
        elif current is not None and line.startswith("+++ ") and line[4:].strip() == "/dev/null":
            out[current] = blob
    return out


def mirrored_deletions(submission_diff, test_patch_path):
    """Owned paths the submission deletes exactly as the test patch itself does.

    A span whose own change removes a test file puts that removal in the test
    patch, so a brief that asks for it -- fastmcp #1723, two stray root test
    files -- sends every correct solution into the verifier-tree guard. Deleting
    such a file is not grading yourself: the test patch makes the same deletion.
    The match is on the deletion, not the path. Both diffs must delete the file
    whole and name the same pre-image blob; a submission that edits, adds, or
    partially changes an owned path is not mirrored and still refuses.
    """
    try:
        with open(test_patch_path, encoding="utf-8", errors="replace") as handle:
            theirs = deleted_files(handle.read())
    except OSError:
        return set()
    same = set()
    for path, blob in deleted_files(submission_diff).items():
        other = theirs.get(path)
        if path in theirs and blob and other and (blob.startswith(other) or other.startswith(blob)):
            same.add(path)
    return same


def run(command, cwd):
    """Run one graded command.

    Deliberately `bash -c` and not `bash -lc`. A login shell re-reads the system
    profile and rebuilds PATH, which drops a toolchain the image installed
    outside the default path. That failure is silent in the worst possible way:
    every target fails to run, the reward is a legitimate-looking zero, and an
    empty-submission control passes for a reason that has nothing to do with the
    submission being empty.
    """
    proc = subprocess.run(["bash", "-c", command], cwd=cwd, capture_output=True,
                          text=True, errors="replace")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


_REWARD_WRITTEN = False


def write_reward(logs, value, reason, counts=None):
    # Harbor's verifier/verifier.py _parse_reward_json requires EVERY value in the
    # object to be a finite number: `values = rewards.values() if isinstance(rewards, dict)
    # else [rewards]` then rejects any non int/float. A "reason" string in reward.json made
    # the whole file unparseable, so Harbor raised VerifierOutputParseError and never read
    # the reward it was sitting next to. The reason is not dropped: it moves to a sibling
    # file, because it is how every no-signal run gets diagnosed.
    global _REWARD_WRITTEN
    _REWARD_WRITTEN = True
    os.makedirs(logs, exist_ok=True)
    with open(os.path.join(logs, REWARD_JSON), "w", encoding="utf-8") as handle:
        json.dump({"reward": round(float(value), 6)}, handle, sort_keys=True)
        handle.write("\n")
    with open(os.path.join(logs, REWARD_TXT), "w", encoding="utf-8") as handle:
        handle.write("%.6f\n" % float(value))
    record = {"reward": round(float(value), 6), "reason": reason}
    if counts:
        record.update(counts)
    with open(os.path.join(logs, REWARD_REASON_JSON), "w", encoding="utf-8") as handle:
        json.dump(record, handle, sort_keys=True)
        handle.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--logs", required=True)
    args = ap.parse_args()
    reward, reason = 0.0, "runner-did-not-complete"
    # Bound before the try so an early exception cannot turn the final write into a
    # NameError. An unbound diagnostic must never be able to destroy the reward itself.
    _final_counts = None
    try:
        with open(args.config, encoding="utf-8") as handle:
            cfg = json.load(handle)
        repo_dir = cfg["repo_dir"]
        parser = PARSERS[cfg["parser"]]
        f2p = list(cfg["f2p_tests"])
        # n2p and s2p are graded beside f2p (operator ruling 2026-09-19). The vocabulary
        # refusals below stay on f2p: an extra target a submission leaves unimportable is a
        # failed target, not a broken grader, and Phase 2 proves each one passes under the oracle.
        extra = list(cfg.get("n2p_tests") or []) + list(cfg.get("s2p_tests") or [])
        p2p = list(cfg["p2p_tests"])

        if not f2p:
            write_reward(args.logs, 0.0, "empty-fail-to-pass-set")
            print("no fail-to-pass target is declared, so there is nothing to grade")
            return 1

        # The workspace is bind-mounted, so its files are owned by the host user
        # while this runs as root, and git refuses to touch a repository it
        # considers foreign. Naming the top-level repository is not enough: a
        # vendored subproject is its own repository, and a build that reads its
        # version through git gets an empty string and fails to configure. The
        # wildcard covers the tree the bundle already owns end to end.
        run("git config --global --add safe.directory '*'", repo_dir)
        run("git config --global --add safe.directory " + repo_dir, repo_dir)

        # Capture the submission before the test patch touches the tree, and
        # measure it against the state the agent was actually given. Both halves
        # matter. Diffing after the test patch is applied puts the reference tests
        # into the submission diff, which shows the judge the answer and makes an
        # empty submission look like a large one. Diffing against HEAD loses the
        # whole submission whenever a run commits its work, which the oracle
        # always does. So the baseline has to be a fixed commit, taken before the
        # patch, that names the tree the agent started from.
        #
        # That commit is not always the root. It is the root for an image whose
        # Dockerfile inits a fresh single-commit repository over the given tree --
        # there, root and the given state are the same object. Both kinds of image
        # this project ships are now that kind: the self-built one unpacks a git
        # archive and inits, and the one derived from a prebuilt evaluator image
        # rebuilds .git as one parentless commit at the base state. In the derived
        # case the declared base commit SHA is an upstream identity that no longer
        # resolves inside the image, which is correct rather than broken, and the
        # depth-one fallback below is the intended path.
        #
        # The third kind is what this logic exists for: an image pinned from the
        # evaluator unchanged carries the upstream history, and its root is the
        # repository's first commit ever. Diffing against that returns the entire
        # history as one submission: measured on dozzle, 408 files across 6179
        # commits, including all three paths the test patch owns. The
        # verifier-tree guard below then intersected those, found the reference
        # tests in a submission that never touched them, and wrote a reward of
        # zero with reason submission-modified-the-verifier-tree over a run the
        # harness had scored 0.08. FORGE no longer authors that kind of bundle,
        # and the guard stays because resident bundles authored before the change
        # are still that kind.
        #
        # So the base commit is preferred and the root is the fallback, and the
        # case where neither is the given state is a refusal rather than a
        # silently enormous diff.
        base = ""
        declared = (cfg.get("base_commit") or "").strip()
        if declared:
            base_code, base_out = run("git rev-parse --verify --quiet " + declared + "^{commit}",
                                      repo_dir)
            if base_code == 0 and base_out.strip():
                base = base_out.strip().splitlines()[-1].strip()
        if not base:
            root_code, root_out = run("git rev-list --max-parents=0 HEAD", repo_dir)
            root = root_out.strip().splitlines()[-1].strip() if root_out.strip() else ""
            count_code, count_out = run("git rev-list --count HEAD", repo_dir)
            try:
                depth = int(count_out.strip().splitlines()[-1].strip())
            except (ValueError, IndexError):
                depth = 0
            if root_code != 0 or not root:
                write_reward(args.logs, 0.0, "submission-diff-unavailable")
                print("could not identify a baseline commit, so the submission cannot be "
                      "separated from the test patch")
                return 1
            if depth > 1:
                write_reward(args.logs, 0.0, "submission-baseline-unresolved")
                print("the declared base commit " + (declared or "<absent>") + " does not resolve "
                      "in this repository and its history is " + str(depth) + " commits deep, so "
                      "the root commit is not the state the agent was given. Diffing against it "
                      "would report the whole history as the submission.")
                return 1
            base = root
        root = base
        run("git add -A", repo_dir)
        submission_code, submission_diff = run("git diff --cached " + root, repo_dir)
        if submission_code != 0:
            write_reward(args.logs, 0.0, "submission-diff-unavailable")
            print(submission_diff[-4000:])
            return 1
        # Subtract what the image already shipped differing from the base commit.
        # `git diff --cached <base>` cannot tell a solver's edit from a divergence the
        # image was built with, so tfsec's absent-but-tracked vendor/ read as 1410
        # deleted files and netbird's pre-written golden testdata read as 267535 bytes
        # on an empty submission. Those paths are measured from the pinned image at
        # authoring time and carried here; a path in that set is not submission content.
        _dirt = set(cfg.get("baseline_dirt") or [])
        if _dirt:
            _kept, _drop, _cur = [], 0, None
            for _ln in submission_diff.splitlines(True):
                if _ln.startswith("diff --git "):
                    _m = re.match(r"diff --git a/(.+?) b/(.+)$", _ln.strip())
                    _cur = (_m.group(2) if _m else "").strip()
                    _drop = _cur in _dirt
                if not _drop:
                    _kept.append(_ln)
            submission_diff = "".join(_kept)
        with open(os.path.join(args.logs, "final.diff"), "w", encoding="utf-8") as h:
            h.write(submission_diff)

        # Reset the state a run may have left behind before grading reads
        # anything. A report file the submission wrote sits exactly where the
        # verifier looks for its own, and a parser cannot tell the two apart:
        # the graded outcome would then be whatever the run chose to write. The
        # submission itself is already captured above, so removing these costs
        # nothing and closes the channel.
        stale = []
        for pattern in cfg.get("report_globs") or []:
            stale.extend(glob.glob(os.path.join(repo_dir, pattern), recursive=True))
        for path in stale:
            try:
                os.remove(path)
            except OSError:
                pass
        if stale:
            print("removed " + str(len(stale)) + " pre-existing report file(s) a run "
                  "could have written where the verifier reads its own")

        # The verifier tree is the answer key. A submission that edits a path the
        # test patch owns is grading itself, and the instruction forbids it, so
        # enforce what final.diff already records rather than only recording it.
        owned = test_patch_paths(cfg["test_patch_path"])
        mirrored = mirrored_deletions(submission_diff, cfg["test_patch_path"])
        touched = sorted((owned & set(diff_paths(submission_diff))) - mirrored)
        if mirrored:
            print("the submission deletes " + str(len(mirrored)) + " owned path(s) exactly as "
                  "the test patch does, first: " + sorted(mirrored)[0])
        if touched:
            write_reward(args.logs, 0.0, "submission-modified-the-verifier-tree")
            print("the submission changed " + str(len(touched)) + " path(s) the test "
                  "patch owns, first: " + touched[0])
            return 1

        # A mirrored deletion is already applied by the submission, so the test
        # patch must not delete the file a second time or git apply refuses the
        # whole patch.
        exclude = "".join(" --exclude=" + shlex.quote(p) for p in sorted(mirrored))
        code, out = run("git apply --whitespace=nowarn" + exclude + " " + cfg["test_patch_path"],
                        repo_dir)
        if code != 0:
            write_reward(args.logs, 0.0, "test-patch-did-not-apply")
            print(out[-4000:])
            return 1

        # Both the submission and the test patch changed sources. For a compiled
        # language the test runner executes binaries, so without rebuilding it
        # runs the artifacts the image was built with: the submission is not in
        # them and neither is the newly added test. Languages whose test command
        # builds declare an empty step and skip this.
        if cfg.get("build_cmd"):
            code, out = run(cfg["build_cmd"], repo_dir)
            if code != 0:
                write_reward(args.logs, 0.0, "build-failed-after-patches")
                print(out[-4000:])
                return 1

        target_code, target_out = run(cfg["target_cmd"], repo_dir)
        report_globs = cfg.get("report_globs") or []
        target_source = collect_reports(repo_dir, report_globs) if report_globs else target_out
        outcomes = parser(target_source)
        with open(os.path.join(args.logs, "target-stdout.md"), "w", encoding="utf-8") as h:
            h.write(target_out)

        # Declared ids and parsed ids are two vocabularies and they do not agree.
        # Matching them exactly credited nothing on eight of the ten Go slots in
        # this batch, because the evaluator records `pkg/path::TestName` and the
        # Go parser emits `TestName`. Measured on dozzle: the target logged
        # `--- PASS`, and the exact lookup below it wrote targets_resolved 0.
        resolved, ambiguous, unseen = resolve_declared(f2p, outcomes)
        # A vocabulary that does not resolve at all is a broken grader, not a
        # failed submission, and it must never be reported as a zero. This check
        # runs BEFORE anything conditioned on the runner's exit status, because
        # the guard that used to cover it did not: it fired only when the runner
        # exited zero, so whether a slot produced an honest refusal or a silent
        # zero was decided by whether some unrelated test in the repository
        # happened to fail. buf exited zero and refused; dozzle exited non-zero
        # and scored a silent zero. Same defect, opposite symptom, and the
        # difference was luck.
        if f2p and len(unseen) == len(f2p):
            write_reward(args.logs, 0.0, "declared-targets-absent-from-output",
                         {"targets_total": len(f2p), "targets_matched": 0, "parsed_keys": len(outcomes)})
            print("none of the " + str(len(f2p)) + " declared target(s) appear in the "
                  "runner's output under any matching, so the declared vocabulary and the "
                  "parsed one do not describe the same suite. First declared: " + f2p[0]
                  + "; first parsed: " + (sorted(outcomes)[0] if outcomes else "<nothing parsed>"))
            return 1
        if ambiguous:
            write_reward(args.logs, 0.0, "declared-target-ambiguous",
                         {"targets_total": len(f2p), "targets_matched": len(resolved), "targets_ambiguous": len(ambiguous)})
            print(str(len(ambiguous)) + " declared target(s) match more than one parsed test "
                  "and crediting either would be a guess, first: " + ambiguous[0])
            return 1
        if unseen:
            write_reward(args.logs, 0.0, "declared-targets-partially-absent",
                         {"targets_total": len(f2p), "targets_matched": len(resolved), "targets_unseen": len(unseen)})
            print(str(len(unseen)) + " of " + str(len(f2p)) + " declared target(s) appear "
                  "nowhere in the runner's output, first: " + unseen[0]
                  + "; the run did not execute the graded surface")
            return 1
        hit = [t for t in f2p if resolved.get(t) == "PASS"]
        extra_resolved = resolve_declared(extra, outcomes)[0] if extra else {}
        extra_hit = [t for t in extra if extra_resolved.get(t) == "PASS"]
        # The log and the exit status must agree in both directions. Every target
        # parsed as passing while the runner failed means the log is not this
        # run's. The mirror case is just as wrong and was unguarded: a clean exit
        # while declared targets appear nowhere in the output means the run never
        # executed them, and scoring the ones it did find would reward a
        # submission for a suite it quietly shrank.
        # A non-zero exit is only evidence of a stale log when the log itself
        # reports nothing failing. A target file that carries an unrelated test
        # already failing at the base commit makes the runner exit non-zero on
        # every run, reference included, while every graded target legitimately
        # passes -- and refusing that discards a sound slot for a failure the
        # submission neither caused nor can fix. So the log has to be silent
        # about failure for the disagreement to mean what it claims.
        log_reports_failure = any(v != "PASS" for v in outcomes.values())
        if f2p and len(hit) == len(f2p) and target_code != 0 and not log_reports_failure:
            write_reward(args.logs, 0.0, "log-and-exit-status-disagree")
            print("every target parsed as passing, the runner exited "
                  + str(target_code) + ", and the log reports nothing failing; "
                  "the log is not describing this run")
            return 1
        # Identity. The submission handed to this verifier must belong to the
        # repository this bundle grades. Eight rollouts ran concurrently into one
        # shared output tree and the collect step walked all of it, so a bundle's
        # deliverable received a sibling's trajectory: linkerd2's directory
        # carried tfsec's output.jsonl, telepresence's carried mem0's patch, and
        # encore's carried linkerd2's. Scored blind, a mismatched patch that
        # happened to apply would produce a number that looked entirely real.
        #
        # Checked here rather than in the runner because the runner is not the
        # only thing that can invoke a verifier, and a check that lives outside
        # the bundle is one a re-score or a third party can skip. The test is
        # simply whether the paths the submission edits exist in the tree being
        # graded: a patch from another repository names files this one does not
        # have.
        # Patch-to-repo is the primary identity assertion, not a fallback.
        # `output.jsonl`'s instance_id cannot carry this: 11 of 13 collected runs
        # in this batch record no instance_id at all, so an identity check keyed
        # on it has nothing to read and silently degrades to trusting position.
        # The separation this gives is absolute where it was measured -- every
        # genuine pairing matched at least 73% of its repository's paths and the
        # one foreign submission matched 0 of 7.
        #
        # Only paths the submission MODIFIES are evidence. A patch may create
        # files, and a created file is legitimately absent from the base tree, so
        # counting additions would refuse an honest submission that only adds.
        modified = [p for p in diff_paths(submission_diff, modified_only=True) if p]
        if modified:
            foreign = [p for p in modified if not os.path.exists(os.path.join(repo_dir, p))]
            if len(foreign) == len(modified):
                write_reward(args.logs, 0.0, "submission-belongs-to-another-repository")
                print("none of the " + str(len(modified)) + " path(s) this submission modifies "
                      "exist in " + cfg["repo"] + " at " + repo_dir + ", so the trajectory being "
                      "graded was produced against a different task. First: " + foreign[0]
                      + ". Grading it would report a number about the wrong repository.")
                return 1

        diff_out = submission_diff

        # The preserve command runs the preserve set and nothing else. Running the
        # whole suite instead makes the verifier pay the full timeout for every
        # package the preserve set already excludes, which on a repository with
        # network-dependent tests and a no-network policy is most of the wall
        # clock and none of the signal.
        preserve_cmd = cfg["preserve_cmd"]
        if cfg.get("preserve_args_file"):
            preserve_cmd = preserve_cmd + " $(cat " + cfg["preserve_args_file"] + ")"
        preserve_code, preserve_out = run(preserve_cmd, repo_dir)
        preserve_source = collect_reports(repo_dir, report_globs) if report_globs else preserve_out
        preserve_outcomes = parser(preserve_source)
        with open(os.path.join(args.logs, "preserve-stdout.md"), "w", encoding="utf-8") as h:
            h.write(preserve_out)
        preserve_resolved, preserve_ambiguous, preserve_unseen = resolve_declared(
            p2p, preserve_outcomes)
        # Prove the preserve command ran the preserve set. Unproven, `broken` is
        # empty for the same reason `hit` was zero and the regression channel is
        # inert: a submission that broke every preserved test reports exactly
        # what a clean one reports. Measured on dozzle, whose preserve command
        # carried no package arguments and so tested only the repository root:
        # one line of output, zero parsed keys, zero of 206 declared ids matched,
        # preserve_broken 0.
        if p2p and len(preserve_unseen) == len(p2p):
            write_reward(args.logs, 0.0, "preserve-set-did-not-execute",
                         {"preserve_total": len(p2p), "preserve_matched": 0,
                          "parsed_keys": len(preserve_outcomes)})
            print("none of the " + str(len(p2p)) + " preserved test(s) appear in the preserve "
                  "run's output, so no regression could have been detected and a reward here "
                  "would mean nothing. Parsed keys: " + str(len(preserve_outcomes)))
            return 1
        if p2p and len(preserve_resolved) * 100 < len(p2p) * PRESERVE_COVERAGE_FLOOR:
            write_reward(args.logs, 0.0, "preserve-set-underexecuted",
                         {"preserve_total": len(p2p),
                          "preserve_matched": len(preserve_resolved),
                          "preserve_floor_pct": PRESERVE_COVERAGE_FLOOR})
            print("the preserve run accounted for only " + str(len(preserve_resolved))
                  + " of " + str(len(p2p)) + " preserved test(s), below the "
                  + str(PRESERVE_COVERAGE_FLOOR) + "% floor; the regression channel is not "
                  "measuring what it claims to")
            return 1
        broken = [t for t in p2p if preserve_resolved.get(t) == "FAIL"]

        if broken:
            reward, reason = 0.0, "preserve-set-regression"
        else:
            reward = (len(hit) + len(extra_hit)) / float(len(f2p) + len(extra))
            reason = "graded" if reward > 0 else "no-target-resolved"
        changed_files = len([l for l in diff_out.splitlines() if l.startswith("diff --git ")])
        _final_counts = {"targets_total": len(f2p) + len(extra), "targets_resolved": len(hit) + len(extra_hit),
                         "targets_matched": len(resolved) + len(extra_resolved),
                         "f2p_total": len(f2p), "f2p_resolved": len(hit),
                         "n2p_total": len(extra), "n2p_resolved": len(extra_hit),
                         "n2p_matched": len(extra_resolved),
                         "preserve_total": len(p2p), "preserve_broken": len(broken),
                         "preserve_matched": len(preserve_resolved)}
        with open(os.path.join(args.logs, "summary.json"), "w", encoding="utf-8") as h:
            json.dump({"targets_total": len(f2p) + len(extra), "targets_resolved": len(hit) + len(extra_hit),
                       "targets_matched": len(resolved) + len(extra_resolved),
                       "f2p_total": len(f2p), "f2p_resolved": len(hit),
                       "n2p_total": len(extra), "n2p_resolved": len(extra_hit),
                       "n2p_matched": len(extra_resolved),
                       "preserve_total": len(p2p), "preserve_broken": len(broken),
                       "preserve_matched": len(preserve_resolved),
                       "parsed_keys": len(outcomes),
                       "changed_files": changed_files,
                       "diff_bytes": len(diff_out)}, h, sort_keys=True)
            h.write("\n")
        print("targets resolved " + str(len(hit) + len(extra_hit)) + " of " + str(len(f2p) + len(extra))
              + " (f2p " + str(len(hit)) + " of " + str(len(f2p)) + ", n2p " + str(len(extra_hit))
              + " of " + str(len(extra)) + ")"
              + ", preserve regressions " + str(len(broken))
              + ", files changed " + str(changed_files))
    except Exception as exc:  # a runner that cannot decide scores zero, never full
        reason = "runner-exception"
        print("runner exception: " + repr(exc), file=sys.stderr)
    finally:
        # Only write the fallback when nothing decided. Every early refusal
        # already wrote its own specific reason, and overwriting it here
        # replaced each of them with a generic one: a verifier that refused for
        # a precise, machine-readable cause reported that it merely did not
        # finish. The value was right and the explanation was destroyed.
        if not _REWARD_WRITTEN:
            write_reward(args.logs, reward, reason, _final_counts)
    return 0 if reward >= 1.0 else 1


if __name__ == "__main__":
    sys.exit(main())
