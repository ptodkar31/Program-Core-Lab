import socket
import sys

HOST = "127.0.0.1"
PORT = 13000

print(f"Connect TCP to {HOST}:{PORT} (type lines, Ctrl+C to exit)")
try:
    with socket.create_connection((HOST, PORT), timeout=5) as s:
        while True:
            try:
                line = input(">> ")
            except (EOFError, KeyboardInterrupt):
                break
            if not line:
                continue
            s.sendall(line.encode("utf-8") + b"\n")
            data = s.recv(4096)
            if not data:
                print("server closed")
                break
            print(data.decode("utf-8"), end="")
except ConnectionRefusedError:
    print("Server not running. Start tcp_server.py first.")
    sys.exit(1)
