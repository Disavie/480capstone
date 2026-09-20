#!/usr/bin/env python3

import socket
import struct

MCAST_GRP = "239.255.0.1"
UDP_PORT = 5000

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM,
    socket.IPPROTO_UDP
)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind(("", UDP_PORT))

mreq = struct.pack(
    "4sl",
    socket.inet_aton(MCAST_GRP),
    socket.INADDR_ANY
)

sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_ADD_MEMBERSHIP,
    mreq
)

print(f"Listening for multicast on {MCAST_GRP}:{UDP_PORT}...")

while True:
    data, addr = sock.recvfrom(4096)
    print(f"Received from {addr}: {data.decode()}")

