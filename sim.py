import csv
import socket
import time
import json
import math

UDP_IP = "127.0.0.1"
UDP_PORT = 5000
sample_rate = 30

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

with open("data/gyro_sample.csv", newline="") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        roll = math.degrees(float(row[1]))
        pitch = math.degrees(float(row[2]))
        yaw = math.degrees(float(row[3]))
        msg = json.dumps({
            "orientation": {
                "roll": roll,
                "pitch": pitch,
                "yaw": yaw
            }
        })
        print(f"{msg} \r", end="")
        sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))
        time.sleep(1 / sample_rate)
