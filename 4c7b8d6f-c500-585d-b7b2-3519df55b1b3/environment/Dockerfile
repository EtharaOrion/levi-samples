# syntax=docker/dockerfile:1
# Sanitized agent environment for jdx/mise at e26b4e78d939.
#
# Derived from 426628337772.dkr.ecr.ap-south-1.amazonaws.com/rfp-coding-q1-tag-milo/jdx_m_mise:pr-8524@sha256:df61963482812a1239195f25326ea9b385012c74ed79acc73cf41d3f59f5bc27, which is the image the targets were measured on.
# The measured image cannot be the delivered one. The evaluator plants the
# reference fix at /home/fix.patch and the reference tests at /home/test.patch in
# every image it builds, and it clones the upstream repository in a layer below
# the one its hardening block purges, so the original pack ships under a whiteout
# with every post-base commit still in it. Both are surviving artefacts in the
# agent-facing delivery closure.
#
# Three things happen here and the order matters.
#
# The evaluator's planted files leave first. The rule is structural rather than a
# list: every regular file directly under /home goes, because that is where every
# repository module writes its patches and scripts and the repository itself is a
# directory. The named set is then asserted absent, so a module that plants a
# name this project has not seen is still removed and the named ones are still
# proven gone.
#
# The repository's git is then rebuilt rather than cleaned. `rm -rf .git` and a
# fresh `git init` leave no upstream object to miss, which a purge cannot promise:
# the evaluator's own purge asserts `git rev-list --all --count` equals
# `git rev-list HEAD --count` and passes while 276 to 11351 post-base commits sit
# one layer down. The commit identity and date are fixed, so the derived image is
# the same image on any host and at any time.
#
# The result is then flattened onto scratch. Everything above happened in a build
# stage, so the layers that held the patches, the scripts and the original pack
# are not part of this image at all. A deletion in a later layer only changes the
# merged view; not shipping the layer is what makes the bytes absent.
#
# Flattening resets the image configuration, so every value 426628337772.dkr.ecr.ap-south-1.amazonaws.com/rfp-coding-q1-tag-milo/jdx_m_mise:pr-8524@sha256:df61963482812a1239195f25326ea9b385012c74ed79acc73cf41d3f59f5bc27 declared
# is restated below. Restated here they are bundle bytes under
# canonical_content_hash, which means the environment is recomputable from the
# bundle rather than taken on trust from whatever this host inspected.
FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/rfp-coding-q1-tag-milo/jdx_m_mise:pr-8524@sha256:df61963482812a1239195f25326ea9b385012c74ed79acc73cf41d3f59f5bc27 AS unsanitized

COPY sanitize-entrypoint.sh /usr/local/bin/forge-sanitize-entrypoint.sh

# 1. The planted artefacts leave the image, and the named ones are proven gone.
RUN set -eux; \
    chmod 0755 /usr/local/bin/forge-sanitize-entrypoint.sh; \
    find /home -maxdepth 1 -type f -delete; \
    rm -f /home/fix.patch /home/test.patch /home/prepare.sh /home/run.sh /home/test-run.sh /home/fix-run.sh /home/run_tests.sh /home/check_git_changes.sh; \
    rm -rf /ctx; \
    for f in /home/fix.patch /home/test.patch /home/prepare.sh /home/run.sh /home/test-run.sh /home/fix-run.sh /home/run_tests.sh /home/check_git_changes.sh /ctx; do test ! -e "$f"; done

WORKDIR /home/mise

