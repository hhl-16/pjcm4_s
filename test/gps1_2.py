import serial
import time
import re
import socket


# Serial port configuration
SERIAL_PORT = "/dev/ttyUSB2"
BAUD_RATE = 115200

def send_data_to_b(data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(str(data).encode(), ('127.0.0.1', 65432))  
        print(f"{data}")

def send_at_command(ser, command):
    """Send an AT command"""
    ser.write((command + "\r\n").encode())
    time.sleep(1)

def parse_gps_info(response):
    """
    Parse GPS data from +CGPSINFO response.
    Example: +CGPSINFO: 1046.197624,N,10646.112661,E,240225,094721.0,23.7,0.0
    """
    match = re.search(r'\+CGPSINFO:\s([\d.]+),([NS]),([\d.]+),([EW]),\d+,\d+\.\d+,([\d.]+),([\d.]+)', response)
    if match:
        raw_lat = match.group(1)
        raw_lon = match.group(3)
        lat = convert_to_decimal(raw_lat, match.group(2))
        lon = convert_to_decimal(raw_lon, match.group(4))
        altitude = round(float(match.group(5)), 2)  # Round altitude to 2 decimal places
        speed = round(float(match.group(6)), 2)  # Round speed to 2 decimal places
        return lat, lon, altitude, speed
    return None, None, None, None
def convert_to_decimal(degrees_minutes, direction):
    """
    Convert GPS coordinates from DMM (degrees and decimal minutes) to DD (decimal degrees).
    
    Example:
    - Input: "1046.197624", "N"
    - Output: 10.7699604
    """
    degrees = int(float(degrees_minutes) / 100)  # Extract degrees
    minutes = float(degrees_minutes) % 100       # Extract minutes
    decimal_degrees = degrees + (minutes / 60)   # Convert to decimal degrees
    
    if direction in ['S', 'W']:  # South and West are negative
        decimal_degrees *= -1

    return round(decimal_degrees,6)
def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        
        # Enable GPS
        print("Enabling GPS...")
        send_at_command(ser, "AT+CGPS=1")

        # Send AT+CGPSINFO=10 ONCE
        print("Requesting GPS data...")
        send_at_command(ser, "AT+CGPSINFO=10")

        print("Listening for GPS data...\n")
        
        while True:
            if ser.in_waiting:
                response = ser.read(ser.in_waiting).decode(errors='ignore')

                if "+CGPSINFO:" in response:
                    lat, lon, altitude, speed = parse_gps_info(response)
                    if lat is not None:
                        print(f"Coordinates: {lat}, {lon} | Altitude: {altitude}m | Speed: {speed} km/h")
                        data = {
                            "lat": lat,
                            "lon": lon,
                            "altitude": altitude,
                            "speed": speed
                        }
                        send_data_to_b(data)
                    else:
                        print("Invalid GPS data.")
                        data = {
                            "lat": 0.0,
                            "lon": 0.0,
                            "altitude": 0.0,
                            "speed": 0.0
                        }
                        send_data_to_b(data)

            time.sleep(0.1)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
