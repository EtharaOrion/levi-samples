#!/bin/bash
set -eo pipefail

cd /home/mise

git checkout HEAD -- .cargo 2>/dev/null || true
cargo --config 'env.INSTA_FORCE_PASS.value="0"' --config 'env.INSTA_FORCE_PASS.force=true' \
      --config 'env.INSTA_UPDATE.value="no"' --config 'env.INSTA_UPDATE.force=true' \
      --config 'env.INSTA_FORCE_UPDATE.value="0"' --config 'env.INSTA_FORCE_UPDATE.force=true' \
      test -- --test-threads=1