# 1b. Dependency closure, sealed at build time with the network up.
#
#     The span's fix edits a dependency manifest, the verifier re-resolves during
#     grading, and grading runs under network_mode none. Resolving here is what
#     makes the graded run possible offline. This is the cd-594 V-004 touchstone
#     pattern, and it previously lived in a levi-repair image on the authoring
#     host, which meant the closure shipped with that host rather than with this
#     bundle. It is bundle bytes now: `manifests.patch` sits beside this file,
#     every step below is inside canonical_content_hash, and a consumer holding
#     the pinned base recomputes the same closure from `environment/` alone.
#
#     Nothing below runs at verification time and no network path reaches the
#     verifier. The manifests are applied to a throwaway copy and the tree the
#     verifier sees is still the unmodified base; what survives is a warmed cache.
COPY manifests.patch /ctx/manifests.patch
RUN set -x; (cargo fetch --locked || cargo fetch || true) && \
    (rm -rf /tmp/_scratch && cp -a . /tmp/_scratch && (cd /tmp/_scratch && (git apply --3way /ctx/manifests.patch 2>/dev/null || git apply /ctx/manifests.patch 2>/dev/null || echo 'fix manifests did not apply') && cargo fetch --locked || cargo fetch || true) ; rm -rf /tmp/_scratch) && \
    (git -C . reset -q -- . 2>/dev/null; git -C . checkout -- . 2>/dev/null; for f in $(git apply --summary /ctx/manifests.patch 2>/dev/null | awk '/create mode/ {print $NF}'); do git ls-files --error-unmatch "$f" >/dev/null 2>&1 || rm -f "$f"; done; true) && \
    (git -C . status --porcelain | head -20)
RUN rm -rf /ctx && test ! -e /ctx

# 1c. Agent runtime, baked at build time so run time needs only the model endpoint.
#
#     Harbor installs the openhands-sdk agent INSIDE the task environment and drives it
#     with environment.exec, so the agent's own install would run under the declared
#     [agent] network policy. That install fetches the uv installer from astral.sh, a
#     Python interpreter from uv's download service, and three packages from PyPI. Under
#     an allowlist scoped to the model endpoint it fails before any reasoning happens,
#     and widening the allowlist to cover PyPI and a Python CDN would hand the agent the
#     open internet for the whole run.
#
#     Baking it here moves that fetch to build time, which has network by design, exactly
#     as the dependency closure above does. Harbor then skips the install: its
#     already_installed probe is `[ -f /opt/openhands-sdk-venv/bin/python ] &&
#     /opt/openhands-sdk-venv/bin/python -c "import openhands.sdk"`. It also calls
#     ensure_system_dependencies(("curl","coreutils")) unconditionally, even for a
#     pre-baked image, but that step short-circuits without touching a package manager
#     when `command -v curl` and `command -v stdbuf` both succeed, so both are asserted
#     present below rather than assumed.
#
#     The version is pinned so the runtime is reproducible, and the import is proven with
#     the network off at build time, so a consumer learns here rather than mid-rollout
#     that the runtime cannot start.
# Harbor probes `command -v curl` and `command -v stdbuf` and, when either is missing, calls
# the distro package manager at RUN time. Under the bound allowlist that fails and the agent
# never starts. Three of this batch's bases ship no stdbuf, so both are installed here at
# build time where network is allowed, rather than left to a run-time apt-get that cannot run.
RUN set -eux; \
    if ! command -v curl >/dev/null || ! command -v stdbuf >/dev/null; then \
      if command -v apt-get >/dev/null; then \
        apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y curl coreutils; \
      elif command -v dnf >/dev/null; then dnf install -y curl coreutils; \
      elif command -v yum >/dev/null; then yum install -y curl coreutils; \
      elif command -v apk >/dev/null; then apk add --no-cache curl coreutils; \
      else echo "no supported package manager for curl/coreutils" >&2; exit 1; fi; \
    fi

