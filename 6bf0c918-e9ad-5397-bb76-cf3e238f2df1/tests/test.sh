#!/bin/bash
set -uo pipefail

REWARD_DIR=/logs/verifier
mkdir -p "$REWARD_DIR"
printf '{"reward":0.0}\n' > "$REWARD_DIR/reward.json"
printf '0.000000\n' > "$REWARD_DIR/reward.txt"
printf '{"reason":"verifier-did-not-complete","reward":0.0}\n' > "$REWARD_DIR/reward_reason.json"

python3 /tests/run_tests.py --config /tests/config.json --logs "$REWARD_DIR"
