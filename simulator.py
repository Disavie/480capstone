import math
import time
import random
import json
import socket
from dataclasses import dataclass


# ============================================================
# UDP SETUP
# ============================================================

UDP_IP = "127.0.0.1"
UDP_PORT = 5000

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)


# ============================================================
# STATE
# ============================================================

@dataclass
class State:
    latitude: float = 42.7315
    longitude: float = -84.5555
    altitude: float = 250.0

    north_velocity: float = 10.0
    east_velocity: float = 0.0
    vertical_velocity: float = 0.0

    north_acceleration: float = 0.0
    east_acceleration: float = 0.0
    vertical_acceleration: float = 0.0

    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0


state = State()

DT = 0.01  # 100 Hz


# ============================================================
# HELPERS
# ============================================================

def meters_to_latitude(meters):
    return meters / 111_320.0


def meters_to_longitude(meters, latitude):
    return meters / (
        111_320.0 *
        math.cos(math.radians(latitude))
    )


def add_noise(value, standard_deviation):
    return value + random.gauss(
        0,
        standard_deviation
    )


# ============================================================
# SIMULATION
# ============================================================

def update_state(state, dt):

    t = time.time()

    # ----------------------------------------
    # Simulated acceleration
    # ----------------------------------------

    state.north_acceleration = \
        math.sin(t) * 0.5

    state.east_acceleration = \
        math.cos(t * 0.5) * 0.2

    # ----------------------------------------
    # Acceleration -> velocity
    # ----------------------------------------

    state.north_velocity += \
        state.north_acceleration * dt

    state.east_velocity += \
        state.east_acceleration * dt

    # ----------------------------------------
    # Velocity -> position
    # ----------------------------------------

    state.latitude += meters_to_latitude(
        state.north_velocity * dt
    )

    state.longitude += meters_to_longitude(
        state.east_velocity * dt,
        state.latitude
    )

    state.altitude += \
        state.vertical_velocity * dt

    # ----------------------------------------
    # Orientation
    # ----------------------------------------

    state.roll = math.sin(t * 0.8) * 90

    state.pitch = math.sin(t * 0.5) * 20

    state.yaw += 30 * dt

    state.yaw %= 360


# ============================================================
# SENSOR GENERATION
# ============================================================

def generate_sensor_data(state):

    return {

        "timestamp": time.time(),

        "gps": {
            "latitude":
                add_noise(
                    state.latitude,
                    0.000005
                ),

            "longitude":
                add_noise(
                    state.longitude,
                    0.000005
                ),

            "altitude":
                add_noise(
                    state.altitude,
                    1.5
                ),

            "north_velocity":
                add_noise(
                    state.north_velocity,
                    0.1
                ),

            "east_velocity":
                add_noise(
                    state.east_velocity,
                    0.1
                ),

            "vertical_velocity":
                add_noise(
                    state.vertical_velocity,
                    0.1
                ),
        },

        "accelerometer": {
            "x":
                add_noise(
                    state.north_acceleration,
                    0.05
                ),

            "y":
                add_noise(
                    state.east_acceleration,
                    0.05
                ),

            "z":
                add_noise(
                    9.81 + state.vertical_acceleration,
                    0.05
                ),
        },

        "orientation": {
            "roll":
                add_noise(
                    state.roll,
                    0.3
                ),

            "pitch":
                add_noise(
                    state.pitch,
                    0.3
                ),

            "yaw":
                add_noise(
                    state.yaw,
                    0.3
                ),
        }
    }


# ============================================================
# MAIN
# ============================================================

while True:

    update_state(
        state,
        DT
    )

    data = generate_sensor_data(
        state
    )

    # Convert dictionary -> JSON -> bytes
    message = json.dumps(data).encode()
    print(message)

    # Send to vis.py
    sock.sendto(
        message,
        (UDP_IP, UDP_PORT)
    )

    # Print locally
    orientation = data["orientation"]

    print(
        f"\r"
        f"Roll:  {orientation['roll']:7.2f}° | "
        f"Pitch: {orientation['pitch']:7.2f}° | "
        f"Yaw:   {orientation['yaw']:7.2f}°",
        end=""
    )

    time.sleep(DT)
