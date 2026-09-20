import socket

UDP_PORT = 5000
MESSAGE = b"Hello from UDP broadcast!"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

sock.sendto(MESSAGE, ("255.255.255.255", UDP_PORT))

sock.close()
