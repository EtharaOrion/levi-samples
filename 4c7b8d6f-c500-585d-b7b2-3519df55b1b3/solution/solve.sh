#!/bin/bash
# Executable oracle. Applies the reference solution and commits it, because a test
# suite that inspects the working tree must see a clean one.
# FORGE canary block. Derived from the canonical content hash.
# FORGE-CANARY[00]=B0DA1BB6B34BE74C93CD24280FEE65D6
# FORGE-CANARY[01]=8586660CB375ACFF276580D9DBA47D08
# FORGE-CANARY[02]=120499FC16D16514990912FCD40AF63E
# FORGE-CANARY[03]=BD5FA149AC965B38CFB3268C11D80B60
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
