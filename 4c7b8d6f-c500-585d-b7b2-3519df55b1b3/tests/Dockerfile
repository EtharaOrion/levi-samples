# syntax=docker/dockerfile:1
FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/rfp-coding-q1-tag-levi/jdx_m_mise@sha256:8548f5c7004d60da6a8eaca625e5fb7152c40e355eada9a6bdea339b73fff6bf

ENV DEBIAN_FRONTEND=noninteractive
RUN command -v python3 >/dev/null 2>&1 \
 || (apt-get update \
 && apt-get install -y --no-install-recommends python3 \
 && rm -rf /var/lib/apt/lists/*)

COPY . /tests
WORKDIR /tests