# uv comes from one pinned release, verified by sha256 before it runs, rather than from the
# astral.sh installer, which fetches whatever release is latest and so made two builds of the
# same bundle bytes install different uv. The musl build is used on both architectures because
# the glibc x86_64 build segfaults on every call under QEMU user emulation, which is how the
# linux/amd64 half of the pushed index is built on an arm64 host; the musl build runs there and
# natively alike.
RUN set -eux; \
    case "$(uname -m)" in \
      x86_64) uv_target=x86_64-unknown-linux-musl; uv_sha256=6401c4665d8fa2a9893e087c91f585430738e3170f5398a1141483efb4a93310 ;; \
      aarch64) uv_target=aarch64-unknown-linux-musl; uv_sha256=a6096da273d548cb9f277d237a01ac7344a39ef0f455c0e148e4dc9737c1596b ;; \
      *) echo "no pinned uv for $(uname -m)" >&2; exit 1 ;; \
    esac; \
    curl -fsSL -o /tmp/uv.tar.gz "https://github.com/astral-sh/uv/releases/download/0.12.17/uv-${uv_target}.tar.gz"; \
    echo "${uv_sha256}  /tmp/uv.tar.gz" | sha256sum -c -; \
    mkdir -p "$HOME/.local/bin"; \
    tar -xzf /tmp/uv.tar.gz -C /tmp; \
    install -m 0755 "/tmp/uv-${uv_target}/uv" "/tmp/uv-${uv_target}/uvx" "$HOME/.local/bin/"; \
    rm -rf /tmp/uv.tar.gz "/tmp/uv-${uv_target}"; \
    export PATH="$HOME/.local/bin:$PATH"; \
    uv --version; \
    uv python install 3.12; \
    uv venv /opt/openhands-sdk-venv --python 3.12 --clear; \
    . /opt/openhands-sdk-venv/bin/activate; \
    uv pip install openhands-sdk==1.49.1 openhands-tools==1.49.1 fastapi; \
    deactivate

# The three conditions Harbor probes, asserted rather than assumed. A failure here fails
# the build; the alternative is an agent that cannot start once the network is closed.
RUN set -eux; \
    test -f /opt/openhands-sdk-venv/bin/python; \
    command -v curl >/dev/null; \
    command -v stdbuf >/dev/null; \
    /opt/openhands-sdk-venv/bin/python -c "import openhands.sdk; print('openhands.sdk', openhands.sdk.__version__)"

