import socket
import threading
from datetime import datetime, timezone
from common import send_msg, recv_msg

HOST = "0.0.0.0"
PORT = 12345

print(f"Starting RPC server on {HOST}:{PORT} ...")

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind((HOST, PORT))
server_sock.listen(50)
print("Server listening; press Ctrl+C to stop.")


def now_utc_iso():
    return datetime.now(timezone.utc).isoformat()


def handle_client(conn: socket.socket, addr):
    with conn:
        print(f"Client connected: {addr}")
        try:
            while True:
                try:
                    req = recv_msg(conn)
                except ConnectionError:
                    print(f"Client closed: {addr}")
                    break
                if not isinstance(req, dict):
                    send_msg(conn, {"ok": False, "error": "Invalid request type", "data": None})
                    continue
                cmd = str(req.get("cmd", "")).lower()
                if cmd == "ping":
                    send_msg(conn, {"ok": True, "data": {"pong": True, "ts": now_utc_iso()}, "error": None})
                elif cmd == "echo":
                    send_msg(conn, {"ok": True, "data": req.get("data"), "error": None})
                elif cmd == "sum":
                    nums = req.get("numbers", [])
                    try:
                        total = float(sum(float(x) for x in nums))
                        send_msg(conn, {"ok": True, "data": {"sum": total}, "error": None})
                    except Exception as e:
                        send_msg(conn, {"ok": False, "data": None, "error": f"bad numbers: {e}"})
                elif cmd == "quit":
                    send_msg(conn, {"ok": True, "data": {"bye": True}, "error": None})
                    break
                else:
                    send_msg(conn, {"ok": False, "data": None, "error": f"unknown cmd: {cmd}"})
        except Exception as e:
            print(f"Error with {addr}: {e}")
        finally:
            print(f"Client disconnected: {addr}")


def accept_loop():
    try:
        while True:
            conn, addr = server_sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server_sock.close()


if __name__ == "__main__":
    accept_loop()
