import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr
import math
import time
from sklearn.preprocessing import normalize

from Geometry import Geometry

# Notes on shaders
# Vertex shader -> Runs once per vertex and is responsible for position on screen and possibly some transformations
# Fragment shader -> Shape assembled and broken down to fragments/pixel. Resposible for calculating colour per pixels. Can be written as 
# strings but text files are better. 
# Notes om shaders. They do colour and positions seperately. It looks like we do it as one. vec4 so transformations can be done ith matrics

# Cube Object that holds position and eulers for an object
class Cube:


    def __init__(self, position, eulers):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

class Camera:
    def __init__(self, position):

        self.position = np.array(position, dtype=np.float32)
        self.update_vectors()

    def update_vectors(self):
        cameraTarget = np.array([0, 0, 0], dtype=np.float32)
        self.cameraDirection = Camera.norm(self.position - cameraTarget)
        print(self.cameraDirection)
        globalUp = np.array([0, 1, 0], dtype=np.float32)
        self.cameraRight = Camera.norm(np.cross(globalUp, self.cameraDirection))
        print(self.cameraRight)
        self.up = Camera.norm(np.cross(self.cameraDirection, self.cameraRight))
        print(self.up)



    def norm(array):
        array = array / np.linalg.norm(array)
        return array


class Light:

    def __init__(self, position, color, strength):
        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.strength = strength

class Scene:
    def __init__(self):

        # Initial object in scene centered in screen
        self.cube = Cube(
                position=[0, 0, 0],
                eulers=[0, 0, 0]
            )

        self.camera = Camera(
            position=[0, 0, 9]
        )
        self.light1 = Light(
            position=np.array([3, 3, 3], dtype=np.float32),
            color=np.array([1, 0, 0], dtype=np.float32),
            strength=3
        )
        self.light2 = Light(
            position=np.array([-3, 3, 3], dtype=np.float32),
            color=np.array([0, 0, 1], dtype=np.float32),
            strength=3
        )

    def move_camera(self, move):

        move = np.array(move, dtype=np.float32)
        self.player.position += move
        self.player.update_vectors