# 2. The repository's history is rebuilt as one parentless commit over the tree
#    the measurement ran against.
#    `core.logAllRefUpdates false` and the removal of .git/logs are not tidying.
#    A reflog is a second record of where a ref has been, and an instrument that
#    accepts one because "it only holds the commit we just made" has accepted the
#    argument that a reflog is sometimes fine. It never is here: the closure
#    claims reflog absence, so the reflog is absent.
RUN set -eux; \
    rm -rf .git; \
    git init -q .; \
    git config --local user.name "Initial State"; \
    git config --local user.email "author@localhost"; \
    git config --local commit.gpgsign false; \
    git config --local gc.auto 0; \
    git config --local core.logAllRefUpdates false; \
    git add -A; \
    for p in 'e2e-win/npm_backend.Tests.ps1' 'e2e/backend/test_aqua_cosign' 'e2e/backend/test_backend_missing_deps' 'e2e/backend/test_dev_version_filter' 'e2e/backend/test_github_filter_bins' 'e2e/backend/test_github_tool_alias_asset_pattern' 'e2e/backend/test_npm_package_manager' 'e2e/cli/test_env_flag_forms' 'e2e/cli/test_tool_depends' 'e2e/cli/test_watch' 'e2e/cli/test_zsh_precmd_runs_once' 'e2e/config/test_config_ignore' 'e2e/core/test_dotnet' 'e2e/core/test_node_slow' 'e2e/core/test_rust' 'e2e/core/test_swift_slow' 'e2e/env/test_fish_path_move_bug' 'e2e/env/test_zsh_consecutive_precmd_runs' 'e2e/env/test_zsh_first_precmd_after_activate' 'e2e/generate/test_generate_bootstrap' 'e2e/helpers.sh' 'e2e/lockfile/test_lockfile_lock_filtered_prune_stale_versions' 'e2e/lockfile/test_lockfile_lock_unfiltered_prune_stale_versions' 'e2e/lockfile/test_lockfile_provenance' 'e2e/lockfile/test_lockfile_python' 'e2e/plugins/test_plugin_link' 'e2e/run_all_tests' 'e2e/run_test' 'e2e/tasks/test_task_dep_args' 'e2e/tasks/test_task_monorepo_file_tasks' 'e2e/tasks/test_task_remote_git_https' 'e2e/tasks/test_task_remote_git_includes' 'e2e/tasks/test_task_remote_git_ssh' 'e2e/tasks/test_tool_versions_trust' 'packaging/e2e/Dockerfile' 'src/config/config_file/snapshots/mise__config__config_file__mise_toml__tests__env_var_in_tool.snap' 'src/config/config_file/snapshots/mise__config__config_file__mise_toml__tests__fixture-3.snap' 'src/config/config_file/snapshots/mise__config__config_file__mise_toml__tests__replace_versions.snap' 'src/shell/snapshots/mise__shell__zsh__tests__activate.snap' 'src/shell/snapshots/mise__shell__zsh__tests__deactivate.snap' 'test/data/plugins/needs-dummy/bin/download' 'test/data/plugins/needs-dummy/bin/install' 'test/data/plugins/needs-dummy/bin/latest-stable' 'test/data/plugins/needs-dummy/bin/list-all'; do \
      if [ -e "$p" ]; then git add -f -- "$p"; fi; \
    done; \
    GIT_AUTHOR_DATE="2000-01-01T00:00:00+00:00" GIT_COMMITTER_DATE="2000-01-01T00:00:00+00:00" \
      git commit -q --no-verify --allow-empty -m "base state of jdx/mise at e26b4e78d939"; \
    rm -rf .git/logs; \
    git config --global --add safe.directory /home/mise

