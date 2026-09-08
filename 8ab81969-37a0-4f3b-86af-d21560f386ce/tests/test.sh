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

/opt/python/bin/python3 /tests/run_tests.py --config /tests/config.json --log-dir /logs/verifier
