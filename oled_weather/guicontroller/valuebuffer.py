import framebuf

from . import numerals, bufferlib


def float_to_chars(f: float) -> list:
    if f == 100:
        s = "100"
    elif f == -100:
        s = "-100"
    elif f == 0:
        s = "0"
    else:
        s = "{:4.1f}".format(f)
    return list(s)


class ValueBuffer(framebuf.FrameBuffer):
    def __init__(self, value: float):
        self.width = 27
        self.height = 8
        self.buffer = bytearray(self.height // 8 * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)

        self.actual_width = 0
        if type(value) == int:
            value = float(value)
        self.value = value
        self.value_chars = float_to_chars(self.value)
        self.value_buffers = []
        self.get_numeral_objects()
        self.calc_buffer_width()
        self.blit_buffer()

        width_diff = self.width - self.actual_width
        if width_diff > 0:
            self.scroll(width_diff, 0)
            self.fill_rect(0, 0, width_diff, self.height, 0)

    def get_numeral_objects(self):
        for c in self.value_chars:
            if c == " ":
                self.value_buffers.append(7)
            elif c in numerals.char_mapping:
                self.value_buffers.append(numerals.get(c))
            else:
                pass

    def calc_buffer_width(self):
        for num in self.value_buffers:
            if type(num) == numerals.Numeral:
                self.actual_width += num.width
            else:
                self.actual_width += num

    def blit_buffer(self):
        x = 0
        for b in self.value_buffers:
            if type(b) == numerals.Numeral:
                self.blit(b, x, 0)
                x += b.width
            else:
                x += b
