#!/bin/sh
# Third guard. The build deleted these and asserted them gone, and the flatten
# left the layers that ever held them behind in a build stage. This runs anyway,
# at container start, because a guard that only runs where the last one already
# succeeded protects nothing: it is here for the mount, the bind, the derived
# image and the resurrected layer that no build-time check can see. The pattern
# is the agent server's own, which removes both patches at build time and again
# in its entrypoint.
rm -f /home/fix.patch /home/test.patch /home/prepare.sh /home/run.sh /home/test-run.sh /home/fix-run.sh /home/run_tests.sh /home/check_git_changes.sh 2>/dev/null || true
rm -rf /ctx 2>/dev/null || true
if [ "$#" -eq 0 ]; then
  exec /bin/bash
fi
exec "$@"
