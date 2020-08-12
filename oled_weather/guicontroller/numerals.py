import framebuf

char_mapping = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-", "."]
buffer_type = framebuf.MONO_HLSB
numerals = [
    bytearray(b'8DTTTD8'), 7, 7,
    bytearray(b'\x10p\x10\x10\x10\x10|'), 7, 7,
    bytearray(b'8D\x04\x08\x10 |'), 7, 7,
    bytearray(b'x\x04\x048\x04\x04x'), 7, 7,
    bytearray(b'\x08\x18(H|\x08\x08'), 7, 7,
    bytearray(b'|@x\x04\x04D8'), 7, 7,
    bytearray(b'8D@xDD8'), 7, 7,
    bytearray(b'|D\x04\x08\x10  '), 7, 7,
    bytearray(b'8DD8DD8'), 7, 7,
    bytearray(b'8DD<\x04\x080'), 7, 7,
    bytearray(b'\x00\x00\x00p\x00\x00\x00'), 4, 7,
    bytearray(b'\x00\x00\x00\x00\x00\x00@'), 3, 7]


class Numeral(framebuf.FrameBuffer):
    def __init__(self, buffer, width, height):
        self.width = width
        self.height = height
        super().__init__(buffer, width, height, buffer_type)


def get(char: str) -> Numeral:
    try:
        index = char_mapping.index(char, )
    except ValueError:
        return None
    index *= 3
    return Numeral(*numerals[index:index + 3])
