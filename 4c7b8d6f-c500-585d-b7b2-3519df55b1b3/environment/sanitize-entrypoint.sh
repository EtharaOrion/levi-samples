#!/bin/sh
rm -f /home/fix.patch /home/test.patch /home/prepare.sh /home/run.sh /home/test-run.sh /home/fix-run.sh /home/run_tests.sh /home/check_git_changes.sh 2>/dev/null || true
rm -rf /ctx 2>/dev/null || true
if [ "$#" -eq 0 ]; then
  exec /bin/bash
fi
exec "$@"
