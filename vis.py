import json
import socket
import pygame

from pygame.locals import (
    DOUBLEBUF,
    OPENGL,
    QUIT,
)

from OpenGL.GL import *
from OpenGL.GLU import *


# ============================================================
# UDP
# ============================================================

UDP_IP = "127.0.0.1"
UDP_PORT = 5000

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sock.bind(
    (UDP_IP, UDP_PORT)
)

# Don't allow recvfrom() to freeze the visualization
sock.setblocking(False)


# ============================================================
# CUBE
# ============================================================

def draw_cube():

    vertices = [
        (-1, -1, -1),
        ( 1, -1, -1),
        ( 1,  1, -1),
        (-1,  1, -1),

        (-1, -1,  1),
        ( 1, -1,  1),
        ( 1,  1,  1),
        (-1,  1,  1),
    ]

    faces = [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 4, 7, 3),
        (1, 5, 6, 2),
        (3, 2, 6, 7),
        (0, 1, 5, 4),
    ]

    glBegin(GL_QUADS)

    for face in faces:
        for vertex in face:
            glVertex3fv(
                vertices[vertex]
            )

    glEnd()


# ============================================================
# OPENGL
# ============================================================

def setup_opengl():

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(
        GL_PROJECTION
    )

    gluPerspective(
        45,
        800 / 600,
        0.1,
        100
    )

    glMatrixMode(
        GL_MODELVIEW
    )


# ============================================================
# MAIN
# ============================================================

pygame.init()

pygame.display.set_mode(
    (800, 600),
    DOUBLEBUF | OPENGL
)

pygame.display.set_caption(
    "Live Sensor Visualization"
)

setup_opengl()

clock = pygame.time.Clock()


# Last received sensor values
roll = 0.0
pitch = 0.0
yaw = 0.0


running = True

while running:

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == QUIT:
            running = False


    # ========================================================
    # RECEIVE SENSOR DATA
    # ========================================================

    try:

        message, address = sock.recvfrom(65535)

        data = json.loads(
            message.decode()
        )

        orientation = \
            data["orientation"]

        roll = orientation["roll"]
        pitch = orientation["pitch"]
        yaw = orientation["yaw"]

    except BlockingIOError:

        # No new packet yet
        pass


    # ========================================================
    # DRAW
    # ========================================================

    glClear(
        GL_COLOR_BUFFER_BIT |
        GL_DEPTH_BUFFER_BIT
    )

    glLoadIdentity()

    # Camera
    glTranslatef(
        0,
        0,
        -6
    )

    # ========================================================
    # APPLY SENSOR ORIENTATION
    # ========================================================

    # Yaw
    glRotatef(
        yaw,
        0,
        1,
        0
    )

    # Pitch
    glRotatef(
        pitch,
        1,
        0,
        0
    )

    # Roll
    glRotatef(
        roll,
        0,
        0,
        1
    )

    # ========================================================
    # DRAW CUBE
    # ========================================================

    draw_cube()

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
sock.close()
