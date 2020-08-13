import framebuf
import logging

import machine

from SSD1306 import SSD1306_I2C

from abutton import Pushbutton

from . import positions, valuebuffer, bufferlib

pbm_dir = "/pbm"



class PBM(framebuf.FrameBuffer):
    def __init__(self, file: str):
        logging.debug("loading pbm from {}".format(file))
        with open("{}/{}.pbm".format(pbm_dir, file), 'rb') as f:
            f.readline()  # Magic number
            f.readline()  # Creator comment
            self.width, self.height = [int(v) for v in f.readline().split()]
            data = bytearray(f.read())
        super().__init__(data, self.width, self.height, framebuf.MONO_HLSB)


class Numeral(PBM):
    def __init__(self, num: str):
        super().__init__("numerals/{}".format(num))


class GUI(SSD1306_I2C):
    def __init__(self, width: int, height: int, i2c: machine.I2C):
        self.on = True
        self.buffer_type = framebuf.MONO_VLSB
        self.width = width
        self.height = height
        super().__init__(self.width, self.height, i2c)
        layout = self.gen_layout()
        self.blit(layout, *positions.get("ORIGIN"))
        self.show()
        powerbutton = Pushbutton(machine.Pin(23, machine.Pin.IN))
        powerbutton.press_func(self.toggle_oled)

    def set_value(self, value: float, kind: str):
        b = valuebuffer.ValueBuffer(value)
        self.blit(b, *positions.get(kind))
        self.show()

    def toggle_oled(self):
        if self.on:
            self.poweroff()
            self.on = False
        else:
            self.poweron()
            self.on = True

    def blit(self, fbuf: framebuf.FrameBuffer, x: int, y: int, key: int = None):
        logging.debug("blitting to {},{}".format(x, y))
        if key:
            super(GUI, self).blit(fbuf, x, y, key)
        else:
            super(GUI, self).blit(fbuf, x, y)

    def gen_layout(self):
        fb = bufferlib.buffer_factory(self.width, self.height, self.buffer_type)
        fb.blit(PBM("layout"), 0, 0)
        return fb
