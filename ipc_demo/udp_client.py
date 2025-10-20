import socket
import sys

HOST = "127.0.0.1"
PORT = 13001

print(f"Send UDP to {HOST}:{PORT} (type lines, Ctrl+C to exit)")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    while True:
        try:
            line = input(">> ")
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        sock.sendto(line.encode("utf-8"), (HOST, PORT))
        data, _ = sock.recvfrom(65535)
        print(data.decode("utf-8"))
finally:
    sock.close()
