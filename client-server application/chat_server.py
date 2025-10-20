import socket
import threading
from datetime import datetime, timezone
from typing import Dict
from common import send_msg, recv_msg

HOST = "0.0.0.0"
PORT = 12346  # chat runs on a different port from the RPC demo

clients: Dict[socket.socket, str] = {}
clients_lock = threading.Lock()


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def broadcast(payload, exclude=None):
    to_remove = []
    with clients_lock:
        for conn in list(clients.keys()):
            if exclude is not None and conn is exclude:
                continue
            try:
                send_msg(conn, payload)
            except Exception:
                to_remove.append(conn)
        for c in to_remove:
            try:
                clients.pop(c, None)
                c.close()
            except Exception:
                pass


def handle_client(conn: socket.socket, addr):
    name = None
    try:
        # Expect a join message first
        hello = recv_msg(conn)
        if not isinstance(hello, dict) or hello.get("type") != "join":
            return
        name = str(hello.get("name", "anonymous")).strip() or "anonymous"
        print(f"JOIN {addr} as {name}")
        with clients_lock:
            clients[conn] = name
        broadcast({"type": "system", "text": f"{name} joined", "ts": now_utc_iso()}, exclude=None)
        # Receive chat messages
        while True:
            msg = recv_msg(conn)
            if not isinstance(msg, dict):
                continue
            mtype = msg.get("type")
            if mtype == "msg":
                text = str(msg.get("text", ""))
                print(f"MSG from {name}@{addr}: {text}")
                broadcast({
                    "type": "msg",
                    "from": name,
                    "text": text,
                    "ts": now_utc_iso()
                }, exclude=None)
            elif mtype == "quit":
                break
    except Exception:
        pass
    finally:
        with clients_lock:
            if conn in clients:
                clients.pop(conn, None)
        try:
            conn.close()
        except Exception:
            pass
        if name:
            print(f"LEAVE {addr} ({name})")
            broadcast({"type": "system", "text": f"{name} left", "ts": now_utc_iso()}, exclude=None)


def main():
    print(f"Chat server listening on {HOST}:{PORT}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(100)
    try:
        while True:
            conn, addr = server.accept()
            print(f"Accepted {addr}")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nShutting down chat server...")
    finally:
        with clients_lock:
            for c in list(clients.keys()):
                try:
                    c.close()
                except Exception:
                    pass
            clients.clear()
        server.close()


if __name__ == "__main__":
    main()
