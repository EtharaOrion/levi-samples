FROM debian:bookworm-slim@sha256:88200866dfff7ea7f5cbcb6ec7c8a701889efe6fe859fe64d6990e4b07ea4171 AS python-fetch

# S-002 (partial): pipefail makes the curl|tar pipeline fail loud on curl errors;
# SHA256 verification deferred per user constraint (curl|tar format required).
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

ARG TARGETARCH=amd64

RUN mkdir -p /opt/python && \
    case "${TARGETARCH}" in \
        amd64) ARCH="x86_64-unknown-linux-gnu" ;; \
        arm64) ARCH="aarch64-unknown-linux-gnu" ;; \
        *) echo "Unsupported: ${TARGETARCH}" && exit 1 ;; \
    esac && \
    curl -fsSL "https://github.com/indygreg/python-build-standalone/releases/download/20240107/cpython-3.12.1+20240107-${ARCH}-install_only.tar.gz" \
    | tar -xzC /opt/python --strip-components=1

# ============================================
FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/rfp-coding-q1-tag-milo/reflex-dev_m_reflex:pr-1369@sha256:61da6204b3162f0b9005da880f5d7f295739f93ae5d501dd39d63f1d30206359

USER root

COPY --from=python-fetch /opt/python /opt/python

# marker for language-specific fixes

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        patch \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/* 
    
# V-002: actual SHA injected by converter.py at render time from
# pyproject.toml [tool.uv.sources].multi-swe-bench.rev. The "main" default is
# kept only as a defensive fallback in case the template is invoked manually.
ARG MSB_REF=main
RUN /opt/python/bin/python3 -m pip install --no-cache-dir \
    "multi-swe-bench @ git+https://github.com/Ethara-Ai/multi-swe-bench.git@${MSB_REF}"
    
# Provide a standardized workspace while keeping upstream layout intact
RUN mkdir -p /workspace && \
    ln -sfn /home/reflex /workspace/reflex && \
    git config --global --add safe.directory /home/reflex && \
    git config --global --add safe.directory /workspace/reflex

WORKDIR /workspace/reflex

ENV PYTHONUNBUFFERED=1

