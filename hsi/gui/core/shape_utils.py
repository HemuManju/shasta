import pyglet
import math
from pyglet import gl

import ctypes
lightfv = ctypes.c_float * 4


def create_window(width, height, resize=False):
    try:
        config = pyglet.gl.Config(sample_buffers=1,
                                  samples=4,
                                  depth_size=24,
                                  double_buffer=True)
        window = pyglet.window.Window(config=config,
                                      width=width,
                                      height=height,
                                      resizable=resize)
    except pyglet.window.NoSuchConfigException:
        config = pyglet.gl.Config(double_buffer=True)
        window = pyglet.window.Window(config=config,
                                      width=width,
                                      height=height,
                                      resizable=resize)

    @window.event
    def on_key_press(symbol, modifiers):
        if modifiers == 0:
            if symbol == pyglet.window.key.Q:
                window.close()

    return window


class Point2d(object):
    """
    Represents a point in 2 dimensions.
    """
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class BaseObject(object):
    """
    Represents an item in the virtual world.
    """
    def __init__(self, color):
        self.tx = self.ty = self.tz = 0
        self.rx = self.ry = self.rz = 0
        self.color = color

    def enable_lightning(self):
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_BLEND)
        # gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, lightfv(50, 50, 50, 1))
        # gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, lightfv(0.8, 1, 0.8, 1))
        gl.glLightf(gl.GL_LIGHT0, gl.GL_CONSTANT_ATTENUATION, 0.1)
        gl.glLightf(gl.GL_LIGHT0, gl.GL_LINEAR_ATTENUATION, 0.05)
        gl.glEnable(gl.GL_LIGHT0)
        return

    def before_draw(self):
        """
        Sets the position, rotation, and color of the item before it is drawn.
        """
        # self.enable_lightning()
        # sets the position
        # gl.glLoadIdentity()
        gl.glTranslatef(self.tx, self.ty, self.tz)

        # sets the rotation
        gl.glRotatef(self.rx, 1, 0, 0)
        gl.glRotatef(self.ry, 0, 1, 0)
        gl.glRotatef(self.rz, 0, 0, 1)

        # sets the color
        gl.glColor4f(*self.color)

        # Clear any previous transformations
        gl.glPushMatrix()


class Rectangle(BaseObject):
    """
    Represents a rectangle in the virtual world.
    """
    def __init__(self, x, y, width, height, color):
        super(Rectangle, self).__init__(color)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def left(self):
        """
        Returns left end of the rectangle.
        """

        return self.x

    @property
    def right(self):
        """
        Returns the right end of the rectangle.
        """

        return self.x + self.width

    @property
    def bottom(self):
        """
        Returns the lower end of the rectangle.
        """

        return self.y

    @property
    def top(self):
        """
        Returns the upper end of the rectangle.
        """

        return self.y + self.height

    def draw(self):
        """
        Draws a rectangle.
        """
        self.before_draw()

        # vertices in counter-clockwise
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex3f(self.x + self.width, self.y + self.height, 0)
        gl.glVertex3f(self.x, self.y + self.height, 0)
        gl.glVertex3f(self.x, self.y, 0)
        gl.glVertex3f(self.x + self.width, self.y, 0)
        gl.glEnd()


class Circle(BaseObject):
    """
    Represents a circle in the virtual world.
    """
    def __init__(self, x, y, radius, color):
        super(Circle, self).__init__(color)
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self):
        """
        Draws a circle.
        """
        self.before_draw()

        # vertices in counter-clockwise
        gl.glBegin(gl.GL_TRIANGLE_FAN)
        for angle in range(0, 360, 10):
            rads = math.radians(angle)
            s = self.radius * math.sin(rads)
            c = self.radius * math.cos(rads)
            gl.glVertex3f(self.x + c, self.y + s, -10)
        gl.glEnd()


class Cube(BaseObject):
    """
    Represents a circle in the virtual world.
    """
    def __init__(self, x, y, radius, color):
        super(Sphere, self).__init__(color)
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self):
        """
        Draws a circle.
        """
        self.before_draw()

        sphere = gl.gluNewQuadric()
        gl.glTranslatef(self.x, self.y, -10)
        gl.gluSphere(sphere, self.radius, 25, 25)


class Sphere(BaseObject):
    """
    Represents a circle in the virtual world.
    """
    def __init__(self, x, y, z=50, radius=1, color=(0, 0, 1, 0)):
        super(Sphere, self).__init__(color)
        self.x = x
        # Need to swap y and z (y is up)
        self.y = z
        self.z = y
        self.radius = radius
        self.sphere = gl.gluNewQuadric()

    def draw(self):
        """
        Draws a circle.
        """
        self.before_draw()

        # Draw
        gl.glTranslatef(self.x, self.y, self.z)
        gl.gluSphere(self.sphere, self.radius, 25, 25)

        # Restore the transformation matrix
        gl.glPopMatrix()
