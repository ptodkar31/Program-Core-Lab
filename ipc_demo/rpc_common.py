import json
import socket
import struct
from typing import Any

HEADER_LEN = 4

def send_msg(sock: socket.socket, obj: Any) -> None:
    data = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    sock.sendall(struct.pack(">I", len(data)) + data)

def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("socket closed")
        buf.extend(chunk)
    return bytes(buf)

def recv_msg(sock: socket.socket) -> Any:
    (length,) = struct.unpack(">I", recv_exact(sock, HEADER_LEN))
    payload = recv_exact(sock, length)
    return json.loads(payload.decode("utf-8"))
