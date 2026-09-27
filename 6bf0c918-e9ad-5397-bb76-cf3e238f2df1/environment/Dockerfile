# syntax=docker/dockerfile:1
FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/rfp-coding-q1-tag-milo/reflex-dev_m_reflex:pr-1891@sha256:060777d77ed2fd5a68721b916e006e9bf699c4064d4f28d92efe2cfa9a2d7596 AS unsanitized

COPY sanitize-entrypoint.sh /usr/local/bin/forge-sanitize-entrypoint.sh

RUN set -eux; \
    chmod 0755 /usr/local/bin/forge-sanitize-entrypoint.sh; \
    find /home -maxdepth 1 -type f -delete; \
    rm -f /home/fix.patch /home/test.patch /home/prepare.sh /home/run.sh /home/test-run.sh /home/fix-run.sh /home/run_tests.sh /home/check_git_changes.sh; \
    rm -rf /ctx; \
    for f in /home/fix.patch /home/test.patch /home/prepare.sh /home/run.sh /home/test-run.sh /home/fix-run.sh /home/run_tests.sh /home/check_git_changes.sh /ctx; do test ! -e "$f"; done

WORKDIR /home/reflex

RUN set -eux; \
    if ! command -v curl >/dev/null || ! command -v stdbuf >/dev/null; then \
      if command -v apt-get >/dev/null; then \
        apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y curl coreutils; \
      elif command -v dnf >/dev/null; then dnf install -y curl coreutils; \
      elif command -v yum >/dev/null; then yum install -y curl coreutils; \
      elif command -v apk >/dev/null; then apk add --no-cache curl coreutils; \
      else echo "no supported package manager for curl/coreutils" >&2; exit 1; fi; \
    fi

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

RUN set -eux; \
    test -f /opt/openhands-sdk-venv/bin/python; \
    command -v curl >/dev/null; \
    command -v stdbuf >/dev/null; \
    /opt/openhands-sdk-venv/bin/python -c "import openhands.sdk; print('openhands.sdk', openhands.sdk.__version__)"

RUN set -eux; \
    rm -rf .git; \
    git init -q .; \
    git config --local user.name "Initial State"; \
    git config --local user.email "author@localhost"; \
    git config --local commit.gpgsign false; \
    git config --local gc.auto 0; \
    git config --local core.logAllRefUpdates false; \
    git add -A; \
    for p in 'integration/test_call_script.py' 'integration/test_event_actions.py' 'integration/test_form_submit.py' 'tests/components/base/test_script.py' 'tests/components/layout/test_foreach.py' 'tests/components/test_component.py' 'tests/test_app.py' 'tests/test_config.py' 'tests/test_event.py' 'tests/test_reflex.py' 'tests/utils/test_format.py' 'tests/utils/test_hosting.py'; do \
      if [ -e "$p" ]; then git add -f -- "$p"; fi; \
    done; \
    GIT_AUTHOR_DATE="2000-01-01T00:00:00+00:00" GIT_COMMITTER_DATE="2000-01-01T00:00:00+00:00" \
      git commit -q --no-verify --allow-empty -m "base state of reflex-dev/reflex at 269334014d4d"; \
    rm -rf .git/logs; \
    git config --global --add safe.directory /home/reflex

RUN set -eux; \
    for p in 'integration/test_call_script.py' 'integration/test_event_actions.py' 'integration/test_form_submit.py' 'tests/components/base/test_script.py' 'tests/components/layout/test_foreach.py' 'tests/components/test_component.py' 'tests/test_app.py' 'tests/test_config.py' 'tests/test_event.py' 'tests/test_reflex.py' 'tests/utils/test_format.py' 'tests/utils/test_hosting.py'; do \
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
    echo "dependency-closure markers for python: $(for p in /home/reflex/.venv/bin/python* /opt/venv/bin/python* /usr/local/lib/python3*/site-packages/*.dist-info /usr/lib/python3*/dist-packages/*.dist-info; do [ -e "$p" ] && echo "$p"; done)"; \
    echo "fix absence, history absence and remote absence asserted"

FROM scratch
COPY --from=unsanitized / /

LABEL "org.opencontainers.image.authors"="https://www.ethara.ai/"
LABEL "org.opencontainers.image.description"="reflex-dev/reflex Docker image"
LABEL "org.opencontainers.image.source"="https://github.com/reflex-dev/reflex"
LABEL "org.opencontainers.image.title"="reflex-dev/reflex"
ENV PATH="/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ENV LANG="C.UTF-8"
ENV GPG_KEY="A035C8C19219BA821ECEA86B64E628F8D684696D"
ENV PYTHON_VERSION="3.10.21"
ENV PYTHON_SHA256="a0da1e72132e950154eca0f6f47d5db828454700de20e5113667940d81e0db04"
ENV DEBIAN_FRONTEND="noninteractive"
ENV PYTHONDONTWRITEBYTECODE="1"
ENV PIP_DISABLE_PIP_VERSION_CHECK="1"
ENV LC_ALL="C.UTF-8"
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
WORKDIR /home/reflex
ENTRYPOINT ["/usr/local/bin/forge-sanitize-entrypoint.sh"]
CMD ["/bin/bash"]
