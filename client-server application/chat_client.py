import socket
import threading
import sys
from common import send_msg, recv_msg

HOST = "127.0.0.1"
PORT = 12346


def receiver(sock: socket.socket):
    try:
        while True:
            try:
                msg = recv_msg(sock)
            except (socket.timeout, TimeoutError):
                continue  # keep waiting for messages
            if not isinstance(msg, dict):
                continue
            t = msg.get("type")
            if t == "system":
                print(f"\r[*] {msg.get('text')}\n>> ", end="", flush=True)
            elif t == "msg":
                sender = msg.get("from", "?")
                text = msg.get("text", "")
                print(f"\r{sender}: {text}\n>> ", end="", flush=True)
    except Exception as e:
        print(f"\r[Disconnected: {e}]", flush=True)


def main():
    name = input("Enter your name: ").strip() or "anonymous"
    try:
        with socket.create_connection((HOST, PORT)) as sock:
            sock.settimeout(3600)
            send_msg(sock, {"type": "join", "name": name})
            t = threading.Thread(target=receiver, args=(sock,), daemon=True)
            t.start()
            while True:
                try:
                    line = input(">> ")
                except (EOFError, KeyboardInterrupt):
                    break
                if not line:
                    continue
                if line.strip().lower() in {"/quit", "/exit"}:
                    send_msg(sock, {"type": "quit"})
                    break
                send_msg(sock, {"type": "msg", "text": line})
    except ConnectionRefusedError:
        print("Chat server not running. Start chat_server.py first.")
        sys.exit(1)


if __name__ == "__main__":
    main()
