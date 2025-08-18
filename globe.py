import pygame
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import numpy


def read_texture(filename):
    """Reads an image file and converts it to an OpenGL texture"""
    img = Image.open(filename).convert("RGB")
    img_data = numpy.array(img.getdata(), numpy.uint8)

    textID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textID)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                 img.size[0], img.size[1], 0,
                 GL_RGB, GL_UNSIGNED_BYTE, img_data)

    return textID


def draw_background(texture):
    """Draw a large sphere with galaxy texture inside-out"""
    glPushMatrix()
    glBindTexture(GL_TEXTURE_2D, texture)

    quad = gluNewQuadric()
    gluQuadricTexture(quad, GL_TRUE)
    gluQuadricOrientation(quad, GLU_INSIDE)  # render inside surface
    gluSphere(quad, 30, 100, 100)            # large sky sphere
    gluDeleteQuadric(quad)

    glPopMatrix()


def main():
    pygame.init()
    info = pygame.display.Info()   # get monitor resolution
    display = (info.current_w - 100, info.current_h - 100)  # slightly smaller than screen

    # Windowed mode with minimize/maximize buttons
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption('Continental Quest')
    pygame.key.set_repeat(1, 10)

    # Projection and initial view
    gluPerspective(40, (display[0] / display[1]), 0.1, 100.0)
    glTranslatef(0.0, 0.0, -6)    # move camera slightly back

    lastPosX, lastPosY = 0, 0
    earth_tex = read_texture('world.jpg')
    galaxy_tex = read_texture('galaxy.jpg')

    # Create sphere quadric once (better performance)
    qobj = gluNewQuadric()
    gluQuadricTexture(qobj, GL_TRUE)

    while True:
        for event in pygame.event.get():
            # Exit cleanly if user quits window
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # Exit with ESC
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_LEFT:
                    glRotatef(1, 0, 1, 0)
                if event.key == pygame.K_RIGHT:
                    glRotatef(1, 0, -1, 0)
                if event.key == pygame.K_UP:
                    glRotatef(1, -1, 0, 0)
                if event.key == pygame.K_DOWN:
                    glRotatef(1, 1, 0, 0)

            # Zoom in/out with mouse wheel
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # wheel rolled up
                    glScaled(1.05, 1.05, 1.05)
                if event.button == 5:  # wheel rolled down
                    glScaled(0.95, 0.95, 0.95)

            # Rotate with mouse drag
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                dx = x - lastPosX
                dy = y - lastPosY
                mouseState = pygame.mouse.get_pressed()
                if mouseState[0]:  # left mouse button drag
                    modelView = (GLfloat * 16)()
                    mvm = glGetFloatv(GL_MODELVIEW_MATRIX, modelView)

                    temp = (GLfloat * 3)()
                    temp[0] = modelView[0]*dy + modelView[1]*dx
                    temp[1] = modelView[4]*dy + modelView[5]*dx
                    temp[2] = modelView[8]*dy + modelView[9]*dx
                    norm_xy = math.sqrt(temp[0]**2 + temp[1]**2 + temp[2]**2)
                    if norm_xy != 0:
                        glRotatef(math.sqrt(dx*dx+dy*dy),
                                  temp[0]/norm_xy, temp[1]/norm_xy, temp[2]/norm_xy)

                lastPosX, lastPosY = x, y

        # -------- Draw scene --------
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw Galaxy Background (rotates with same transformations)
        glEnable(GL_TEXTURE_2D)
        draw_background(galaxy_tex)

        # Draw Earth
        glBindTexture(GL_TEXTURE_2D, earth_tex)
        gluSphere(qobj, 2.5, 100, 100)

        glDisable(GL_TEXTURE_2D)

        # Display pygame window
        pygame.display.flip()
        pygame.time.wait(10)


main()
