import pyglet
import matplotlib.pyplot as plt

from .core.obj import Obj
from .core.user import User

from .core.information import Timer, ImageView, Text


def get_layout(window_width, window_height, show=False):
    fig = plt.figure(figsize=(5, 5))
    ax = {}
    # Setup your layout here
    grid = (4, 6)
    ax['main'] = plt.subplot2grid(grid, (0, 0), colspan=4, rowspan=3, fig=fig)
    ax['cont'] = plt.subplot2grid(grid, (3, 0), colspan=4, rowspan=1, fig=fig)
    ax['info'] = plt.subplot2grid(grid, (3, 4), colspan=2, fig=fig)
    ax['pan1'] = plt.subplot2grid(grid, (0, 4), fig=fig)
    ax['pan2'] = plt.subplot2grid(grid, (1, 4), fig=fig)
    ax['pan3'] = plt.subplot2grid(grid, (2, 4), fig=fig)
    ax['pan4'] = plt.subplot2grid(grid, (0, 5), fig=fig)
    ax['pan5'] = plt.subplot2grid(grid, (1, 5), fig=fig)
    ax['pan6'] = plt.subplot2grid(grid, (2, 5), fig=fig)

    # Cleaning and setting up the padding
    for key in ax.keys():
        ax[key].text(0.5, 0.5, key, va="center", ha="center")
        for tl in ax[key].get_xticklabels() + ax[key].get_yticklabels():
            tl.set_visible(False)
        # Add window size
        setattr(ax[key], 'window_width', window_width)
        setattr(ax[key], 'window_height', window_height)

    # Adjust the paddings around the sub plots
    plt.subplots_adjust(top=0.99, left=0.01, bottom=0.01, right=0.99)
    fig.subplots_adjust(wspace=0.05, hspace=0.05)

    if show:
        plt.setp(plt.gcf().get_axes(), xticks=[], yticks=[])
        plt.show()
    return ax


class MainGUI(pyglet.window.Window):
    def __init__(self, width, height, config):
        super().__init__(width, height)
        ax = get_layout(width, height, show=False)

        # Obj path
        path = '/'.join([
            config['urdf_data_path'], config['simulation']['map_to_use'],
            'meshes/map.obj'
        ])

        self.main = Obj(ax['main'], path)
        self.panels = []
        for i in range(6):
            key = 'pan' + str(i + 1)
            self.panels.append(Obj(ax[key], path))

        self.info = Timer(ax['info'])
        self.enemy_info = Text(ax['info'])
        self.control = ImageView(ax['cont'])

        self.user = User([
            self.main, self.panels[0], self.panels[1], self.panels[2],
            self.panels[3], self.panels[4], self.panels[5]
        ])
        self.alive = True
        return None

    def on_close(self):
        self.alive = False

    def push_events(self):
        # Push handlers
        pyglet.clock.tick()
        self.push_handlers(self.user)
        self.dispatch_events()

        # Flush all the handlers
        self.pop_handlers()

        # Draw
        self.flip()

    def run(self):
        while self.alive:
            self.clear()

            # Update window
            self.main.update()
            for panel in self.panels:
                panel.update()

            self.control.update()
            self.info.update()
            self.enemy_info.update('Enemy Attack', 0, 100)

            # Update the user
            self.user.draw()
            self.main.update()

            # time.sleep(2)

            self.push_events()
