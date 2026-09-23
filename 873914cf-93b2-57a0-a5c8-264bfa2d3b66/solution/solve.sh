#!/bin/bash
# Executable oracle. Applies the reference solution and commits it, because a test
# suite that inspects the working tree must see a clean one.
# FORGE canary block. Derived from the canonical content hash.
# FORGE-CANARY[00]=E553CE85A6EB1F7D4A7659959DEDB7A0
# FORGE-CANARY[01]=A9641C2DD6753F65E328BF2EBA5300DC
# FORGE-CANARY[02]=31FE7C963D6FB908C38453B641ADF0E7
# FORGE-CANARY[03]=3B134102F505CD43087B73B2BFADFFCF
set -euo pipefail

cd "/home/reflex"
# The workspace may be bind-mounted, in which case its ownership differs from the
# running user and git refuses to touch it. Declaring it safe is not a relaxation of
# anything the policy manifest denies: it is what makes the oracle behave the same
# whether the tree lives in the image or is mounted into it.
git config --global --add safe.directory "/home/reflex" || true
git apply --whitespace=nowarn /solution/fix.patch
git add -A
git -c user.email=oracle@trinity.invalid -c user.name="Trinity Oracle" \
    commit -q --no-verify -m "reference solution" || true
