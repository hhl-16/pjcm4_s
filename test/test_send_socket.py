import socket
import time

def send_data_to_b(data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(str(data).encode(), ('127.0.0.1', 65432))  
        print(f"{data}")
if __name__ == "__main__":
    try:
        while True:
            data = {
                "lat": 10.123456,
                "lon": 106.654321,
                "altitude": 26.2,
                "speed": 5.5
            }
            send_data_to_b(data)
            time.sleep(2)
    except KeyboardInterrupt:
        print(".")