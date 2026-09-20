import socket

UDP_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind(("", UDP_PORT))

print(f"Listening for UDP broadcasts on port {UDP_PORT}...")

while True:
    data, addr = sock.recvfrom(4096)
    print(f"Received from {addr}: {data.decode()}")
