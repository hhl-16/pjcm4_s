import serial
import time

UART_PORT = "/dev/ttyS0"  
BAUD_RATE = 115200 

ser = serial.Serial(UART_PORT, BAUD_RATE, timeout=1)

def send_at_command(command, delay=1):
    ser.write((command + "\r\n").encode())  
    time.sleep(delay)
    response = ser.read_all().decode(errors='ignore')  
    return response.strip()

try:
    print("-------..")
    response = send_at_command("AT")
    if "OK" in response:
        print("T---------- OK!")
    else:
        print("K------------ART.")

    print("K--------tra SIM...")
    response = send_at_command("AT+CPIN?")
    print("P-----------i:", response)

except KeyboardInterrupt:
    print("---------- chuong.")
finally:
    ser.close()
