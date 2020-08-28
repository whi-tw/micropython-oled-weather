import framebuf

import logging

from . import bufferlib


class ScreenConfig:
    background = None

    def __init__(self, name: str, _vars: dict):
        try:
            self.background = PBM("backgrounds/{}".format(name))
        except OSError:
            pass
        self.vars = _vars


class Screen(framebuf.FrameBuffer):
    def __init__(self, _width, _height, _config: ScreenConfig):
        self.width = _width
        self.height = _height
        self.config = _config
        buffer = bytearray(_height // 8 * _width)
        super(Screen, self).__init__(buffer, _width, _height, framebuf.MONO_VLSB)
        if _config.background:
            self.blit(self.config.background, 0, 0)

    def update(self, data: dict):
        for key, value in data.items():
            if key in self.config.vars.keys():
                # logging.info("printing {} to {} {}".format(value, self.config.vars[key][0], self.config.vars[key][1]))
                # self.fill_rect(self.config.vars[key][0], self.config.vars[key][1], 8*len(value), 8, 0)
                x = self.config.vars[key][0]
                y = self.config.vars[key][1]
                a = self.config.vars[key][2]
                if a == "l":
                    for i, char in enumerate(value):
                        bitmap, h, w = self.config.vars[key][3].get_ch(char)
                        c = framebuf.FrameBuffer(bytearray(bitmap), w, h, framebuf.MONO_HLSB)
                        self.blit(c, x, y)
                        x += w
                        del bitmap, c, h, w
                elif a == "r":
                    for i, char in reversed(list(enumerate(value))):
                        bitmap, h, w = self.config.vars[key][3].get_ch(char)
                        c = framebuf.FrameBuffer(bytearray(bitmap), w, h, framebuf.MONO_HLSB)
                        self.blit(c, x-w, y)
                        x -= w
                        del bitmap, c, h, w
                # self.text(value, self.config.vars[key][0], self.config.vars[key][1])


class PBM(framebuf.FrameBuffer):
    def __init__(self, file: str):
        logging.debug("loading pbm from {}".format(file))
        with open("{}/{}.pbm".format("/pbm", file), 'rb') as f:
            f.readline()  # Magic number
            f.readline()  # Creator comment
            self.width, self.height = [int(v) for v in f.readline().split()]
            data = bytearray(f.read())
        super().__init__(data, self.width, self.height, framebuf.MONO_HLSB)
