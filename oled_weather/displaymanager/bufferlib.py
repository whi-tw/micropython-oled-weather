import framebuf


def buffer_factory(width: int, height: int, buffer_type: int = None, buffer: bytearray = None):
    if buffer is None:
        buffer = bytearray(height // 8 * width)
    if buffer_type is None:
        buffer_type = framebuf.MONO_VLSB
    return framebuf.FrameBuffer(buffer, width, height, buffer_type)
