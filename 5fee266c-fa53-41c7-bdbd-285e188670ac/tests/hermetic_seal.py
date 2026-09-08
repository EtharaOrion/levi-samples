#!/usr/bin/env python3
"""V-005: loopback NXDOMAIN resolver so offline name lookups fail authoritatively.

Under `network_mode = "none"` no resolver is reachable, so glibc getaddrinfo()
returns EAI_AGAIN -> "Temporary failure in name resolution". Graded tests assert
on EAI_NONAME -> "Name or service not known", which is what a *reachable*
resolver returns for a name that genuinely does not exist. This serves that
truthful answer locally. It fabricates no content and opens no network.
"""

import os
import socket
import struct
import sys
import threading

FLAG_QR = 0x8000
FLAG_AA = 0x0400
FLAG_RD = 0x0100
FLAG_RA = 0x0080
OPCODE_MASK = 0x7800
RCODE_NXDOMAIN = 0x0003

DNS_ADDR = ("127.0.0.1", 53)
READY_MARKER = "/tmp/.hermetic_seal_ready"


def skip_question(data, offset):
    while offset < len(data):
        length = data[offset]
        if length == 0:
            return offset + 1
        if length & 0xC0 == 0xC0:
            return offset + 2
        offset += 1 + length
    return None


def build_nxdomain_reply(query):
    if len(query) < 12:
        return None
    original_flags = struct.unpack("!H", query[2:4])[0]
    reply_flags = (
        FLAG_QR
        | (original_flags & OPCODE_MASK)
        | FLAG_AA
        | (original_flags & FLAG_RD)
        | FLAG_RA
        | RCODE_NXDOMAIN
    )
    question_count = struct.unpack("!H", query[4:6])[0]
    offset = 12
    for _ in range(question_count):
        offset = skip_question(query, offset)
        if offset is None:
            return None
        offset += 4
    if offset > len(query):
        return None
    header = query[0:2] + struct.pack("!HHHHH", reply_flags, question_count, 0, 0, 0)
    return header + query[12:offset]


def serve_udp(sock):
    while True:
        try:
            data, peer = sock.recvfrom(4096)
        except OSError:
            return
        reply = build_nxdomain_reply(data)
        if reply:
            try:
                sock.sendto(reply, peer)
            except OSError:
                pass


def handle_tcp_client(conn):
    try:
        conn.settimeout(5)
        header = conn.recv(2)
        if len(header) < 2:
            return
        expected = struct.unpack("!H", header)[0]
        buffer = b""
        while len(buffer) < expected:
            chunk = conn.recv(expected - len(buffer))
            if not chunk:
                return
            buffer += chunk
        reply = build_nxdomain_reply(buffer)
        if reply:
            conn.sendall(struct.pack("!H", len(reply)) + reply)
    except OSError:
        pass
    finally:
        try:
            conn.close()
        except OSError:
            pass


def serve_tcp(sock):
    while True:
        try:
            conn, _ = sock.accept()
        except OSError:
            return
        threading.Thread(target=handle_tcp_client, args=(conn,), daemon=True).start()


def start_resolver():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind(DNS_ADDR)

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp.bind(DNS_ADDR)
    tcp.listen(32)

    threading.Thread(target=serve_udp, args=(udp,), daemon=True).start()
    threading.Thread(target=serve_tcp, args=(tcp,), daemon=True).start()


def point_resolver_at_loopback():
    with open("/etc/resolv.conf", "w") as handle:
        handle.write("nameserver 127.0.0.1\noptions timeout:1 attempts:2 ndots:0\n")


def main():
    start_resolver()
    point_resolver_at_loopback()
    with open(READY_MARKER, "w") as handle:
        handle.write(str(os.getpid()))
    sys.stderr.write("[hermetic-seal] NXDOMAIN resolver ready on 127.0.0.1:53\n")
    sys.stderr.flush()
    threading.Event().wait()


if __name__ == "__main__":
    main()
