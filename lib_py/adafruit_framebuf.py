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

from os import stat
import struct

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

    @staticmethod
    def fill_rect(framebuf, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments
        while height > 0:
            index = (y >> 3) * framebuf.stride + x
            offset = y & 0x07
            for w_w in range(width):
                framebuf.buf[index + w_w] = (
                    framebuf.buf[index + w_w] & ~(0x01 << offset)
                ) | ((color != 0) << offset)
            y += 1
            height -= 1



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

    def __init__(self, buf, width, height, stride=None):
        # pylint: disable=too-many-arguments
        self.buf = buf
        self.width = width
        self.height = height
        self.stride = stride
        self._font = None
        if self.stride is None:
            self.stride = width
        self.format = MVLSBFormat()
        # self._rotation = 0

    def fill(self, color):
        """Fill the entire FrameBuffer with the specified color."""
        self.format.fill(self, color)

    def fill_rect(self, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments, too-many-boolean-expressions
        self.rect(x, y, width, height, color, fill=True)



    # def pixel(self, x, y, color=None):
    #     """If ``color`` is not given, get the color value of the specified pixel. If ``color`` is
    #     given, set the specified pixel to the given color."""
    #     # if self.rotation == 1:
    #     #     x, y = y, x
    #     #     x = self.width - x - 1
    #     # if self.rotation == 2:
    #     #     x = self.width - x - 1
    #     #     y = self.height - y - 1
    #     # if self.rotation == 3:
    #     #     x, y = y, x
    #     #     y = self.height - y - 1
    #
    #     if x < 0 or x >= self.width or y < 0 or y >= self.height:
    #         return None
    #     if color is None:
    #         return self.format.get_pixel(self, x, y)
    #     self.format.set_pixel(self, x, y, color)
    #     return None
    #
    # pylint: disable=too-many-arguments

    def rect(self, x, y, width, height, color, *, fill=False):
        """Draw a rectangle at the given location, size and color. The ```rect``` method draws only
        a 1 pixel outline."""
        # pylint: disable=too-many-arguments
        # if self.rotation == 1:
        #     x, y = y, x
        #     width, height = height, width
        #     x = self.width - x - width
        # if self.rotation == 2:
        #     x = self.width - x - width
        #     y = self.height - y - height
        # if self.rotation == 3:
        #     x, y = y, x
        #     width, height = height, width
        #     y = self.height - y - height
        #
        # pylint: disable=too-many-boolean-expressions
        if (
                width < 1
                or height < 1
                or (x + width) <= 0
                or (y + height) <= 0
                or y >= self.height
                or x >= self.width
        ):
            return
        x_end = min(self.width - 1, x + width - 1)
        y_end = min(self.height - 1, y + height - 1)
        x = max(x, 0)
        y = max(y, 0)
        if fill:
            self.format.fill_rect(self, x, y, x_end - x + 1, y_end - y + 1, color)
        else:
            self.format.fill_rect(self, x, y, x_end - x + 1, 1, color)
            self.format.fill_rect(self, x, y, 1, y_end - y + 1, color)
            self.format.fill_rect(self, x, y_end, x_end - x + 1, 1, color)
            self.format.fill_rect(self, x_end, y, 1, y_end - y + 1, color)

    def text(self, string, x, y, color, *, font_name="font5x8.bin", size=1):
        """Place text on the screen in variables sizes. Breaks on \n to next line.

        Does not break on line going off screen.
        """
        # determine our effective width/height, taking rotation into account
        frame_width = self.width
        frame_height = self.height

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
            if 2 + 256 * self.font_width != stat(font_name)[6]:
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
