# Import generic tools
import board
import busio
from digitalio import DigitalInOut
from time import sleep

# Import PM libs
from adafruit_pm25.uart import PM25_UART

# Import screen libs
from adafruit_ssd1306 import SSD1306_I2C

# Import radio libs
from adafruit_rfm69 import RFM69

# Import temperature libs
from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20

# Import neopixels libs
from neopixel import Neopixel

# Define pins and config
pm25_reset_pin = None
pm25_int_tx_pin = board.TX
pm25_int_rx_pin = board.RX
pm25_ext_tx_pin = board.A1  # https://learn.adafruit.com/circuitpython-essentials/circuitpython-uart-serial
pm25_ext_rx_pin = board.A2

screen_reset_pin = board.D5
screen_clock_pin = board.SCL
screen_data_pin = board.SDA
screen_width = 128
screen_height = 64

radio_clock_pin = board.SCK
radio_mosi_pin = board.MOSI
radio_miso_pin = board.MISO
radio_cs_pin = board.RFM69_CS
radio_freq = 868.0

temp_data_pin = board.D9
temp_addresses = {'int': b'XXX',}

neopixel_pin = board.D6

button_pin = board.D14

# Create pm25 connections
uart_int = busio.UART(pm25_int_tx_pin, pm25_int_rx_pin, baudrate=9600)
uart_ext = busio.UART(pm25_ext_tx_pin, pm25_ext_rx_pin, baudrate=9600)
pm25_int = PM25_UART(uart_int, pm25_reset_pin)
pm25_ext = PM25_UART(uart_ext, pm25_reset_pin)

# Create screen connection
screen_reset_io = DigitalInOut(screen_reset_pin)
i2c = busio.I2C(screen_clock_pin, screen_data_pin)
oled = SSD1306_I2C(screen_width, screen_height, i2c, addr=0x3d, reset=screen_reset_io)

# Create radio connection
radio_cs = DigitalInOut(radio_cs_pin)
radio_reset_io = DigitalInOut(radio_cs_pin)
spi = busio.SPI(radio_clock_pin, MOSI=radio_mosi_pin, MISO=radio_miso_pin)
rfm69 = RFM69(spi, radio_cs, radio_reset_io, radio_freq)

# Create temperature connection
ow_bus = OneWireBus(temp_data_pin)
temp_devices = {}
for name, address in temp_addresses.items():
	temp_devices[name] = DS18X20(ow_bus, address)


