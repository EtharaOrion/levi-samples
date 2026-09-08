#!/usr/bin/env python3
"""V-006: loopback stand-in for the changedetection.io share/content endpoints.

Two graded tests depend on that host being reachable:

  test_notification_errors  needs the first watch fetch to succeed so a history
      entry exists; only then does the second (local) fetch count as a change and
      queue the notification whose delivery failure is what the test asserts. The
      body is never asserted, it only has to differ from the local endpoint.

  test_share_watch  needs the share round trip: POST a watch blob, get a key
      back, GET that key and receive the same blob. The client contract lives in
      __init__.py api_share_put_watch and store.py add_watch. This implements
      exactly that contract and stores nothing but what the app uploaded, so the
      round-trip fidelity the test asserts is the app's own, not invented here.

Serves only 127.0.0.1 and answers only for names mapped to loopback in /etc/hosts.
"""

import json
import os
import ssl
import subprocess
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FIXTURE_HOST = "changedetection.io"
LISTEN_ADDR = ("127.0.0.1", 443)
CERT_DIR = "/tmp/.hermetic_fixture_pki"
READY_MARKER = "/tmp/.hermetic_fixtures_ready"

CHANGELOG_BODY = (
    "changedetection.io changelog\n"
    "0.39.x  hermetic offline fixture body\n"
    "This content exists so the initial watch fetch succeeds.\n"
)

_shared_watches = {}
_lock = threading.Lock()


class FixtureHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_args):
        pass

    def _respond(self, code, body, content_type):
        payload = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/CHANGELOG.txt":
            self._respond(200, CHANGELOG_BODY, "text/plain; charset=utf-8")
            return
        if self.path.startswith("/share/"):
            key = self.path[len("/share/") :]
            with _lock:
                watch = _shared_watches.get(key)
            if watch is None:
                self._respond(404, "{}", "application/json")
                return
            self._respond(200, json.dumps(watch), "application/json")
            return
        self._respond(404, "not found", "text/plain")

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", "replace")
        if self.path == "/share/share":
            watch_json = None
            for pair in raw.split("&"):
                name, _, value = pair.partition("=")
                if name == "watch":
                    from urllib.parse import unquote_plus

                    watch_json = unquote_plus(value)
            if watch_json is None:
                self._respond(400, "{}", "application/json")
                return
            key = uuid.uuid4().hex[:12]
            with _lock:
                _shared_watches[key] = json.loads(watch_json)
            self._respond(200, json.dumps({"share_key": key}), "application/json")
            return
        self._respond(200, "{}", "application/json")


def generate_pki():
    os.makedirs(CERT_DIR, exist_ok=True)
    key = os.path.join(CERT_DIR, "leaf.key")
    cert = os.path.join(CERT_DIR, "leaf.crt")
    config = os.path.join(CERT_DIR, "openssl.cnf")
    with open(config, "w") as handle:
        handle.write(
            "[req]\ndistinguished_name=dn\nx509_extensions=v3\nprompt=no\n"
            "[dn]\nCN=%s\n"
            "[v3]\nbasicConstraints=critical,CA:TRUE\n"
            "subjectAltName=DNS:%s,DNS:*.%s,IP:127.0.0.1\n"
            % (FIXTURE_HOST, FIXTURE_HOST, FIXTURE_HOST)
        )
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-nodes",
            "-keyout",
            key,
            "-out",
            cert,
            "-days",
            "3650",
            "-config",
            config,
        ],
        check=True,
        capture_output=True,
    )
    return key, cert


def trust_certificate(cert_path):
    with open(cert_path) as handle:
        pem = handle.read()
    targets = ["/etc/ssl/certs/ca-certificates.crt"]
    probe = subprocess.run(
        ["/usr/local/bin/python3", "-c", "import certifi;print(certifi.where())"],
        capture_output=True,
        text=True,
    )
    if probe.returncode == 0:
        targets.append(probe.stdout.strip())
    for target in targets:
        if target and os.path.exists(target):
            with open(target, "a") as handle:
                handle.write("\n" + pem)


def map_host_to_loopback():
    with open("/etc/hosts") as handle:
        current = handle.read()
    if (" %s\n" % FIXTURE_HOST) not in current:
        with open("/etc/hosts", "a") as handle:
            handle.write("127.0.0.1 %s\n" % FIXTURE_HOST)


def main():
    key, cert = generate_pki()
    trust_certificate(cert)
    map_host_to_loopback()

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)

    server = ThreadingHTTPServer(LISTEN_ADDR, FixtureHandler)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    with open(READY_MARKER, "w") as handle:
        handle.write(str(os.getpid()))
    sys.stderr.write(
        "[hermetic-fixtures] https://%s ready on 127.0.0.1:443\n" % FIXTURE_HOST
    )
    sys.stderr.flush()
    threading.Event().wait()


if __name__ == "__main__":
    main()
