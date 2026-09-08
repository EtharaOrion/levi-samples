#!/bin/bash
set -euo pipefail

# V-003: pytest-flask defaults SERVER_NAME to the literal "localhost.localdomain"
# and the tests self-fetch via url_for(_external=True), so that name must resolve
# under network_mode = "none". Must live here, not in the Dockerfile: Docker
# regenerates /etc/hosts per container, so a RUN layer cannot reach runtime.
# Loopback alias only; opens no network.
if ! getent hosts localhost.localdomain >/dev/null 2>&1; then
    echo "127.0.0.1 localhost.localdomain" >> /etc/hosts
fi

# V-005: start the loopback NXDOMAIN resolver before pytest. Without a reachable
# resolver, glibc reports EAI_AGAIN ("Temporary failure in name resolution");
# graded tests assert the EAI_NONAME text ("Name or service not known") that a
# reachable resolver returns for a genuinely nonexistent name. See
# tests/hermetic_seal.py. No content is fabricated and no network is opened.
/opt/python/bin/python3 /tests/hermetic_seal.py &
for _ in $(seq 1 50); do
    [ -e /tmp/.hermetic_seal_ready ] && break
    sleep 0.1
done
if [ ! -e /tmp/.hermetic_seal_ready ]; then
    echo "hermetic seal failed to start" >&2
    exit 1
fi

# V-006: loopback stand-in for the changedetection.io share/content endpoints, so
# the share round trip and the first-fetch-succeeds precondition hold offline.
# See tests/hermetic_fixtures.py. Binds 127.0.0.1 only.
/usr/local/bin/python3 /tests/hermetic_fixtures.py &
for _ in $(seq 1 50); do
    [ -e /tmp/.hermetic_fixtures_ready ] && break
    sleep 0.1
done
if [ ! -e /tmp/.hermetic_fixtures_ready ]; then
    echo "hermetic fixtures failed to start" >&2
    exit 1
fi

/opt/python/bin/python3 /tests/run_tests.py --config /tests/config.json --log-dir /logs/verifier
