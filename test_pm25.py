import board
import busio
from adafruit_pm25.uart import PM25_UART
uart = busio.UART(board.TX, board.RX, baudrate=9600)
reset_pin = None
pm25 = PM25_UART(uart, reset_pin)
aqdata = pm25.read()
print(aqdata)
