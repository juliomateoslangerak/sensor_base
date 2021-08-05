import board
import busio as io
import adafruit_ssd1306
from digitalio import DigitalInOut
from time import sleep

i2c = io.I2C(board.SCL, board.SDA)

reset_pin = DigitalInOut(board.D5) # any pin!

oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3d, reset=reset_pin)

sleep(.5)

oled.fill(1)
oled.show()
sleep(.5)

oled.fill(0)
oled.show()
sleep(.5)

for i in range(64):
    oled.pixel(i, i, 1)
    oled.show()

oled.fill(0)
oled.text('Hello', 0, 0, 1, size=2)
oled.text('World', 0, 30, 1, size=2)
oled.show()
