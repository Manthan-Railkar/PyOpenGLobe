import pygame
import math
import time
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import numpy as np
import random


def read_texture(filename):
    """Reads an image file and converts it to an OpenGL texture with enhanced filtering"""
    try:
        img = Image.open(filename).convert("RGB")
        img_data = np.array(img.getdata(), np.uint8)

        textID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, textID)

        # Enhanced texture parameters for better quality
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        
        # Generate mipmaps for better quality at distance
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                     img.size[0], img.size[1], 0,
                     GL_RGB, GL_UNSIGNED_BYTE, img_data)
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, img.size[0], img.size[1],
                          GL_RGB, GL_UNSIGNED_BYTE, img_data)

        return textID
    except Exception as e:
        print(f"Error loading texture {filename}: {e}")
        return 0

def setup_lighting():
    """Setup realistic lighting with sun positioning"""
    # Enable lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Set ambient light (space environment)
    ambient_light = [0.1, 0.1, 0.15, 1.0]  # Slightly blue ambient
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    
    # Set diffuse light (sun)
    diffuse_light = [1.0, 0.95, 0.8, 1.0]  # Warm sunlight
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    
    # Set specular light
    specular_light = [0.8, 0.8, 0.8, 1.0]
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)
    
    # Position the sun (from the right side)
    light_position = [10.0, 5.0, 5.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

def draw_atmosphere(radius):
    """Draw a glowing atmosphere around the Earth"""
    glPushMatrix()
    
    # Disable texture and enable blending for atmosphere
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)  # Don't write to depth buffer
    
    # Atmosphere color (blue glow)
    glColor4f(0.2, 0.4, 0.8, 0.3)
    
    # Draw slightly larger transparent sphere
    quad = gluNewQuadric()
    gluSphere(quad, radius * 1.05, 50, 50)
    gluDeleteQuadric(quad)
    
    # Reset states
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glColor4f(1.0, 1.0, 1.0, 1.0)
    
    glPopMatrix()

def draw_stars(count=500):
    """Draw a field of stars in the background"""
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glPointSize(1.0)
    
    glBegin(GL_POINTS)
    random.seed(42)  # Consistent star pattern
    
    for _ in range(count):
        # Random position on sphere
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        r = 50  # Far away
        
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        
        # Vary brightness
        brightness = random.uniform(0.3, 1.0)
        glColor3f(brightness, brightness, brightness)
        glVertex3f(x, y, z)
    
    glEnd()
    glEnable(GL_LIGHTING)

def draw_clouds(radius, time_offset):
    """Draw animated cloud layer"""
    glPushMatrix()
    
    # Rotate clouds slowly
    glRotatef(time_offset * 5, 0, 1, 0)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    
    # Semi-transparent white clouds
    glColor4f(1.0, 1.0, 1.0, 0.6)
    
    # Draw cloud patches procedurally
    glBegin(GL_TRIANGLES)
    
    random.seed(123)  # Consistent cloud pattern
    for _ in range(200):  # Number of cloud patches
        # Random position on sphere
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        
        # Cloud density varies
        if random.random() > 0.7:  # Only 30% coverage
            cloud_radius = radius * 1.02  # Slightly above surface
            
            # Create small triangular cloud patch
            for i in range(3):
                offset_theta = theta + random.uniform(-0.1, 0.1)
                offset_phi = phi + random.uniform(-0.1, 0.1)
                
                x = cloud_radius * math.sin(offset_phi) * math.cos(offset_theta)
                y = cloud_radius * math.sin(offset_phi) * math.sin(offset_theta)
                z = cloud_radius * math.cos(offset_phi)
                
                glVertex3f(x, y, z)
    
    glEnd()
    
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glColor4f(1.0, 1.0, 1.0, 1.0)
    
    glPopMatrix()


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
    pygame.display.set_caption('Continental Quest - Realistic Earth')
    pygame.key.set_repeat(1, 10)

    # OpenGL setup
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)  # Normalize normals automatically
    
    # Set clear color to space black
    glClearColor(0.0, 0.0, 0.05, 1.0)

    # Projection and initial view
    gluPerspective(40, (display[0] / display[1]), 0.1, 100.0)
    glTranslatef(0.0, 0.0, -6)    # move camera slightly back

    # Setup realistic lighting
    setup_lighting()

    # Load textures
    lastPosX, lastPosY = 0, 0
    earth_tex = read_texture('world.jpg')
    galaxy_tex = read_texture('galaxy.jpg')
    
    # Try to load cloud texture (optional)
    cloud_tex = read_texture('clouds.png')
    if cloud_tex == 0:
        cloud_tex = None
        print("Cloud texture not found, using procedural clouds")

    # Create sphere quadric once (better performance)
    qobj = gluNewQuadric()
    gluQuadricTexture(qobj, GL_TRUE)
    gluQuadricNormals(qobj, GLU_SMOOTH)  # Enable smooth normals
    
    # Earth material properties
    earth_material_ambient = [0.2, 0.2, 0.2, 1.0]
    earth_material_diffuse = [0.8, 0.8, 0.8, 1.0]
    earth_material_specular = [0.1, 0.1, 0.1, 1.0]
    earth_material_shininess = [5.0]
    
    start_time = time.time()

    while True:
        current_time = time.time() - start_time
        
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
                # Add lighting controls
                if event.key == pygame.K_l:
                    # Toggle lighting
                    if glIsEnabled(GL_LIGHTING):
                        glDisable(GL_LIGHTING)
                        print("Lighting disabled")
                    else:
                        glEnable(GL_LIGHTING)
                        print("Lighting enabled")

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
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Disable lighting for background elements
        glDisable(GL_LIGHTING)
        
        # Draw stars in far background
        draw_stars(800)
        
        # Draw Galaxy Background (rotates with same transformations)
        glEnable(GL_TEXTURE_2D)
        glColor4f(0.3, 0.3, 0.3, 1.0)  # Dim the galaxy texture
        draw_background(galaxy_tex)
        
        # Re-enable lighting for Earth
        glEnable(GL_LIGHTING)
        glColor4f(1.0, 1.0, 1.0, 1.0)  # Reset color
        
        # Set Earth material properties
        glMaterialfv(GL_FRONT, GL_AMBIENT, earth_material_ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, earth_material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, earth_material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, earth_material_shininess)
        
        # Draw atmosphere first (behind Earth)
        glDisable(GL_TEXTURE_2D)
        draw_atmosphere(2.5)
        
        # Draw Earth with texture
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, earth_tex)
        gluSphere(qobj, 2.5, 100, 100)
        
        # Draw procedural clouds
        glDisable(GL_TEXTURE_2D)
        draw_clouds(2.5, current_time)
        
        # Optional: if cloud texture is available, use it instead
        if cloud_tex:
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glBindTexture(GL_TEXTURE_2D, cloud_tex)
            glColor4f(1.0, 1.0, 1.0, 0.7)
            
            glPushMatrix()
            glRotatef(current_time * 8, 0, 1, 0)  # Rotate clouds
            gluSphere(qobj, 2.52, 80, 80)  # Slightly larger than Earth
            glPopMatrix()
            
            glDisable(GL_BLEND)
            glColor4f(1.0, 1.0, 1.0, 1.0)
        
        glDisable(GL_TEXTURE_2D)

        # Display pygame window
        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == '__main__':
    main()
