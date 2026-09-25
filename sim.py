import csv
import socket
import time
import json
import math
import struct

UDP_IP = "127.0.0.1"
UDP_PORT = 5000
UDP_PORT_JSON = 5001

GROUP = b"ABCD"
UUID  = b"1234"
sample_rate = 30



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

with open("data/cow-test.csv", newline="") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        ax = float(row[1])
        ay = float(row[2])
        az = float(row[3])
        lat = float(row[4])
        lon = float(row[5])
        height = float(row[6])
        v = float(row[7])
        bearing = float(row[8])
        roll = math.degrees(float(row[9]))
        pitch = math.degrees(float(row[10]))
        yaw = math.degrees(float(row[11]))


        packet = struct.pack(
            "<4s4sfffffffffff",
            GROUP,
            UUID,
            ax,
            ay,
            az,
            lat,
            lon,
            height,
            v,
            bearing,
            roll,
            pitch,
            yaw

        )
#Even parity over all preceding bytes

        ones = sum(byte.bit_count() for byte in packet)
        parity = ones & 1

        packet += struct.pack("<B", parity)
        print(packet)
        print(f"{roll} {pitch} {yaw} \r", end="")

        sock.sendto(packet, (UDP_IP, UDP_PORT))
        time.sleep(1 / sample_rate)
'''
    'packet' format, add more info into this later
    everything from TIME..UZ will be a float
    PARITY can be a 1 bit even parity
    GROUP and UUID will be 8 bits each

    |GROUP|UUID|ax|ay|az|lat|lon|height|velocity|bearing|roll|pitch|yaw|PARITY|
    GROUP, UUID -> 4 Bytes
    Data fields -> 4 Bytes (32 bits)
    Parity -> 1 bit + padding
'''
