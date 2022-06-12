class User:
    def __init__(self, scenes):
        self.w = 0
        self.h = 0
        if not isinstance(scenes, list):
            scenes = [scenes]
        self.scenes = scenes
        return None

    def do_claim(self):
        return 0, 0

    def on_mouse_release(self, x, y, button, modifiers):
        for scene in self.scenes:
            try:
                scene.on_mouse_release(x, y, button, modifiers)
            except AttributeError:
                pass

    def on_key_release(self, symbol, modifiers):
        for scene in self.scenes:
            try:
                scene.on_key_release(symbol, modifiers)
            except AttributeError:
                pass

    def on_key_press(self, symbol, modifiers):
        for scene in self.scenes:
            try:
                scene.on_key_press(symbol, modifiers)
            except AttributeError:
                pass

    def on_mouse_motion(self, x, y, dx, dy):
        for scene in self.scenes:
            try:
                scene.on_mouse_motion(x, y, dx, dy)
            except AttributeError:
                pass

    def on_mouse_press(self, x, y, button, modifiers):
        for scene in self.scenes:
            try:
                scene.on_mouse_press(x, y, button, modifiers)
            except AttributeError:
                pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        for scene in self.scenes:
            try:
                if scene.rect.is_inside(x, y):
                    scene.on_mouse_scroll(x, y, scroll_x, scroll_y)
            except AttributeError:
                pass

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        for scene in self.scenes:
            try:
                if scene.rect.is_inside(x, y):
                    scene.on_mouse_drag(x, y, dx, dy, button, modifiers)
            except AttributeError:
                pass

    def draw(self):
        for scene in self.scenes:
            try:
                scene.do_draw()
            except AttributeError:
                pass
