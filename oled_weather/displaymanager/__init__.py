import framebuf
import logging

import machine

import uasyncio as asyncio

from SSD1306 import SSD1306_I2C

from aswitch import Pushbutton

from .screen import Screen, ScreenConfig
from .header import Header
from .datamanager import DataManager


class DisplayManager(SSD1306_I2C):
    screens = []
    superscreen = None
    header = None
    current_screen = None
    can_transition = False
    screen_x = 0

    def __init__(self, width: int, height: int, i2c: machine.I2C, button: machine.Pin, datamanager, header_height=0):
        self.on = True
        self.buffer_type = framebuf.MONO_VLSB
        self.width = width
        self.height = height
        self.header_height = header_height
        self.body_height = height - header_height
        if header_height:
            self.screen_x = self.header_height + 1
        super().__init__(self.width, self.height, i2c)
        self.show()
        powerbutton = Pushbutton(button, True)
        # powerbutton.double_func()
        powerbutton.long_func(self.toggle_oled)
        powerbutton.release_func(self.next_screen)
        self.datamanager = datamanager

    def start(self):
        if not self.screens:
            return
        self.current_screen = 0
        if len(self.screens) > 1:
            self.can_transition = True
        loop = asyncio.get_event_loop()
        loop.create_task(self.draw_loop())

    async def draw_loop(self):
        while True:
            if self.on:
                if self.header:
                    self.header.update()
                    self.blit(self.header, 0, 0)
                if self.screens:
                    self.screens[self.current_screen].update(self.datamanager.get())
                    self.blit(self.screens[self.current_screen], 0, self.screen_x)
                self.show()
            await asyncio.sleep_ms(1000)

    def next_screen(self):
        if not self.can_transition:
            logging.debug("not transitioning")
            return False
        logging.debug("transitioning")
        next_screen_idx = self.current_screen + 1
        if next_screen_idx > len(self.screens) - 1:
            next_screen_idx = 0
        self.current_screen = next_screen_idx

    def toggle_oled(self):
        if self.on:
            logging.debug("screen toggled off")
            self.poweroff()
            self.on = False
        else:
            logging.debug("screen toggled on")
            self.poweron()
            self.on = True

    def blit(self, fbuf: framebuf.FrameBuffer, x: int, y: int, key: int = None):
        logging.debug("blitting to {},{}".format(x, y))
        if key:
            super(DisplayManager, self).blit(fbuf, x, y, key)
        else:
            super(DisplayManager, self).blit(fbuf, x, y)

    def screen_factory(self, config: ScreenConfig):
        return Screen(self.width, ((self.body_height + 7) & (-8)), config)  # round height to nearest multiple of 8

    def add_screen(self, s: Screen):
        self.screens.append(s)

    def set_header(self, _background: str = None):
        self.header = Header(self.width, self.header_height, _background)
