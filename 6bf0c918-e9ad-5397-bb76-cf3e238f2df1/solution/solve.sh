#!/bin/bash
# Executable oracle. Applies the reference solution and commits it, because a test
# suite that inspects the working tree must see a clean one.
# FORGE canary block. Derived from the canonical content hash.
# FORGE-CANARY[00]=24553901DC6282770870EDB77847B933
# FORGE-CANARY[01]=E5E6C24D72D8532B145FBBE50F827476
# FORGE-CANARY[02]=A95995746EB340C766897008A27FF7FC
# FORGE-CANARY[03]=8042888AF71769D13D156A4A17FF2E7A
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
