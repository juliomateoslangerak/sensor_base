# SPDX-FileCopyrightText: 2016 Damien P. George
# SPDX-FileCopyrightText: 2017 Scott Shawcroft for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Carter Nelson
# SPDX-FileCopyrightText: 2019 Roy Hooper
#
# SPDX-License-Identifier: MIT

"""
`neopixel` - NeoPixel strip driver
====================================================

* Author(s): Damien P. George, Scott Shawcroft, Carter Nelson, Rose Hooper
"""

import digitalio
from neopixel_write import neopixel_write

try:
    import adafruit_pixelbuf
except ImportError:
    try:
        import _pixelbuf as adafruit_pixelbuf
    except ImportError:
        import adafruit_pypixelbuf as adafruit_pixelbuf


__version__ = "6.2.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel.git"


# Pixel color order constants
GRBW = "GRBW"
"""Green Red Blue White"""


class NeoPixel(adafruit_pixelbuf.PixelBuf):
    """
    A sequence of neopixels.

    :param ~microcontroller.Pin pin: The pin to output neopixel data on.
    :param int n: The number of neopixels in the chain
    :param int bpp: Bytes per pixel. 3 for RGB and 4 for RGBW pixels.
    :param float brightness: Brightness of the pixels between 0.0 and 1.0 where 1.0 is full
      brightness
    :param bool auto_write: True if the neopixels should immediately change when set. If False,
      `show` must be called explicitly.
    :param str pixel_order: Set the pixel color channel order. GRBW is set by default.

    Example for Circuit Playground Express:

    .. code-block:: python

        import neopixel
        from board import *

        RED = 0x100000 # (0x10, 0, 0) also works

        pixels = neopixel.NeoPixel(NEOPIXEL, 10)
        for i in range(len(pixels)):
            pixels[i] = RED

    Example for Circuit Playground Express setting every other pixel red using a slice:

    .. code-block:: python

        import neopixel
        from board import *
        import time

        RED = 0x100000 # (0x10, 0, 0) also works

        # Using ``with`` ensures pixels are cleared after we're done.
        with neopixel.NeoPixel(NEOPIXEL, 10) as pixels:
            pixels[::2] = [RED] * (len(pixels) // 2)
            time.sleep(2)

    .. py:method:: NeoPixel.show()

        Shows the new colors on the pixels themselves if they haven't already
        been autowritten.

        The colors may or may not be showing after this function returns because
        it may be done asynchronously.

    .. py:method:: NeoPixel.fill(color)

        Colors all pixels the given ***color***.

    .. py:attribute:: brightness

        Overall brightness of the pixel (0 to 1.0)

    """

    def __init__(
        self, pin, n, *, brightness=1.0, auto_write=True, pixel_order=GRBW
    ):

        self._power = None
        super().__init__(
            n, brightness=brightness, byteorder=pixel_order, auto_write=auto_write
        )

        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT

    def deinit(self):
        """Blank out the NeoPixels and release the pin."""
        self.fill(0)
        self.show()
        self.pin.deinit()
        if self._power:
            self._power.deinit()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.deinit()

    def __repr__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"

    @property
    def n(self):
        """
        The number of neopixels in the chain (read-only)
        """
        return len(self)

    def _transmit(self, buffer):
        neopixel_write(self.pin, buffer)
