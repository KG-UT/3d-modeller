"""Contains our Viewer class"""
from OpenGL.GLU import *
from OpenGL.GLUT import *
from scene import Scene
from interactions import Interaction
from nodes import *
from primitive import init_primitives
from numpy.linalg import norm


class Viewer:
    """Manages window creation and rendering. Contains main loop of program"""

    def __init__(self):
        # Initialize our interface
        self.init_interface()

        # initialize openGL
        # ModelView and inverse are set to identity matrix to start with
        self.inverseModelView = numpy.identity(4)
        self.ModelView = numpy.identity(4)
        self.init_opengl()

        # initialize our scene
        self.scene = Scene()
        self.create_sample_scene()

        # Initialize our interactions
        self.interaction = Interaction()
        self.init_interaction()
        init_primitives()

    def init_interface(self):
        """Initialize the window and register the render function"""
        glutInit()   # initialize GLUT library
        glutInitWindowSize(640, 480)     # set window size
        glutCreateWindow("3D Modeller")  # creates window and sets title
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)  # Default: GLUT_SINGLE, GLUT_RGB
        glutDisplayFunc(self.render)  # set display callback for current window

    @staticmethod
    def init_opengl():
        """initialize opengl settings to render the scene"""

        # Note: Cull basically == get rid of
        glEnable(GL_CULL_FACE)  # Allow getting rid of objects not in view for efficiency
        glCullFace(GL_BACK)  # We get rid of the back face of polygons not in view
        glEnable(GL_DEPTH_TEST)  # do depth comparisons and update the depth buffer. Note: depth = pixel depth
        glDepthFunc(GL_LESS)  # Specifies function used to compare incoming pixel with the depth value present
        # in the depth buffer. I.e. whether or not incoming objects at same pixel location replaces old objects.
        # In this case, it passes if incoming depth value < stored depth value.

        glEnable(GL_LIGHT0)  # Set source of light. this is a single light. Can enable GL_LIGHT (1-7) for more lights.
        glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(0, 0, 1, 0))  # specifies a \light\, a light source for \light\,
        # and a pointer to the value(s) that the light source of \light\ will be set to.
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, GLfloat_3(0, 0, -1))  # same as above.
        # Note: GL_POSITION = position of light, and GL_SPOT_DIRECTION = direction of light.

        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)  # Specifies which faces should track current colour,
        # and specifies details on light quality.
        glEnable(GL_COLOR_MATERIAL)  # Enables the settings we previously just set
        glClearColor(0.4, 0.4, 0.4, 0.0)  # sets default RGBA values that glClear sets to.

    def create_sample_scene(self):
        """ Create a sample scene."""
        cube_node = Cube()
        # cube_node.translate(2, 0, 2)
        cube_node.color_index = 2
        self.scene.add_node(cube_node)

        sphere_node = Sphere()
        # sphere_node.translate(-2, 0, 2)
        sphere_node.color_index = 3
        self.scene.add_node(sphere_node)

    def init_interaction(self):
        """ init user interaction and callbacks """
        pass
        # self.interaction.register_callback('pick', self.pick)
        # self.interaction.register_callback('move', self.move)
        # self.interaction.register_callback('place', self.place)
        # self.interaction.register_callback('rotate_color', self.rotate_color)
        # self.interaction.register_callback('scale', self.scale)

    @staticmethod
    def main_loop():
        glutMainLoop()

    @staticmethod
    def init_view():
        """ Initialize the projection matrix"""
        width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)  # self explanatory
        aspect_ratio = width/height # ratio of width to height

        # load the projection matrix. Always the same.
        glMatrixMode(GL_PROJECTION)  # specifies projection matrix as matrix to do subsequent operations on.
        glLoadIdentity()  # make projection matrix into identity matrix

        glViewport(0, 0, width, height) # Sets the viewport to have proper width and height, and
        # specifies lower left corner be have coordinate (0,0)
        gluPerspective(70, aspect_ratio, 0.1, 1000.0)  # Set up perspective projection matrix.
        # field of view angle in y dir. = 70, 0.1 and 1000 specify distance from viewer to near and far clipping plane
        # respectively. Objects nearer than near clipping plane or farther than far clipping plane are not rendered
        glTranslated(0, 0, -15)  # multiply curr. matrix by this

    def render(self):
        """ The render pass for the scene"""
        self.init_view()  # Initialize projection matrix

        glEnable(GL_LIGHTING)  # Use curr. lighting parameters to compute vertex colour
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Set these stuff back to default value

        # Load the modelview matrix from the current state of the trackball
        glMatrixMode(GL_MODELVIEW)  # Set modelview matrix as curr. matrix
        glPushMatrix()  # duplicate and push down the stack the curr. matrix. add duplicate to top.
        glLoadIdentity()  # replace curr. matrix with identity matrix

        loc = self.interaction.translation  # current location of camera
        glTranslated(loc[0], loc[1], loc[2])  # multiply current matrix with a translation matrix
        glMultMatrixf(self.interaction.trackball.matrix)  # multiply current matrix with given matrix

        # store the inverse of the current modelview.
        current_modelview = numpy.array(glGetFloatv(GL_MODELVIEW_MATRIX))
        self.ModelView = numpy.transpose(current_modelview)
        self.inverseModelView = numpy.linalg.inv(numpy.transpose(current_modelview))

        # render the scene. This calls the render function for each object in the scene
        self.scene.render()

        # draw the grid
        glDisable(GL_LIGHTING)
        glCallList(G_OBJ_PLANE)
        glPopMatrix()

        # flush the buffers so that the scene can be drawn
        glFlush()

    def generate_ray(self, x: int, y: int) -> tuple:
        """ Generates a ray beginning at the near plane in the direction the x,y coordinates are facing

        :param x: x coordinate of mouse
        :param y: y coordinate of mouse
        :return: a tuple containing ? start ? and the direction of the ray
        """
        self.init_view()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # get two points on the line.
        start = numpy.array(gluUnProject(x, y, 0.001))   # z coordinate = 0.001
        end = numpy.array(gluUnProject(x, y, 0.999))  # z coordinate = 0.999

        # convert those points into a direction
        direction = end - start  # the difference between the two points gives a vector
        direction = direction / norm(direction)  # we divide by the norm of the vector to normalize it

        return start, direction

    def pick(self, x, y):
        """ Execute pick of an object. Selects an object in the scene. """
        start, direction = self.generate_ray(x, y)
        self.scene.pick(start, direction, self.ModelView)


if __name__ == "__main__":
    viewer = Viewer()
    viewer.main_loop()
