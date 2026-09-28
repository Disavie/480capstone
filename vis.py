import json
import pygame
import sqlite3

from pygame.locals import (
    DOUBLEBUF,
    OPENGL,
    QUIT,
)

from OpenGL.GL import *
from OpenGL.GLU import *


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
            glVertex3fv(vertices[vertex])

    glEnd()


# ============================================================
# DIRECTION ARROW
# ============================================================

def draw_direction_arrow():

    # The cube's forward direction is +Z.
    #
    # Cube front:
    #       z = +1
    #
    # Arrow:
    #       starts at z = 1
    #       ends at z = 3.5

    arrow_start = 1.0
    arrow_end = 3.5

    # ----------------------------
    # Arrow shaft
    # ----------------------------

    glLineWidth(5.0)

    glColor3f(
        1.0,
        0.0,
        0.0
    )

    glBegin(GL_LINES)

    glVertex3f(
        0,
        0,
        arrow_start
    )

    glVertex3f(
        0,
        0,
        arrow_end
    )

    glEnd()

    # ----------------------------
    # Arrow head
    # ----------------------------

    # Four lines making a simple arrowhead

    head_start = 3.1
    head_end = 3.5
    head_size = 0.35

    glBegin(GL_LINES)

    # Top/bottom
    glVertex3f(0, 0, head_end)
    glVertex3f(head_size, 0, head_start)

    glVertex3f(0, 0, head_end)
    glVertex3f(-head_size, 0, head_start)

    # Left/right
    glVertex3f(0, 0, head_end)
    glVertex3f(0, head_size, head_start)

    glVertex3f(0, 0, head_end)
    glVertex3f(0, -head_size, head_start)

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
        with sqlite3.connect("data/test_db.sqlite") as con:
            cursor = con.cursor()

            sql_query = "SELECT * FROM entries ORDER BY timestamp DESC LIMIT 1"
            query_params = ()
            cursor.execute(sql_query,query_params)

            res = cursor.fetchall()[0]

            print(res)
            if len(res) > 3:
                roll = res[len(res)-3]
                pitch = res[len(res)-2]
                yaw = res[len(res)-1]

    except BlockingIOError:

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

    glColor3f(
        0.7,
        0.7,
        0.7
    )

    draw_cube()


    # ========================================================
    # DRAW FACING DIRECTION
    # ========================================================

    draw_direction_arrow()


    pygame.display.flip()

    clock.tick(60)


pygame.quit()
sock.close()
