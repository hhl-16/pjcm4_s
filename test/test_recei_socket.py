import socket
import ast

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('127.0.0.1', 65432))
        print("Chờ nhận dữ liệu từ a.py...")
        while True:
            data, addr = s.recvfrom(1024)
            data_dict = ast.literal_eval(data.decode())
            print(f"Nhận dữ liệu từ {addr}: {data_dict}")

if __name__ == "__main__":
    start_server()