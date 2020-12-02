import pywavefront
import pyglet
from pyglet.window import key, mouse
import pyglet.gl as gl
import numpy as np
from pywavefront import visualization

from .shape_utils import Sphere
from .utils import ViewPort

import ctypes
lightfv = ctypes.c_float * 4


class Obj():
    def __init__(self, ax, obj_path):
        # Setup viewport
        self.rect = ViewPort(ax)

        # Parameters
        self.rotation_x = 90
        self.rotation_y = 0
        self.x = 0
        self.y = 0
        self.zoom_level = 4

        self.meshes = pywavefront.Wavefront(obj_path)
        self.spheres = []
        t = np.linspace(0, 2 * np.pi, 10)

        # Just for plotting
        for i in range(10):
            x = 0 + 5 * np.cos(t[i])
            y = 0 + 5 * np.sin(t[i])
            self.spheres.append(Sphere(x, y=y, z=5.0, color=(0, 0, 1, 0)))

        for i in range(10):
            x = 20 + 5 * np.cos(t[i])
            y = 5 + 5 * np.sin(t[i])
            self.spheres.append(Sphere(x, y=y, z=5.0, color=(1, 0, 0, 0)))

        for i in range(10):
            x = -40 + 3 * np.cos(t[i])
            y = -70 + 3 * np.sin(t[i])
            self.spheres.append(Sphere(x, y=y, z=5.0, color=(1, 0, 0, 0)))

        t = np.linspace(0, 2 * np.pi, 5)
        for i in range(5):
            x = -30 + 3 * np.cos(t[i])
            y = -50 + 3 * np.sin(t[i])
            self.spheres.append(Sphere(x, y=y, z=5.0, color=(0, 0, 1, 0)))

        # Drawing
        self.w = 0
        self.h = 0
        self.vertex_list = None
        self.mouse_pos = []

        self.active = False

        return None

    def apply_transformation(self):
        self.rect.set_viewport()

        # Translation
        gl.glTranslated(self.x, self.y, 0)

        # Scale
        gl.glScaled(self.zoom_level, self.zoom_level, 1)

        # Rotation
        gl.glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        gl.glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
        return None

    def prepare_projection(self):
        self.apply_transformation()
        gl.glRotatef(90, 1, 0, 0)

    def convert_to_obj_coordinates(self, x, y):
        x = int(x) * self.rect._m_scale
        y = int(y) * self.rect._m_scale
        pmat = (gl.GLdouble * 16)()
        mvmat = (gl.GLdouble * 16)()
        viewport = (gl.GLint * 4)()

        # Model, projection and viewport matrices
        gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX, mvmat)
        gl.glGetDoublev(gl.GL_PROJECTION_MATRIX, pmat)
        gl.glGetIntegerv(gl.GL_VIEWPORT, viewport)

        # Unproject
        point = [gl.GLdouble() for _ in range(3)]
        gl.gluUnProject(x, y, 1, mvmat, pmat, viewport, *point)
        obj_coord = [v.value for v in point]
        return obj_coord[0:2]

    def pan_rotate(self, x, y, dx, dy, button, modifiers):
        # Shifting
        if button is mouse.RIGHT:
            if modifiers is key.MOD_SHIFT:
                gl.glEnable(gl.GL_DEPTH_TEST)
                self.rotation_x -= dy
                self.rotation_y += dx
                if self.rotation_x < 0:
                    self.rotation_x = 0
            else:
                self.x += self.rect._m_scale * dx
                self.y += self.rect._m_scale * dy

    def on_key_press(self, symbol, modifiers):
        if symbol == key.R:
            self.rotation_x = 90
            self.rotation_y = 0
            self.x = 0
            self.y = 0
            self.zoom_level = 4
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        return None

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.zoom_level += scroll_y
        if self.zoom_level < 4:
            self.zoom_level = 4
        elif self.zoom_level > 15:
            self.zoom_level = 15

    def on_mouse_release(self, x, y, button, modifiers):
        self.w, self.h = 0, 0
        self.mouse_pos = []
        self.vertex_list = None

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self.rect.is_inside(x, y):
            self.active = True

            # Drawing with user
            if button is mouse.LEFT:
                self.prepare_projection()
                pos = self.convert_to_obj_coordinates(x, y)
                self.mouse_pos.append(pos)
                x, y = self.mouse_pos[0][0], self.mouse_pos[0][1]
                self.w += (self.rect._m_scale * dx) / self.zoom_level
                self.h += (self.rect._m_scale * dy) / self.zoom_level
                z = 500
                gl.glLineWidth(5)
                self.vertex_list = pyglet.graphics.vertex_list(
                    4, ('v3f', (x, y, z, x + self.w, y, z, x + self.w,
                                y - self.h, z, x, y - self.h, z)),
                    ('c3B', (0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0, 255)))

        else:
            self.active = False

        # Obj movement
        self.pan_rotate(x, y, dx, dy, button, modifiers)

    def do_draw(self):
        # Draw OBJ
        self.apply_transformation()
        visualization.draw(self.meshes)

        if self.active:
            self.prepare_projection()
            if self.vertex_list is not None:
                self.vertex_list.draw(gl.GL_LINE_LOOP)

    def update(self):
        # Draw OBJ
        self.apply_transformation()
        visualization.draw(self.meshes)

        # # Draw UxV
        for i, sphere in enumerate(self.spheres):
            sphere.draw()
