from pathlib import Path
import pyglet
from pyglet import gl

from .utils import ViewPort


class Timer():
    def __init__(self, ax):
        self.rect = ViewPort(ax)
        self.label = pyglet.text.Label('00:00',
                                       font_size=54,
                                       x=0,
                                       y=self.rect.origin_y // 2 //
                                       self.rect._m_scale,
                                       anchor_x='center',
                                       anchor_y='center')
        self.reset()

    def prepare_projection(self):
        self.rect.set_viewport()

    def reset(self):
        self.time = 0
        self.running = True
        self.label.text = '00:00'
        self.label.color = (255, 255, 255, 255)

    def update(self):
        if self.running:
            self.time += 1 / 60
            m, s = divmod(self.time, 60)
            self.label.text = 'Time : ' + '%02d:%02d' % (m, s)
            if m >= 5:
                self.label.color = (180, 0, 0, 255)
                self.running = False
        self.prepare_projection()
        self.label.draw()


class Text():
    def __init__(self, ax):
        self.rect = ViewPort(ax)
        self.label = pyglet.text.Label('00:00',
                                       font_size=54,
                                       x=0,
                                       y=self.rect.origin_y // 2 //
                                       self.rect._m_scale,
                                       anchor_x='center',
                                       anchor_y='center')

        self.reset()

    def prepare_projection(self):
        self.rect.set_viewport()

    def reset(self):
        self.time = 0
        self.running = True
        self.label.text = 'Text'
        self.label.color = (255, 255, 255, 255)

    def update(self, text=None, x_pos=None, y_pos=None):
        if text is not None:
            self.label.color = (180, 0, 0, 255)
            self.label.text = text
            self.label.x = x_pos
            self.label.y = y_pos
            self.prepare_projection()
            self.label.draw()


class ImageView():
    def __init__(self, ax):
        self.rect = ViewPort(ax)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER,
                           gl.GL_NEAREST)

        path = Path(__file__).parents[1] / 'images/controls.png'

        image = pyglet.image.load(path)
        self.scale = 2.0
        self.image_sprite = pyglet.sprite.Sprite(image,
                                                 x=-image.width // 2,
                                                 y=-image.height // 2)

    def prepare_projection(self):
        self.rect.set_viewport()
        gl.glScaled(self.scale, self.scale, 1)

    def update(self):
        self.prepare_projection()
        self.image_sprite.draw()
