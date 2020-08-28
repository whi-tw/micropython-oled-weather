import framebuf

import logging


class PBM(framebuf.FrameBuffer):
    def __init__(self, file: str):
        logging.debug("loading pbm from {}".format(file))
        with open("{}/{}.pbm".format("/pbm", file), 'rb') as f:
            f.readline()  # Magic number
            f.readline()  # Creator comment
            self.width, self.height = [int(v) for v in f.readline().split()]
            data = bytearray(f.read())
        super().__init__(data, self.width, self.height, framebuf.MONO_HLSB)
