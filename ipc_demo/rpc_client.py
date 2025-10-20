import socket
import sys
from rpc_common import send_msg, recv_msg

HOST = "127.0.0.1"
PORT = 13003


def rpc_call(name, *args, **kwargs):
    with socket.create_connection((HOST, PORT), timeout=5) as s:
        send_msg(s, {"call": name, "args": list(args), "kwargs": kwargs})
        return recv_msg(s)


if __name__ == "__main__":
    # Demo
    print("add ->", rpc_call("add", 2, 3))
    print("mul ->", rpc_call("mul", 6, 7))
    print("echo ->", rpc_call("echo", {"hello": "world"}))
    print("time ->", rpc_call("time"))

    # Interactive
    print("Type: call <name> [args...] | quit")
    while True:
        try:
            line = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line.lower() == "quit":
            break
        parts = line.split()
        if parts[0] != "call" or len(parts) < 2:
            print("usage: call <name> [args...]")
            continue
        name = parts[1]
        # treat remaining tokens as strings; integers if possible
        args = []
        for t in parts[2:]:
            try:
                if "." in t:
                    args.append(float(t))
                else:
                    args.append(int(t))
            except:
                args.append(t)
        print(rpc_call(name, *args))
