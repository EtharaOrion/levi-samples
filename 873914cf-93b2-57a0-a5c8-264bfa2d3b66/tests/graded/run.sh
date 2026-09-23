#!/bin/bash
set -eo pipefail
cd /home/reflex
# pytest file paths the PR's test patch touches (tests/ unit suite only;
# top-level integration/ harness tests need a browser and are skipped).
TEST_FILES=$({ grep -E '^diff --git a/tests/' /tests/test.patch     | sed -E 's#^diff --git a/(.+) b/.*#\1#'     | grep -E '\.py$' | grep -vE 'conftest\.py|__init__\.py' | sort -u; } || true)
EXIST=""
for f in $TEST_FILES; do if [ -f "$f" ]; then EXIST="$EXIST $f"; fi; done
if [ -z "$EXIST" ]; then echo "NO_BASELINE_TEST_FILES"; exit 0; fi
python -m pytest $EXIST -v --no-header -rA --tb=line     -p no:cacheprovider --continue-on-collection-errors -o 'addopts=' 2>&1
