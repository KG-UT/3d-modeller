"""Contains our node classes"""
from numpy import random
from OpenGL.GL import *
import numpy
import pyrr

G_OBJ_PLANE = 1
G_OBJ_SPHERE = 2
G_OBJ_CUBE = 3


class Node:
    """Base class for scene elements"""

    def __init__(self):
        # TODO: FIND RIGHT NUMBERS TO PUT INTO HERE. 0 AND 255 ARE PLACEHOLDERS
        self.color_index = random.randint(0, 255)
        self.aabb = pyrr.aabb.create_from_points([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]])  # Maybe need to convert outer list
        # into a numpy array
        self.translation_matrix = numpy.identity(4)
        self.scaling_matrix = numpy.identity(4)
        self.selected = False

    def render(self):
        glPushMatrix() # duplicate and push down matrix
        glMultMatrixf(numpy.transpose(self.translation_matrix)) # mult. curr. matrix by transpose of translation matrix
        # cuz reasons
        glMultMatrixf(self.scaling_matrix)  # scale it
        cur_color = (255, 255, 255)  # TODO: FIND WHAT TO PUT HERE! BLACK PLACEHOLDER HERE FOR NOW
        glColor3f(cur_color[0], cur_color[1], cur_color[2])  # specify new rgb values for curr. color
        if self.selected: # emit light if node is selected
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.3, 0.3, 0.3])

        self.render_self()

        if self.selected:
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0])
        glPopMatrix()  # replace curr. matrix with one below

    def render_self(self):
        raise NotImplementedError('render_self is not defined in the abstract Node class.')


class Primitive(Node):
    def __init__(self):
        """ Initializes Primitive. Inherits __init__ from parent."""
        super().__init__()
        self.call_list = None

    def render_self(self):
        glCallList(self.call_list)


class Sphere(Primitive):
    def __init__(self):
        """ Initializes Sphere. Inherits __init__ from parent."""
        super().__init__()
        self.call_list = G_OBJ_SPHERE


class Cube(Primitive):
    def __init__(self):
        """ Initializes Sphere. Inherits __init__ from parent."""
        super().__init__()
        self.call_list = G_OBJ_CUBE


class HierarchicalNode(Node):
    def __init__(self):
        """ Initializes HierarchicalNode. Inherits __init__ from parent."""
        super(HierarchicalNode, self).__init__()
        self.child_nodes = []

    def render_self(self):
        for child in self.child_nodes:
            child.render()