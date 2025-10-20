import json
import socket
import struct
from typing import Any

HEADER_LEN = 4  # 4-byte big-endian length prefix


def send_msg(sock: socket.socket, obj: Any) -> None:
    data = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    header = struct.pack(">I", len(data))
    sock.sendall(header + data)


def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket closed")
        buf.extend(chunk)
    return bytes(buf)


def recv_msg(sock: socket.socket) -> Any:
    header = recv_exact(sock, HEADER_LEN)
    (length,) = struct.unpack(">I", header)
    payload = recv_exact(sock, length)
    return json.loads(payload.decode("utf-8"))
