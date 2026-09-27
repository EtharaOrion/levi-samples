#!/bin/bash
# Runs the bundle's own grader (tests/levi_grader). Always exits 0: the trial
# result is /logs/verifier/reward.json (scored) or invalid.json.
set -u
# Agent code can plant importable modules in the repo or in /: run from / with -P
# so python never imports from the cwd.
cd / || exit 0
out=/logs/verifier
mkdir -p "$out"
rm -f "$out/reward.json" "$out/reward.txt" "$out/invalid.json" "$out/grading.json"

PYTHONPATH=/tests python3 -P -m levi_grader --tests-dir /tests --out-dir "$out"
rc=$?

# After a crash anything in $out may be planted, so it is discarded.
if [ "$rc" -ne 0 ] || { [ ! -f "$out/reward.json" ] && [ ! -f "$out/invalid.json" ]; }; then
  rm -f "$out/reward.json" "$out/reward.txt" "$out/grading.json"
  printf '{"schema_version": "levi-invalid/1", "reason": "grader_crashed", "stage": "test.sh", "detail": "levi_grader exited %s"}\n' "$rc" > "$out/invalid.json"
fi
if [ -f "$out/invalid.json" ]; then rm -f "$out/reward.json" "$out/reward.txt"; fi
exit 0
