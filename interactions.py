""" Contains our Interaction class"""
import trackball
from collections import defaultdict
from OpenGL.GLUT import *
from typing import Optional, List, Tuple, Any

# For some reason, wheel up and wheel down constants not defnied anymore in glut
# http://hackage.haskell.org/package/GLUT-2.1.2.1/docs/src/Graphics-UI-GLUT-Constants.html  for constants
GLUT_WHEEL_UP = 3
GLUT_WHEEL_DOWN = 4


class Interaction:
    """ Handles user interactions.
    pressed - currently pressed mouse button
    translation - current location of camera
    trackball - the trackball to track rotation
    mouse_loc - current mouse location
    callbacks - callback mechanism"""
    pressed: Optional[int]
    translation: Optional[List[int]]
    mouse_loc: Optional[Tuple[int]]
    callbacks: dict

    def __init__(self):
        """ Initializes self. """
        self.pressed = None  # current pressed mouse button
        self.translation = [0, 0, 0, 0]  # current location of camera
        self.trackball = trackball.Trackball(theta=-25, distance=15)  # trackball to calculate rotation
        self.mouse_loc = None  # current mouse location
        self.callbacks = defaultdict(list)  # our callback mechanism
        # defaultdict is a normal dict, but if a key that isn't in there is called
        # instead of an error, it will create a new entry with default value [] given the argument list
        self.register()

    def register(self):  # TODO: FINISH THIS
        """ register callbacks with glut """
        glutMouseFunc(self.handle_mouse_button)
        glutMotionFunc(self.handle_mouse_motion)
        glutKeyboardFunc(self.handle_keystroke)
        glutSpecialFunc(self.handle_keystroke)

    def translate(self, x: float, y: float, z: float) -> None:
        """ translate the camera """
        self.translation[0] += x
        self.translation[1] += y
        self.translation[2] += z

    def handle_mouse_button(self, button: int, mode: int, x: int, y: int) -> None:
        """ Called when mouse button is pressed or released """
        width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = height - y  # invert y coordinate cuz OpenGL is inverted
        self.mouse_loc = (x, y)

        # do stuff depending on mode of button
        if mode == GLUT_DOWN:
            self.pressed = button
            if self.pressed == GLUT_RIGHT_BUTTON:  # do nothing if right button is pressed for now
                pass
            elif self.pressed == GLUT_LEFT_BUTTON: # pick
                self.trigger('pick', x, y)
            elif self.pressed == GLUT_WHEEL_UP: # scroll up
                self.translate(0, 0, 1)
            elif self.pressed == GLUT_WHEEL_DOWN:
                self.translate(0, 0, -1)
        else:  # Button has been released then.
            self.pressed = None
        glutPostRedisplay()

    def handle_mouse_motion(self, x: int, screen_y: int) -> None:
        """ Called when the mouse is moved """
        width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = height - screen_y  # invert y coordinate cuz OpenGL is inverted
        if self.pressed is not None:
            dx = x - self.mouse_loc[0]
            dy = y - self.mouse_loc[1]
            if self.pressed == GLUT_RIGHT_BUTTON and self.trackball is not None:
                # I'm not sure why we're tracking if trackball is not None, since it never should be, but w/e
                # if we pressed right button, drags trackball to new mouse location ?
                self.trackball.drag_to(self.mouse_loc[0], self.mouse_loc[1], dx, dy)
            elif self.pressed == GLUT_LEFT_BUTTON:
                self.trigger('move', x, y)
            elif self.pressed == GLUT_MIDDLE_BUTTON:
                self.translate(dx/60.0, dy/60.0, 0)
            glutPostRedisplay()
        self.mouse_loc = (x, y)

    def handle_keystroke(self, key, x: int, screen_y: int) -> None:
        """ Called when a key is pressed """
        width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = height - screen_y  # invert y coordinate cuz OpenGL is inverted
        if key == 's':  # place a sphere if press s
            self.trigger('place', 'sphere', x, y)
        elif key == 'c':  # place a cube if press c
            self.trigger('place', 'cube', x, y)
        elif key == GLUT_KEY_UP:  # scale up size
            self.trigger('scale', up=True)
        elif key == GLUT_KEY_DOWN:  # scale down size
            self.trigger('scale', up=False)
        elif key == GLUT_KEY_LEFT:  # rotate colour
            self.trigger('rotate_color', forward=True)
        elif key == GLUT_KEY_RIGHT:  # rotate colour other direction
            self.trigger('rotate_color', forward=False)
        glutPostRedisplay()

    def register_callback(self, action_name: str, func: callable) -> None:
        """ registers a function a certain action"""
        self.callbacks[action_name].append(func)

    def trigger(self, action_name: str, *args: Any, **kwargs: Any) -> None:
        """ Triggers/calls each function associated with action_name in the callbacks dictionary"""
        for func in self.callbacks[action_name]:
            func(*args, **kwargs)
