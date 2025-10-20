import socket

HOST = "0.0.0.0"
PORT = 13001

print(f"UDP echo server on {HOST}:{PORT}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

while True:
    data, addr = sock.recvfrom(65535)
    print("UDP from", addr, data)
    sock.sendto(b"echo: " + data, addr)
