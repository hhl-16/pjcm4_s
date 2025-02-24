import subprocess
import serial
import time

SERIAL_PORT = '/dev/ttyUSB2'
BAUD_RATE = 115200
def get_signal_quality():
	try:
		ser = serial.Serial(SERIAL_PORT,BAUD_RATE,timeout=1)
		ser.write(b'AT+CSQ\r')
		time.sleep(0.5)
		response = ser.read(100)
		print(response)
		ser.close()
	except Exception as e:
		print(e)
print("abc")
get_signal_quality()

