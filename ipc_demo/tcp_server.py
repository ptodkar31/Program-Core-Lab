import socket
import threading

HOST = "0.0.0.0"
PORT = 13000

print(f"TCP echo server on {HOST}:{PORT}")

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((HOST, PORT))
srv.listen(50)


def handle(conn: socket.socket, addr):
    with conn:
        print("TCP connected:", addr)
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                conn.sendall(b"echo: " + data)
        finally:
            print("TCP closed:", addr)


while True:
    c, a = srv.accept()
    threading.Thread(target=handle, args=(c, a), daemon=True).start()
