# syntax=docker/dockerfile:1
# Separate verifier environment for reflex-dev/reflex at 977cc6990f22.
#
# Derived from the agent image, pinned by digest, so the verifier holds the same
# toolchain and the same already-resolved dependency cache the agent had. That
# matters more than it looks: grading runs with no network, so a verifier built
# from a bare base would fail every target on a dependency fetch and report a
# reward of zero that has nothing to do with the submission.
#
# It is still a separate environment. The image is separate, its filesystem is
# separate, and it adds only the grading interpreter, so nothing the agent wrote
# can reach the tool that grades it. The verifier never downloads a toolchain
# while grading, because the published attack against this task family replaces
# exactly such a fetched tool.
#
# Build order is agent image first, then this one. The agent image is referenced
# by tag here because a locally built image has no registry manifest digest and
# `FROM tag@sha256:...` asks a registry to resolve one. The exact image this tag
# must resolve to is recorded as [environment].docker_image in task.toml, so the
# pin is still checkable: build the agent image, read back its identifier, and
# compare it against the manifest.
#
# Expected agent image identifier: sha256:844744ef3ba7a2bf175f3f4446cfc4d26324deea3276dddc3570263e0e1926d7
FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/rfp-coding-q1-tag-levi/reflex-dev_m_reflex@sha256:eca2d8710d1baffad6f1d273610bbce183857c73bed6574dce2252fb3fb446aa

ENV DEBIAN_FRONTEND=noninteractive
# The grading interpreter is installed only when the agent image lacks one. An image on an
# archived Debian suite answers apt with 404, which killed the verifier build for a
# telepresence image that already carried /usr/bin/python3.
RUN command -v python3 >/dev/null 2>&1 \
 || (apt-get update \
 && apt-get install -y --no-install-recommends python3 \
 && rm -rf /var/lib/apt/lists/*)

COPY . /tests
WORKDIR /tests
