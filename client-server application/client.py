import socket
import sys
from common import send_msg, recv_msg

HOST = "127.0.0.1"
PORT = 12345


def demo_sequence(sock: socket.socket) -> None:
    send_msg(sock, {"cmd": "ping"}); print("PING ->", recv_msg(sock))
    send_msg(sock, {"cmd": "echo", "data": {"hello": "world"}}); print("ECHO ->", recv_msg(sock))
    send_msg(sock, {"cmd": "sum", "numbers": [1, 2, 3.5]}); print("SUM ->", recv_msg(sock))


def interactive(sock: socket.socket) -> None:
    print("Type commands (ping | echo <text> | sum <nums...> | quit). Ctrl+C to exit.")
    while True:
        try:
            line = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); return
        if not line: continue
        parts = line.split(); cmd = parts[0].lower()
        if cmd == "ping":
            send_msg(sock, {"cmd": "ping"})
        elif cmd == "echo":
            send_msg(sock, {"cmd": "echo", "data": " ".join(parts[1:])})
        elif cmd == "sum":
            nums = []
            for p in parts[1:]:
                try: nums.append(float(p))
                except: print(f"skip non-number: {p}")
            send_msg(sock, {"cmd": "sum", "numbers": nums})
        elif cmd == "quit":
            send_msg(sock, {"cmd": "quit"}); print(recv_msg(sock)); return
        else:
            print("unknown command"); continue
        try:
            print(recv_msg(sock))
        except Exception as e:
            print("recv error:", e); return


if __name__ == "__main__":
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as sock:
            print(f"Connected to {HOST}:{PORT}")
            demo_sequence(sock)
        with socket.create_connection((HOST, PORT), timeout=5) as sock:
            interactive(sock)
    except ConnectionRefusedError:
        print("Server not running. Start server.py first.")
        sys.exit(1)
