import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

# Inisialisasi pygame dan jendela OpenGL
pygame.init()
screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Transformasi Objek 3D - Limas & Kerucut")

# Perspektif kamera
gluPerspective(45, (800 / 600), 0.1, 50.0)
glTranslatef(0.0, 0.0, -10)

# Variabel transformasi
angle_x, angle_y = 0, 0
scale = 1.0

# Gambar Limas Segitiga
def draw_pyramid():
    glBegin(GL_TRIANGLES)
    # Depan
    glColor3f(1, 0, 0)
    glVertex3f(0, 1, 0)
    glVertex3f(-1, -1, 1)
    glVertex3f(1, -1, 1)
    # Kiri
    glColor3f(0, 1, 0)
    glVertex3f(0, 1, 0)
    glVertex3f(-1, -1, 1)
    glVertex3f(-1, -1, -1)
    # Kanan
    glColor3f(0, 0, 1)
    glVertex3f(0, 1, 0)
    glVertex3f(1, -1, 1)
    glVertex3f(1, -1, -1)
    # Belakang
    glColor3f(1, 1, 0)
    glVertex3f(0, 1, 0)
    glVertex3f(-1, -1, -1)
    glVertex3f(1, -1, -1)
    glEnd()

    glBegin(GL_QUADS)
    # Alas
    glColor3f(1, 0, 1)
    glVertex3f(-1, -1, 1)
    glVertex3f(1, -1, 1)
    glVertex3f(1, -1, -1)
    glVertex3f(-1, -1, -1)
    glEnd()

# Gambar Kerucut
def draw_cone():
    glColor3f(0, 1, 1)
    quad = gluNewQuadric()
    glPushMatrix()
    glTranslatef(3, -1, 0)    # Geser posisi kerucut
    glRotatef(-90, 1, 0, 0)   # Putar agar berdiri tegak
    gluCylinder(quad, 1, 0, 2, 32, 32)
    glPopMatrix()

# Loop utama
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_EQUALS:
                scale += 0.1
            elif event.key == pygame.K_MINUS:
                scale = max(0.1, scale - 0.1)
            elif event.key == pygame.K_LEFT:
                glTranslatef(-0.3, 0, 0)
            elif event.key == pygame.K_RIGHT:
                glTranslatef(0.3, 0, 0)
            elif event.key == pygame.K_UP:
                glTranslatef(0, 0.3, 0)
            elif event.key == pygame.K_DOWN:
                glTranslatef(0, -0.3, 0)

    # Bersihkan layar
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    # Transformasi dan gambar objek
    glPushMatrix()
    glScalef(scale, scale, scale)
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)

    draw_pyramid()
    draw_cone()

    glPopMatrix()

    # Rotasi otomatis
    angle_x += 0.5
    angle_y += 0.5

    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()
sys.exit()
