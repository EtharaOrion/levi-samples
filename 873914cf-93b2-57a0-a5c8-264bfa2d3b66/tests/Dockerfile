# syntax=docker/dockerfile:1
FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/rfp-coding-q1-tag-levi/reflex-dev_m_reflex@sha256:eca2d8710d1baffad6f1d273610bbce183857c73bed6574dce2252fb3fb446aa

ENV DEBIAN_FRONTEND=noninteractive
RUN command -v python3 >/dev/null 2>&1 \
 || (apt-get update \
 && apt-get install -y --no-install-recommends python3 \
 && rm -rf /var/lib/apt/lists/*)

COPY . /tests
WORKDIR /tests
