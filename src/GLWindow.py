import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr

from Geometry import Geometry

# Notes on shaders
# Vertex shader -> Runs once per vertex and is responsible for position on screen and possibly some transformations
# Fragment shader -> Shape assembled and broken down to fragments/pixel. Resposible for calculating colour per pixels. Can be written as 
# strings but text files are better. 
# Notes om shaders. They do colour and positions seperately. It looks like we do it as one. vec4 so transformations can be done ith matrics

class Triangle:

    def __init__(self, shader):
        self.vertexLoc = glGetAttribLocation(shader, "position")
        #x, y, z, r, g, b    List of vertices. All the data we want to store at each point in a primitive. Here only positions - no colours or textures etc
        # openGL uses normalised device co-ordinates
        # x - left tp right - -1 to +1
        # y - bottom to top
        # z - depth - 0 -> flat on screen
        # np array data type built for c style data reading 
        # np array constructors used to pass to graphics card
        # must be 32 
        self.vertices = np.array([0.0, 0.5, 0.0,
                                  -0.5, -0.5, 0.0,
                                  0.5, -0.5, 0.0], dtype=np.float32)

        self.vertexCount = 3
        self.vbo = glGenBuffers(1)     # Vertex buffer object. One buffer for us.
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo) # Bind buffer so we know which one we are talking about
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW) # Shift buffer off to graphics card. # Static draw means set data once and use many times. Static draw for reading and writing multiple times. Both good though

        # enable attribute and describe how it is laid out in VBO. Not sure what vertex.loc is. 3 points in attribute
        # Data type floating point decimals 
        # False as do not need to normalise numbers
        # Stride is how many bytes we need to step to get to next position. Not sure why it is 0
        # Offset. How far we need to go to find type. Void pointer is special type of memory address. 
        # Allocating memory to graphcis card
        glEnableVertexAttribArray(self.vertexLoc)
        glVertexAttribPointer(self.vertexLoc, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

    def cleanup(self):
        # Freeing vbo. , represents a list
        glDeleteBuffers(1, (self.vbo,))

# Cube Object that holds position and eulers for an object
class Cube:


    def __init__(self, position, eulers):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

# Used to define Cube objects to be displayed
class Scene:
    def __init__(self):

        # Initial object in scene centered in screen
        self.cubes = [
            Cube(
                position=[0, 0, -10],
                eulers=[0, 0, 0]
            ),
        ]

    # Add secondary object adjacent to initial object
    def addCube(self):
        newCube = Cube(
                position=[-3, 0, -10],
                eulers=[0, 0, 0]
            )
        self.cubes.append(newCube)

class OpenGLWindow:

    def __init__(self):
        self.triangle = None
        self.clock = pg.time.Clock()
        self.scene = Scene()


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
    def initGL(self, screen_width=960, screen_height=540, addSwitch=False, objectname="cube.obj"):
        # Initialise Scene. Has to be here in order for us to reset the scene
        self.scene = Scene()
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



        # Note that this path is relative to your working directory when running the program
        # You will need change the filepath if you are running the script from inside ./src/
        # Call function and call resulting shader
        # Should have shader in use before declaring data

        self.shader = self.loadShaderProgram("./shaders/simple.vert", "./shaders/simple.frag")
        glUseProgram(self.shader)

        colorLoc = glGetUniformLocation(self.shader, "objectColor")
        glUniform3f(colorLoc, 1.0, 1.0, 1.0)

        # Uncomment this for triangle rendering
        #self.triangle = Triangle(self.shader)

        # Uncomment this for model rendering
        # Load obj file
        name = "resources/" + objectname
        self.cube_load = Geometry(name)

        # Used to add an extra object and reset scene
        if (addSwitch == True):
            self.scene = Scene()
            self.scene.addCube()

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

        print("Setup complete!")


    def render(self, rotate, scale, x, y, z):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)   # Colour buffer stores all pixels on screen. Colours stored in colour buffer bit
        glUseProgram(self.shader)  # You may not need this line


        count = 0   # Used to seperate rotation of cubes
        for cube in self.scene.cubes:
            # Start with identity and multiply on progressively
            # Identity Matrix
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)    # Gonna leave this here for now
            # When count is 0 we are rotating the center object
            if count == 0:
                # Eulers used for rotation. Value of rotate used to determine which axis we are rotating on relative to the center object. x, z, y
                if (rotate >= 0 & rotate <=2):
                    cube.eulers[rotate] += 0.25
                    if cube.eulers[rotate] > 360:
                        cube.eulers[rotate] -= 360


                # Rotation matrix
                model_transform = pyrr.matrix44.multiply(
                    m1=model_transform,
                    m2=pyrr.matrix44.create_from_eulers(
                        eulers=np.radians(cube.eulers), dtype=np.float32
                    )
                )
                # Used to scale objects
                model_transform = pyrr.matrix44.multiply(
                    m1=model_transform,
                    m2=pyrr.matrix44.create_from_scale(np.array([scale, scale, scale]), dtype=np.float32)
                )
            # When count is 1 (ie > 0) we are rotating the peripheral object around center object
            elif count > 0:
                # translate

                model_transform = pyrr.matrix44.multiply(
                    m1=model_transform,
                    m2=pyrr.matrix44.create_from_translation(np.array([3, 0, 0]), dtype=np.float32)
                )

                if (rotate >= 0 & rotate <=2):
                    cube.eulers[rotate] += 0.25
                    if cube.eulers[rotate] > 360:
                        cube.eulers[rotate] -= 360

                model_transform = pyrr.matrix44.multiply(
                    m1=model_transform,
                    m2=pyrr.matrix44.create_from_eulers(
                        eulers=np.radians(cube.eulers), dtype=np.float32
                    )
                )

                # Used to scale objects
                model_transform = pyrr.matrix44.multiply(
                    m1=model_transform,
                    m2=pyrr.matrix44.create_from_scale(np.array([scale, scale, scale]), dtype=np.float32)
                )

                model_transform = pyrr.matrix44.multiply(
                    m1=model_transform,
                    m2=pyrr.matrix44.create_from_translation(np.array([3, 0, 0]), dtype=np.float32)
                    )



            # Used to translate both objects
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_translation(np.array([x, y, z]), dtype=np.float32)
            )

            # Send to position
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_translation(
                    vec=np.array(cube.position), dtype=np.float32
                )
            )
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_transform)


            glBindVertexArray(self.cube_load.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.cube_load.vertexCount)

            count = count + 1
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



