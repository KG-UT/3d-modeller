""" Contains our Scene class"""
from nodes import Node


class Scene:
    """ The scene that is to be rendered."""
    node_list: list
    # default depth from the camera to place an object at
    PLACE_DEPTH = 15.0

    def __init__(self):
        """ Initialize the Scene."""
        # keep a list of nodes to be displayed
        self.node_list = []
        # Keep track of the currently selected node.
        self.selected_node = None

    def add_node(self, node: Node):
        """adds a new node to the scene"""
        self.node_list.append(node)

    def render(self):
        """ Renders the Scene."""
        for node in self.node_list:
            node.render()

    def pick(self, start, direction, mat):
        """ Executes selection of a node.

        :param start: Describes a ray. This is where the ray starts from. Is a numpy array.
        :param direction: Describes a ray. This is the direction of the ray. Is a numpy array.
        :param mat: The inverse of the current modelview matrix for the scene.
        :return: None
        """
        if self.selected_node is not None:
            self.selected_node.select(False)
            self.selected_node = None

        # Keep track of the closest hit.
        mindist = sys.maxint
        closest_node = None
        for node in self.node_list:
            hit, distance = node.pick(start, direction, mat)
            if hit and distance < mindist:
                mindist, closest_node = distance, node

        # If we hit something, keep track of it.
        if closest_node is not None:
            closest_node.select()
            closest_node.depth = mindist
            closest_node.selected_loc = start + direction * mindist
            self.selected_node = closest_node
