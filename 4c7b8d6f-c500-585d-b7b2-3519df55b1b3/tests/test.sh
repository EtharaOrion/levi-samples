#!/bin/bash
# Harbor verifier entry point. Terminates by writing reward bytes at Harbor's
# fixed paths, which are /logs/verifier/reward.json first and
# /logs/verifier/reward.txt second. Harbor prefers the JSON form when both are
# present, and the plural spelling that Harbor's own task template carries in a
# comment does not exist, so a bundle that copied it would score zero silently.
#
# A zero is written before the grader runs and overwritten by the graded value,
# so a grader that dies before deciding leaves a zero with a reason rather than
# an absent file. An unwritten reward file is indistinguishable from a zero the
# grader never computed, and this path refuses to be ambiguous about which it is.
set -uo pipefail

REWARD_DIR=/logs/verifier
mkdir -p "$REWARD_DIR"
printf '{"reward":0.0}\n' > "$REWARD_DIR/reward.json"
printf '0.000000\n' > "$REWARD_DIR/reward.txt"
printf '{"reason":"verifier-did-not-complete","reward":0.0}\n' > "$REWARD_DIR/reward_reason.json"

python3 /tests/run_tests.py --config /tests/config.json --logs "$REWARD_DIR"
