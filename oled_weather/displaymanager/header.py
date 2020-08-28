import collections

import framebuf

from .pbm import PBM


class Header(framebuf.FrameBuffer):
    icons = collections.OrderedDict()

    def __init__(self, _width, _height, _background: str = None):
        self.width = _width
        self.height = _height
        buffer = bytearray(_height * _width)
        super(Header, self).__init__(buffer, _width, _height, framebuf.MONO_VLSB)
        if _background:
            self.background = PBM("backgrounds/{}".format(_background))
            self.blit(self.background, 0, 0)

    def add_icon(self, name: str, visible=True):
        self.icons[name] = [visible, PBM("icons/{}".format(name))]

    def set_icon_visible(self, name, visible):
        self.icons[name][0] = visible

    def update(self):
        x = self.width
        for icon in self.icons.values():
            x -= icon[1].width
            if icon[0]:
                self.blit(icon[1], x, 0)
            else:
                self.fill_rect(x, 0, icon[1].width, icon[1].height, 0)
            x -= 2
