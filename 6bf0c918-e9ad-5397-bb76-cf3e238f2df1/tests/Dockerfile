# syntax=docker/dockerfile:1
FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/levi@sha256:b4d482d8e163d741ac086af764c04daabcd6aee412850fee8a80d8881d90f4ab

ENV DEBIAN_FRONTEND=noninteractive
RUN command -v python3 >/dev/null 2>&1 \
 || (apt-get update \
 && apt-get install -y --no-install-recommends python3 \
 && rm -rf /var/lib/apt/lists/*)

RUN python3 -m pytest --version >/dev/null 2>&1 \
 || python3 -m pip install --no-cache-dir pytest 2>/dev/null \
 || (apt-get update \
 && apt-get install -y --no-install-recommends python3-pytest \
 && rm -rf /var/lib/apt/lists/*)

COPY . /tests
WORKDIR /tests
