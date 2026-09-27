#!/bin/bash
set -euo pipefail

cd "/home/mise"
git config --global --add safe.directory "/home/mise" || true
git apply --whitespace=nowarn /solution/fix.patch
git add -A
git -c user.email=oracle@trinity.invalid -c user.name="Trinity Oracle" \
    commit -q --no-verify -m "reference solution" || true
