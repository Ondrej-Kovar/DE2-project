"""
MicroPython SH1106 OLED driver (128x64) via I2C.
Compatible with standard framebuf API.
"""

from machine import I2C
import framebuf

# Constants
SET_CONTRAST = 0x81
SET_NORM_INV = 0xA6
SET_DISP = 0xAE
SET_SCAN_DIR = 0xC0
SET_SEG_REMAP = 0xA0
LOW_COLUMN_ADDRESS = 0x00
HIGH_COLUMN_ADDRESS = 0x10
SET_PAGE_ADDRESS = 0xB0

class SH1106_I2C(framebuf.FrameBuffer):
    """
    SH1106 128x64 OLED display driver over I2C bus.
    Extends MicroPython's built-in framebuf.FrameBuffer.
    """

    def __init__(self, width: int = 128, height: int = 64, i2c: I2C = None, addr: int = 0x3C, rotate: int = 0):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.rotate = rotate
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def write_cmd(self, cmd: int):
        self.i2c.writeto(self.addr, bytearray([0x80, cmd]))

    def write_data(self, buf):
        self.i2c.writeto(self.addr, b'\x40' + buf)

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00,           # off
            0xD5, 0x80,                # clock div
            0xA8, self.height - 1,     # multiplex
            0xD3, 0x00,                # display offset
            0x40,                      # start line 0
            0xAD, 0x8B,                # charge pump
            0x33,                      # pump voltage
            SET_SEG_REMAP | 0x01,      # reverse mapping
            SET_SCAN_DIR | 0x08,       # reverse scan
            0xDA, 0x12,                # com pins
            SET_CONTRAST, 0x80,        # contrast
            0xD9, 0x22,                # pre-charge
            0xDB, 0x35,                # vcomh
            SET_NORM_INV | 0x00,       # normal
            SET_DISP | 0x01            # turn on
        ):
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def show(self):
        """Send memory frame buffer to OLED display."""
        for page in range(self.pages):
            self.write_cmd(SET_PAGE_ADDRESS | page)
            self.write_cmd(LOW_COLUMN_ADDRESS | 2)     # SH1106 offset is 2 pixels
            self.write_cmd(HIGH_COLUMN_ADDRESS | 0)
            page_slice = self.buffer[page * self.width:(page + 1) * self.width]
            self.write_data(page_slice)

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast: int):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast & 0xFF)