# 5. Assertions, inside the build, so a violation fails it rather than shipping.
#    Every one of these is a property this bundle's sanitization closure claims,
#    and a claim nothing checks is a claim.
RUN set -eux; \
    for p in 'e2e-win/npm_backend.Tests.ps1' 'e2e/backend/test_aqua_cosign' 'e2e/backend/test_backend_missing_deps' 'e2e/backend/test_dev_version_filter' 'e2e/backend/test_github_filter_bins' 'e2e/backend/test_github_tool_alias_asset_pattern' 'e2e/backend/test_npm_package_manager' 'e2e/cli/test_env_flag_forms' 'e2e/cli/test_tool_depends' 'e2e/cli/test_watch' 'e2e/cli/test_zsh_precmd_runs_once' 'e2e/config/test_config_ignore' 'e2e/core/test_dotnet' 'e2e/core/test_node_slow' 'e2e/core/test_rust' 'e2e/core/test_swift_slow' 'e2e/env/test_fish_path_move_bug' 'e2e/env/test_zsh_consecutive_precmd_runs' 'e2e/env/test_zsh_first_precmd_after_activate' 'e2e/generate/test_generate_bootstrap' 'e2e/helpers.sh' 'e2e/lockfile/test_lockfile_lock_filtered_prune_stale_versions' 'e2e/lockfile/test_lockfile_lock_unfiltered_prune_stale_versions' 'e2e/lockfile/test_lockfile_provenance' 'e2e/lockfile/test_lockfile_python' 'e2e/plugins/test_plugin_link' 'e2e/run_all_tests' 'e2e/run_test' 'e2e/tasks/test_task_dep_args' 'e2e/tasks/test_task_monorepo_file_tasks' 'e2e/tasks/test_task_remote_git_https' 'e2e/tasks/test_task_remote_git_includes' 'e2e/tasks/test_task_remote_git_ssh' 'e2e/tasks/test_tool_versions_trust' 'packaging/e2e/Dockerfile' 'src/config/config_file/snapshots/mise__config__config_file__mise_toml__tests__env_var_in_tool.snap' 'src/config/config_file/snapshots/mise__config__config_file__mise_toml__tests__fixture-3.snap' 'src/config/config_file/snapshots/mise__config__config_file__mise_toml__tests__replace_versions.snap' 'src/shell/snapshots/mise__shell__zsh__tests__activate.snap' 'src/shell/snapshots/mise__shell__zsh__tests__deactivate.snap' 'test/data/plugins/needs-dummy/bin/download' 'test/data/plugins/needs-dummy/bin/install' 'test/data/plugins/needs-dummy/bin/latest-stable' 'test/data/plugins/needs-dummy/bin/list-all'; do \
      if [ -e "$p" ] && ! git ls-files --error-unmatch -- "$p" >/dev/null 2>&1; then \
        echo "test-patch path present but untracked: $p" >&2; exit 1; \
      fi; \
    done; \
    test ! -e /home/fix.patch; \
    test ! -e /home/test.patch; \
    test ! -e /ctx; \
    test -z "$(find /home -maxdepth 1 -type f)"; \
    test "$(git rev-list --count HEAD)" = "1"; \
    test "$(git rev-list --all --count)" = "1"; \
    test "$(git cat-file --batch-all-objects --batch-check='%(objecttype)' \
            | grep -c '^commit$')" = "1"; \
    test -z "$(git remote)"; \
    test -z "$(git tag -l)"; \
    test -z "$(git for-each-ref refs/remotes refs/tags refs/replace)"; \
    test "$(git reflog show --all 2>/dev/null | wc -l)" = "0"; \
    test ! -e .git/logs; \
    test "$(git stash list 2>/dev/null | wc -l)" = "0"; \
    test ! -e .git/shallow; \
    test ! -e .git/info/grafts; \
    test ! -e .git/objects/info/alternates; \
    test ! -e .git/FETCH_HEAD; \
    test ! -e .git/ORIG_HEAD; \
    test -z "$(git config --local --get-regexp '^remote\.' || true)"; \
    echo "dependency-closure markers for rust: $(for p in /usr/local/cargo/registry/cache /root/.cargo/registry/cache; do [ -e "$p" ] && echo "$p"; done)"; \
    echo "fix absence, history absence and remote absence asserted"

# 3. One content layer. The stage above is not in this image.
FROM scratch
COPY --from=unsanitized / /

LABEL "org.opencontainers.image.authors"="https://www.ethara.ai/"
LABEL "org.opencontainers.image.description"="jdx/mise Docker image"
LABEL "org.opencontainers.image.source"="https://github.com/jdx/mise"
LABEL "org.opencontainers.image.title"="jdx/mise"
ENV PATH="/usr/local/cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ENV RUSTUP_HOME="/usr/local/rustup"
ENV CARGO_HOME="/usr/local/cargo"
ENV RUST_VERSION="1.88.0"
ENV DEBIAN_FRONTEND="noninteractive"
ENV LANG="C.UTF-8"
ENV TZ="UTC"
ENV http_proxy=""
ENV https_proxy=""
ENV HTTP_PROXY=""
ENV HTTPS_PROXY=""
ENV no_proxy="localhost,127.0.0.1,::1"
ENV NO_PROXY="localhost,127.0.0.1,::1"
ENV SSL_CERT_FILE="/etc/ssl/certs/ca-certificates.crt"
ENV REQUESTS_CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"
ENV CURL_CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"
ENV LC_ALL="C.UTF-8"
WORKDIR /home/mise
# The wrapper deletes the planted artefacts again at container start and then
# execs whatever the source image declared, so the derived image runs the way
# the measured one did. An --entrypoint override skips the wrapper, which is
# why it is the third guard and not the only one.
ENTRYPOINT ["/usr/local/bin/forge-sanitize-entrypoint.sh"]
CMD ["/bin/bash"]
