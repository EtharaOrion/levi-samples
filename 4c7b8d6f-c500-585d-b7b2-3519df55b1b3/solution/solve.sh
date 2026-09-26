#!/bin/bash
# Executable oracle. Applies the reference solution and commits it, because a test
# suite that inspects the working tree must see a clean one.
set -euo pipefail

cd "/home/mise"
# The workspace may be bind-mounted, in which case its ownership differs from the
# running user and git refuses to touch it. Declaring it safe is not a relaxation of
# anything the policy manifest denies: it is what makes the oracle behave the same
# whether the tree lives in the image or is mounted into it.
git config --global --add safe.directory "/home/mise" || true
git apply --whitespace=nowarn /solution/fix.patch
git add -A
git -c user.email=oracle@trinity.invalid -c user.name="Trinity Oracle" \
    commit -q --no-verify -m "reference solution" || true
