import socket
import threading
from datetime import datetime, timezone
from rpc_common import send_msg, recv_msg

HOST = "0.0.0.0"
PORT = 13003

print(f"RPC server on {HOST}:{PORT}")

# Function registry

def add(a, b):
    return a + b

def mul(a, b):
    return a * b

def echo(x):
    return x

def time_now():
    return datetime.now(timezone.utc).isoformat()

FUNCS = {
    "add": add,
    "mul": mul,
    "echo": echo,
    "time": time_now,
}

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((HOST, PORT))
srv.listen(50)


def handle(conn: socket.socket, addr):
    with conn:
        print("RPC connected:", addr)
        try:
            while True:
                try:
                    req = recv_msg(conn)
                except ConnectionError:
                    break
                if not isinstance(req, dict):
                    send_msg(conn, {"ok": False, "error": "bad request", "data": None})
                    continue
                name = str(req.get("call", ""))
                args = req.get("args", [])
                kwargs = req.get("kwargs", {})
                fn = FUNCS.get(name)
                if not fn:
                    send_msg(conn, {"ok": False, "error": f"unknown function: {name}", "data": None})
                    continue
                try:
                    res = fn(*args, **kwargs)
                    send_msg(conn, {"ok": True, "data": res, "error": None})
                except Exception as e:
                    send_msg(conn, {"ok": False, "error": str(e), "data": None})
        finally:
            print("RPC closed:", addr)

while True:
    c, a = srv.accept()
    threading.Thread(target=handle, args=(c, a), daemon=True).start()