class OpenGLWindow:

    def __init__(self):
        self.triangle = None
        self.clock = pg.time.Clock()
        self.scene = Scene()
        self.CameraTheta = 0
        self.lightTheta = 0


    def loadShaderProgram(self, vertex, fragment):
        # Opening vertex shader file in read. with as localises lifespan of resource so file closed after indented block
        with open(vertex, 'r') as f:
            vertex_src = f.readlines()

        with open(fragment, 'r') as f:
            fragment_src = f.readlines()

        # Compile each of shader and pass in source code with flags
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

    # Initialise
    def initGL(self, screen_width=810, screen_height=540, objectname="suzanne.obj", diffuseMap = "brickwall.jpg" , normalMap = "brickwall_normal.jpg"):
        # Initialise Scene. Has to be here in order for us to reset the scene
        #self.scene = Scene()
        pg.init()

        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)      # Wonder what this does

        # Creates new window. Tell pygame using opengL and use double buffering system.
        pg.display.set_mode((screen_width, screen_height), pg.OPENGL | pg.DOUBLEBUF)

        glEnable(GL_DEPTH_TEST) # Checks if objects are drawing in front of each other properly
        # Uncomment these two lines when perspective camera has been implemented
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # Shows which colour we want to show on our screen
        glClearColor(0, 0, 0, 1)

        self.shader = self.loadShaderProgram("./shaders/simple.vert", "./shaders/simple.frag")
        glUseProgram(self.shader)

        # colorLoc = glGetUniformLocation(self.shader, "objectColor")
        # glUniform3f(colorLoc, 1.0, 1.0, 1.0)


        self.texture = Material("resources/" + diffuseMap, "resources/" + normalMap)
        self.texture.use()


        glUniform1i(
            glGetUniformLocation(
                self.shader, "diffuseMap"
            ), 0
        )

        glUniform1i(
            glGetUniformLocation(
                self.shader, "normalMap"
            ), 1
        )


        name = "resources/" + objectname
        self.cube_load = Geometry(name)

        # Used to add an extra object and reset scene

        # Perspective Projection matrix - Gives us our view
        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy=45, aspect=640 / 480,    # fovy - field of view angle in the y think like half a view angle; aspect -> aspect ratio
            near=0.1, far=50, dtype=np.float32 # near closer than 0.1 not drawn and further than 10 not drawn
        )
        # Sending in a 4 x 4 matrix with float values
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"), # Get location of projection uniform matrix
            1, GL_FALSE, projection_transform     # Number of matrices putting in and whether to transpose them. Lasr arguement matrix we send in
        )

        # Don't have to query projection matrix because used every frame
        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
        self.cameraPosLoc = glGetUniformLocation(self.shader, "cameraPostion")
        self.light1Location = {
            "position": glGetUniformLocation(self.shader, "Light1.position"),
            "color": glGetUniformLocation(self.shader, "Light1.color"),
            "strength": glGetUniformLocation(self.shader, "Light1.strength")
        }

        self.light2Location = {
            "position": glGetUniformLocation(self.shader, "Light2.position"),
            "color": glGetUniformLocation(self.shader, "Light2.color"),
            "strength": glGetUniformLocation(self.shader, "Light2.strength")
        }

        print("Setup complete!")


    def render(self, rotate, scale, rotateCam = False, rotateLights = False):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)   # Colour buffer stores all pixels on screen. Colours stored in colour buffer bit
        glUseProgram(self.shader)  # You may not need this line

        if rotateCam:
            theta_copy = math.radians(self.CameraTheta)
            radius = 9
            camx = math.sin(theta_copy) * radius
            camz = math.cos(theta_copy) * radius
            self.CameraTheta += 0.3
            view_transform = pyrr.matrix44.create_look_at(
                eye=np.array([camx, 0, camz], dtype=np.float32),  # Position as eye
                target=np.array([0,0,0], dtype=np.float32),  # Where are looking to
                up=np.array([0,1,0], dtype=np.float32)  # Pass up for some reason
            )

        else:
            view_transform = pyrr.matrix44.create_look_at(
                eye=np.array([0, 0, 9], dtype=np.float32),  # Position as eye
                target=np.array([0, 0, 0], dtype=np.float32),  # Where are looking to
                up=np.array([0, 1, 0], dtype=np.float32)  # Pass up for some reason
            )

        glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_FALSE, view_transform)

        if rotateLights:
            lightTheta1 = math.radians(self.lightTheta + 45)
            lightx = math.sin(lightTheta1) * 4.242640687
            lightz = math.cos(lightTheta1) * 4.242640687
            self.scene.light1.position = np.array([lightx, 3, lightz], dtype=np.float32)

            lightTheta2 = math.radians(self.lightTheta - 45)
            camx = math.sin(lightTheta2) * 4.242640687
            camz = math.cos(lightTheta2) * 4.242640687
            self.scene.light2.position = np.array([camx, 3, camz], dtype=np.float32)

            self.lightTheta += 0.3

        else:
            lightTheta1 = math.radians(self.lightTheta + 45)
            lightx = math.sin(lightTheta1) * 4.242640687
            lightz = math.cos(lightTheta1) * 4.242640687
            self.scene.light1.position = np.array([lightx, 3, lightz], dtype=np.float32)

            lightTheta2 = math.radians(self.lightTheta - 45)
            camx = math.sin(lightTheta2) * 4.242640687
            camz = math.cos(lightTheta2) * 4.242640687
            self.scene.light2.position = np.array([camx, 3, camz], dtype=np.float32)

        glUniform3fv(self.light1Location["position"], 1, self.scene.light1.position)
        glUniform3fv(self.light1Location["color"], 1, self.scene.light1.color)
        glUniform1f(self.light1Location["strength"], self.scene.light1.strength)

        glUniform3fv(self.light2Location["position"], 1, self.scene.light2.position)
        glUniform3fv(self.light2Location["color"], 1, self.scene.light2.color)
        glUniform1f(self.light2Location["strength"], self.scene.light2.strength)

        glUniform3fv(self.cameraPosLoc, 1, self.scene.camera.position)

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)    # Gonna leave this here for now

        if (rotate >= 0 & rotate <=2):
            self.scene.cube.eulers[rotate] += 0.25
            if self.scene.cube.eulers[rotate] > 360:
                self.scene.cube.eulers[rotate] -= 360

        # Rotation matrix
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_eulers(
                eulers=np.radians(self.scene.cube.eulers), dtype=np.float32
            )
        )
        # Used to scale objects
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_scale(np.array([scale, scale, scale]), dtype=np.float32)
        )

        # Send to position
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.scene.cube.position), dtype=np.float32
            )
        )
        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_transform)


        glBindVertexArray(self.cube_load.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.cube_load.vertexCount)

        # Swap the front and back buffers on the window, effectively putting what we just "drew"
        # Onto the screen (whereas previously it only existed in memory)
        pg.display.flip()

        #
        self.clock.tick(100)

    def cleanup(self):
        # Deleting vao , represents list

        # Uncomment for triangle rendering
        #glDeleteVertexArrays(1, (self.vao,))
        #self.triangle.cleanup()
        # Uncomment for model rendering
        # Deleting vao , represents list
        glDeleteVertexArrays(1, (self.cube_load.vao,))
        self.cube_load.cleanup()

# Followed tutorial https://www.youtube.com/playlist?list=PLn3eTxaOtL2PDnEVNwOgZFm5xYPr4dUoR
class Material:

    def __init__(self, file1, file2):
        self.textures = []

        self.textures.append(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, self.textures[0])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(file1).convert()
        image_width, image_height = image.get_rect().size
        img_data = pg.image.tostring(image, 'RGBA')
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        self.textures.append(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, self.textures[1])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(file2).convert()
        image_width, image_height = image.get_rect().size
        img_data = pg.image.tostring(image, 'RGBA')
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        for i in range(len(self.textures)):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, self.textures[i])

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

