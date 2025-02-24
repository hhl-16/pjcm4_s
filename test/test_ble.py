#CODE BLUETOOTH RECEIVER DATA
#VERSION 1.1
import socket
import time
import os

os.environ['BLUETOOTH_HCI'] = '1'

raw_var = []  # Global variable to store processed data

# read MAC address from file
def read_from_file(filename):
    with open(filename, 'r') as file:
        mac_address = file.readline().strip()
    return mac_address


# Reconnect to Bluetooth
def connect_bluetooth(mac_address):
    connected = False
    s = None    
    while not connected:
        try:
            s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            print(f"BLEconnecting {mac_address}...")
            s.connect((mac_address, 1))
            print("BLEconnect success.")
            connected = True  

        except Exception as e:
            print(f"Error connecting: {e}. Retrying in 5 seconds...")
            time.sleep(5)  
        
    return s  

# Format received data
def process_data(data):
    data_str = data.decode('utf-8').strip()  # Giải mã dữ liệu

    print(f"Received raw data: {data_str}")  # In ra dữ liệu thô để kiểm tra

    if data_str.startswith("ID,") and data_str.endswith("|"):
        data_str = data_str[3:-1]  # Loại bỏ "ID," và "|"
        values = data_str.split(',')
        
        try:
            var1 = values[0]  # '0000' hoặc tương tự
            var2 = float(values[1])  # Giá trị float đầu tiên
            var3 = float(values[2])  # Giá trị float thứ hai
            
            return var1, var2, var3
        except (IndexError, ValueError):
            # print("Error processing data: incorrect format or conversion.")
            return None, None, None
    else:
        # print("Error: Data format invalid.")  # Thông báo lỗi nếu định dạng không hợp lệ
        return None, None, None


# Receive and process data from Bluetooth
def receive_data(s, mac_address):
    global raw_var  # Declare as global to modify it
    while True:
        try:
            data = s.recv(1024)  # Receive data (1024 bytes)
            if not data:
                print("BLEConnection disconnected.")
                raise ConnectionError("BLEConnection disconnected")
            
            print(f"BLEdata: {data.decode('utf-8')}")
            
            # Process the received data
            raw_var = process_data(data)
            if raw_var[0] is not None:
                print(f"var1: {raw_var[0]}")
                print(f"var2: {raw_var[1]}")
                print(f"var3: {raw_var[2]}")

        except Exception as e:
            print(f"BLE error: {e}. Attempting to reconnect...")
            s.close()  # Close the current socket
            s = connect_bluetooth(mac_address)  # Reconnect to Bluetooth


if __name__ == "__main__":
    # Read the MAC address from the file
    #mac_address = read_from_file('/home/hkn/pj_cm4/device_info/mac_ble.txt')
    mac_address = '08:A6:F7:1D:A0:1A'

    
    # Connect to the Bluetooth device
    s = connect_bluetooth(mac_address)
    
    # Start receiving data
    receive_data(s, mac_address)
