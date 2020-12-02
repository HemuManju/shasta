import pyglet
import pyglet.gl as gl

import ctypes
lightfv = ctypes.c_float * 4


class ViewPort(object):
    def __init__(self, ax):
        self._b_box = ax.get_position()

        # For mac the graphiscs need to be scaled by 2
        self._m_scale = 2

        # Window size
        self._win_width = ax.window_width * self._m_scale
        self._win_height = ax.window_height * self._m_scale

        # Set up all the dimensions
        self.setup_bounding_box()

    def set_viewport(self):
        # Set viewport
        gl.glViewport(self.x0, self.y0, self.width, self.height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()

        # Set projection
        gl.glOrtho(-self.width / (2), self.width / (2), -self.height / (2),
                   self.height / (2), -1000, 1000)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, lightfv(1.0, 1., 1.0, 0.0))
        return None

    def setup_bounding_box(self):
        self.x0 = int(self._b_box.x0 * self._win_width)
        self.y0 = int(self._b_box.y0 * self._win_height)

        self.x1 = int(self._b_box.x1 * self._win_width)
        self.y1 = int(self._b_box.y1 * self._win_height)

        # Setup origin
        self.origin_x = self.x0
        self.origin_y = self.y0

        # Setup width and height
        self.width = self.x1 - self.x0
        self.height = self.y1 - self.y0
        return None

    def is_inside(self, x, y):
        if (self.x0 / self._m_scale < x and x < self.x1 / self._m_scale):
            if (self.y0 / self._m_scale < y and y < self.y1 / self._m_scale):
                return True
        return False

    def get_origin(self):
        return (self.x0, self.y0)

    def get_size(self):
        raise (self.width, self.height)


def create_window(width, height):
    try:
        config = pyglet.gl.Config(sample_buffers=1,
                                  samples=4,
                                  depth_size=24,
                                  double_buffer=True)
        window = pyglet.window.Window(config=config,
                                      width=width,
                                      height=height)
    except pyglet.window.NoSuchConfigException:
        config = pyglet.gl.Config(double_buffer=True)
        window = pyglet.window.Window(config=config,
                                      width=width,
                                      height=height)

    @window.event
    def on_key_press(symbol, modifiers):
        if modifiers == 0:
            if symbol == pyglet.window.key.Q:
                window.close()

    return window
