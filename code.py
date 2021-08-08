# Import generic tools
from board import LED, D5, SCL, SDA, TX, RX, A0, A1, A2, SCK, MOSI, MISO, RFM69_CS, RFM69_RST
from busio import I2C, UART  #, SPI
from digitalio import DigitalInOut, Direction, Pull
from time import monotonic, sleep

# Import PM libs
from adafruit_pm25.uart import PM25_UART

# Import screen libs
from adafruit_ssd1306 import SSD1306_I2C

# Import radio libs
from adafruit_rfm69 import RFM69

# # Import temperature libs
# from adafruit_onewire.bus import OneWireBus
# from adafruit_ds18x20 import DS18X20
#
# Import neopixels libs
# from neopixel import NeoPixel

# Turn on status led
status_led = DigitalInOut(LED)
status_led.direction = Direction.OUTPUT
status_led.value = True

try:
	# Define pins and config
	radio_clock_pin = SCK
	radio_mosi_pin = MOSI
	radio_miso_pin = MISO
	radio_cs_pin = RFM69_CS
	radio_reset_pin = RFM69_RST
	radio_freq = 868.0

	# temp_data_pin = board.D9
	# temp_addresses = {
	# #	'int': b'XXX',
	# }

	# pixel_pin = board.D6
	# nr_pixels = 4

	display_time = 3
	cycle_time = 300

	# Create screen connection
	oled = SSD1306_I2C(128, 64, I2C(SCL, SDA), addr=0x3d, reset=DigitalInOut(D5))

	# Showing some feedback
	sleep(0.5)
	oled.fill(0)
	oled.text('Starting...', 0, 0, 1, size=2)
	oled.show()

	# Create pm25 connections
	pm25_int = PM25_UART(UART(TX, RX, baudrate=9600), None)
	pm25_ext = PM25_UART(UART(A1, A2, baudrate=9600), None)

	# # Create radio connection
	# radio_cs = DigitalInOut(radio_cs_pin)
	# radio_reset = DigitalInOut(radio_reset_pin)
	# spi = SPI(radio_clock_pin, MOSI=radio_mosi_pin, MISO=radio_miso_pin)
	# rfm69 = RFM69(spi, radio_cs, radio_reset, radio_freq)

	# Create temperature connection
	# ow_bus = OneWireBus(temp_data_pin)
	# temp_devices = {}
	# for name, address in temp_addresses.items():
	# 	temp_devices[name] = DS18X20(ow_bus, address)
	#
	# Create neopixels
	# pixels = NeoPixel(pixel_pin, nr_pixels, brightness=0.3, auto_write=False)
	#
	# def wheel(pos):
	# 	# Input a value 0 to 255 to get a color value.
	# 	# The colours are a transition r - g - b - back to r.
	# 	if pos < 0 or pos > 255:
	# 		return (0, 0, 0)
	# 	if pos < 85:
	# 		return (255 - pos * 3, pos * 3, 0)
	# 	if pos < 170:
	# 		pos -= 85
	# 		return (0, 255 - pos * 3, pos * 3)
	# 	pos -= 170
	# 	return (pos * 3, 0, 255 - pos * 3)
	#
	# for j in range(255):
	# 	for i in range(nr_pixels):
	# 		rc_index = (i * 256 // nr_pixels) + j
	#
	# 		pixels[i] = wheel(rc_index & 255)
	# 	pixels.show()
	# 	# sleep(0)
	# pixels.fill(0, 0, 0, 255)
	# pixels.show
	# sleep(0.5)
	# pixels.fill((0, 0, 0, 0))
	# pixels.show()

	# Create button
	button = DigitalInOut(A0)
	button.direction = Direction.INPUT
	button.pull = Pull.UP

	oled.text('...done', 10, 32, 1, size=2)
	oled.show()
	sleep(display_time)
	oled.fill(0)
	oled.show()
	status_led.value = False
	# oled.poweroff()

except Exception as e:
	print(e)
	try:
		oled.text('...failed!', 8, 32, 1, size=2)
		oled.show()
	except:
		pass
	while True:
		sleep(0.2)
		status_led.value = False
		sleep(0.2)
		status_led.value = True


def print_data():
	# oled.poweron()
	# sleep(1)
	oled.fill(0)
	oled.text('INT. parts um/0.1L:', 5, 0, 1)
	oled.text('0.3u:', 5, 16, 1)
	oled.text(str(pm25_int_data["particles 03um"]), 39, 16, 1)
	oled.text('0.5u:', 5, 28, 1)
	oled.text(str(pm25_int_data["particles 05um"]), 39, 28, 1)
	oled.text('1.0u:', 5, 40, 1)
	oled.text(str(pm25_int_data["particles 10um"]), 39, 40, 1)
	oled.text('2.5u:', 66, 16, 1)
	oled.text(str(pm25_int_data["particles 25um"]), 100, 16, 1)
	oled.text('5.0u:', 66, 28, 1)
	oled.text(str(pm25_int_data["particles 50um"]), 100, 28, 1)
	oled.text('10u:', 66, 40, 1)
	oled.text(str(pm25_int_data["particles 100um"]), 100, 40, 1)
	oled.show()
	sleep(display_time)

	oled.fill(0)
	oled.text('EXT. parts um/0.1L:', 5, 0, 1)
	oled.text('0.3u:', 5, 16, 1)
	oled.text(str(pm25_ext_data["particles 03um"]), 39, 16, 1)
	oled.text('0.5u:', 5, 28, 1)
	oled.text(str(pm25_ext_data["particles 05um"]), 39, 28, 1)
	oled.text('1.0u:', 5, 40, 1)
	oled.text(str(pm25_ext_data["particles 10um"]), 39	, 40, 1)
	oled.text('2.5u:', 66, 16, 1)
	oled.text(str(pm25_ext_data["particles 25um"]), 100, 16, 1)
	oled.text('5.0u:', 66, 28, 1)
	oled.text(str(pm25_ext_data["particles 50um"]), 100, 28, 1)
	oled.text('10u:', 66, 40, 1)
	oled.text(str(pm25_ext_data["particles 100um"]), 100, 40, 1)
	oled.show()
	sleep(display_time)

	oled.fill(0)
	oled.show()

	# oled.poweroff()


while True:
	print('entering loop')
	pm25_int_data = pm25_int.read()
	pm25_ext_data = pm25_ext.read()
	print(pm25_int_data)
	print(pm25_ext_data)

	# read temps

	end_time = monotonic() + cycle_time

	while end_time > monotonic():
		if button.value:
			print('button pressed')
			try:
				print_data()
			except Exception as e:
				print(e)
		sleep(0.1)









