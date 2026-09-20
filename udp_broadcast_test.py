#!/usr/bin/env python3

import socket

MCAST_GRP = "239.255.0.1"
UDP_PORT = 5000
MESSAGE = b"Hello from UDP multicast!"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

sock.sendto(MESSAGE, (MCAST_GRP, UDP_PORT))

sock.close()

