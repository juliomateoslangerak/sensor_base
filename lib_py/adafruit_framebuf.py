# SPDX-FileCopyrightText: <text> 2018 Kattni Rembor, Melissa LeBlanc-Williams
# and Tony DiCola, for Adafruit Industries.
# Original file created by Damien P. George </text>
#
# SPDX-License-Identifier: MIT

"""
`adafruit_framebuf`
====================================================

CircuitPython pure-python framebuf module, based on the micropython framebuf module.

Implementation Notes
--------------------

**Hardware:**

* `Adafruit SSD1306 OLED displays <https://www.adafruit.com/?q=ssd1306>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

__version__ = "1.4.7"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_framebuf.git"

import os
import struct

# Framebuf format constants:
MVLSB = 0  # Single bit displays (like SSD1306 OLED)


class MVLSBFormat:
    """MVLSBFormat"""

    @staticmethod
    def set_pixel(framebuf, x, y, color):
        """Set a given pixel to a color."""
        index = (y >> 3) * framebuf.stride + x
        offset = y & 0x07
        framebuf.buf[index] = (framebuf.buf[index] & ~(0x01 << offset)) | (
            (color != 0) << offset
        )

    @staticmethod
    def fill(framebuf, color):
        """completely fill/clear the buffer with a color"""
        if color:
            fill = 0xFF
        else:
            fill = 0x00
        for i in range(len(framebuf.buf)):
            framebuf.buf[i] = fill


class FrameBuffer:
    """FrameBuffer object.

    :param buf: An object with a buffer protocol which must be large enough to contain every
                pixel defined by the width, height and format of the FrameBuffer.
    :param width: The width of the FrameBuffer in pixel
    :param height: The height of the FrameBuffer in pixel
    :param buf_format: Specifies the type of pixel used in the FrameBuffer; permissible values
                        are listed under Constants below. These set the number of bits used to
                        encode a color value and the layout of these bits in ``buf``. Where a
                        color value c is passed to a method, c is  a small integer with an encoding
                        that is dependent on the format of the FrameBuffer.
    :param stride: The number of pixels between each horizontal line of pixels in the
                   FrameBuffer. This defaults to ``width`` but may need adjustments when
                   implementing a FrameBuffer within another larger FrameBuffer or screen. The
                   ``buf`` size must accommodate an increased step size.

    """

    def __init__(self, buf, width, height, buf_format=MVLSB, stride=None):
        # pylint: disable=too-many-arguments
        self.buf = buf
        self.width = width
        self.height = height
        self.stride = stride
        self._font = None
        if self.stride is None:
            self.stride = width
        if buf_format == MVLSB:
            self.format = MVLSBFormat()
        else:
            raise ValueError("invalid format")
        self._rotation = 0

    def fill(self, color):
        """Fill the entire FrameBuffer with the specified color."""
        self.format.fill(self, color)

    def pixel(self, x, y, color=None):
        """If ``color`` is not given, get the color value of the specified pixel. If ``color`` is
        given, set the specified pixel to the given color."""
        if self.rotation == 1:
            x, y = y, x
            x = self.width - x - 1
        if self.rotation == 2:
            x = self.width - x - 1
            y = self.height - y - 1
        if self.rotation == 3:
            x, y = y, x
            y = self.height - y - 1

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        if color is None:
            return self.format.get_pixel(self, x, y)
        self.format.set_pixel(self, x, y, color)
        return None

    def scroll(self, delta_x, delta_y):
        """shifts framebuf in x and y direction"""
        if delta_x < 0:
            shift_x = 0
            xend = self.width + delta_x
            dt_x = 1
        else:
            shift_x = self.width - 1
            xend = delta_x - 1
            dt_x = -1
        if delta_y < 0:
            y = 0
            yend = self.height + delta_y
            dt_y = 1
        else:
            y = self.height - 1
            yend = delta_y - 1
            dt_y = -1
        while y != yend:
            x = shift_x
            while x != xend:
                self.format.set_pixel(
                    self, x, y, self.format.get_pixel(self, x - delta_x, y - delta_y)
                )
                x += dt_x
            y += dt_y

    # pylint: disable=too-many-arguments
    def text(self, string, x, y, color, *, font_name="font5x8.bin", size=1):
        """Place text on the screen in variables sizes. Breaks on \n to next line.

        Does not break on line going off screen.
        """
        # determine our effective width/height, taking rotation into account
        frame_width = self.width
        frame_height = self.height
        if self.rotation == 1 or self.rotation == 3:
            frame_width, frame_height = frame_height, frame_width

        for chunk in string.split("\n"):
            if not self._font or self._font.font_name != font_name:
                # load the font!
                self._font = BitmapFont(font_name)
            width = self._font.font_width
            height = self._font.font_height
            for i, char in enumerate(chunk):
                char_x = x + (i * (width + 1)) * size
                if (
                    char_x + (width * size) > 0
                    and char_x < frame_width
                    and y + (height * size) > 0
                    and y < frame_height
                ):
                    self._font.draw_char(char, char_x, y, self, color, size=size)
            y += height * size

    # pylint: enable=too-many-arguments


# MicroPython basic bitmap font renderer.
# Author: Tony DiCola
# License: MIT License (https://opensource.org/licenses/MIT)
class BitmapFont:
    """A helper class to read binary font tiles and 'seek' through them as a
    file to display in a framebuffer. We use file access so we dont waste 1KB
    of RAM on a font!"""

    def __init__(self, font_name="font5x8.bin"):
        # Specify the drawing area width and height, and the pixel function to
        # call when drawing pixels (should take an x and y param at least).
        # Optionally specify font_name to override the font file to use (default
        # is font5x8.bin).  The font format is a binary file with the following
        # format:
        # - 1 unsigned byte: font character width in pixels
        # - 1 unsigned byte: font character height in pixels
        # - x bytes: font data, in ASCII order covering all 255 characters.
        #            Each character should have a byte for each pixel column of
        #            data (i.e. a 5x8 font has 5 bytes per character).
        self.font_name = font_name

        # Open the font file and grab the character width and height values.
        # Note that only fonts up to 8 pixels tall are currently supported.
        try:
            self._font = open(self.font_name, "rb")
            self.font_width, self.font_height = struct.unpack("BB", self._font.read(2))
            # simple font file validation check based on expected file size
            if 2 + 256 * self.font_width != os.stat(font_name)[6]:
                raise RuntimeError("Invalid font file: " + font_name)
        except OSError:
            print("Could not find font file", font_name)
            raise
        except OverflowError:
            # os.stat can throw this on boards without long int support
            # just hope the font file is valid and press on
            pass

    def deinit(self):
        """Close the font file as cleanup."""
        self._font.close()

    def __enter__(self):
        """Initialize/open the font file"""
        self.__init__()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """cleanup on exit"""
        self.deinit()

    def draw_char(
        self, char, x, y, framebuffer, color, size=1
    ):  # pylint: disable=too-many-arguments
        """Draw one character at position (x,y) to a framebuffer in a given color"""
        size = max(size, 1)
        # Don't draw the character if it will be clipped off the visible area.
        # if x < -self.font_width or x >= framebuffer.width or \
        #   y < -self.font_height or y >= framebuffer.height:
        #    return
        # Go through each column of the character.
        for char_x in range(self.font_width):
            # Grab the byte for the current column of font data.
            self._font.seek(2 + (ord(char) * self.font_width) + char_x)
            try:
                line = struct.unpack("B", self._font.read(1))[0]
            except RuntimeError:
                continue  # maybe character isnt there? go to next
            # Go through each row in the column byte.
            for char_y in range(self.font_height):
                # Draw a pixel for each bit that's flipped on.
                if (line >> char_y) & 0x1:
                    framebuffer.fill_rect(
                        x + char_x * size, y + char_y * size, size, size, color
                    )

    def width(self, text):
        """Return the pixel width of the specified text message."""
        return len(text) * (self.font_width + 1)
