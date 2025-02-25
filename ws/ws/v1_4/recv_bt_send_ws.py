'''
VERSION 1.4
RECEIVE DATA BLUETOOTH  <---- ESP32 SENSOR
DATA -> CALCULATOR 
SEND WEBSOCKET SERVER
CODE MAIN

FORMAT SERVER
{"name":"ABC","gps":{"lat":"0.000000","lng":"0.000000","speed":"0.00"},"sensor":{"fuel":"0.00","weight":"1128.21"}}

'''
import asyncio
import websockets
import socket
import time
import serial
import os
import sysv_ipc
import ast


FILE_URI_PATH = "/home/hkn/pjcm4/device_info/url_ws.txt" # url websocket
FILE_BLE_ADDRESS_PATH = "/home/hkn/pjcm4/device_info/mac_ble.txt" #address bluetooth
FILE_CONFIG_PATH = "/home/hkn/pjcm4/device_info/id_device.txt" # max infor sensor
FILE_ID_DEVICE = "/home/hkn/pjcm4/device_info/config.txt" #id device
pipe_path = "/home/hkn/pjcm4/device_info/pipe_sensor"

sendInterval = int(2) # delay between each send
raw_var = [] # raw data bluetooth
volume_s = 0
weight_s = 0
flow_s = 0
lat = 0.0
lng = 0.0
speed = 0.0



#time.sleep(310)
async def start_udp_server():
    global lat,lng,speed
    loop = asyncio.get_running_loop()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('127.0.0.1', 65432))
        print("Chờ nhận dữ liệu từ a.py...")
        while True:
            data, addr = await loop.run_in_executor(None, s.recvfrom, 1024)
            data_dict = ast.literal_eval(data.decode())
            print(f"Nhận dữ liệu từ {addr}: {data_dict}")
            lat = float(data_dict.get("lat", 0.0))
            lng = float(data_dict.get("lon", 0.0))
            speed = float(data_dict.get("speed", 0.0))



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
            print(f"BLE Error connecting: {e}. Retrying in 5 seconds...")
            s.close()
            time.sleep(5)  
        
    return s  

# Format received data
def process_data_ble(data):
    data_str = data.decode('utf-8').strip() 
    print(f"BLE Received raw data: {data_str}")  
    if data_str.startswith("ID,") and data_str.endswith("|"):
        data_str = data_str[3:-1]
        values = data_str.split(',')        
        try:
            var1 = values[0]
            var2 = float(values[1])
            var3 = float(values[2])         
            return var1, var2, var3
        except (IndexError, ValueError):
            return None, None, None
    else:
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
            raw_var = process_data_ble(data)
            if raw_var[0] is not None:
                cal_data_ble(raw_var[0],raw_var[1],raw_var[2])
                print("BLE format:" + str(raw_var[0]) +"," +  str(raw_var[1]) + "," + str(raw_var[2]))

        except Exception as e:
            print(f"BLE error: {e}. Attempting to reconnect...")
            s.close()  # Close the current socket
            s = connect_bluetooth(mac_address)  # Reconnect to Bluetooth

def cal_data_ble(volume,weight,flow):
    global volume_s,weight_s,flow_s
    try:
      num_float = float(volume)
    except ValueError:
      num_float = 0.0
    if(num_float != 0):
      volume_s = ((num_float *0.1) * 645) / 670
      volume_s = round(volume_s, 2)
    #volume_s = volume
    
    weight_s = weight
    flow_s = flow




# return data from read file txt
def read_from_file(filename):
    with open(filename, 'r') as file:
        data = file.readline().strip()
    return data

'''
read txt in device_info
'''
def read_file_init():
    global url,address_ble,id,mac_config
    print("-------READ FILE---------")
    url = read_from_file(FILE_URI_PATH)
    time.sleep(0.1)
    address_ble = read_from_file(FILE_BLE_ADDRESS_PATH)
    time.sleep(0.1)
    id = read_from_file(FILE_CONFIG_PATH)
    time.sleep(0.1)
    mac_config = read_from_file(FILE_ID_DEVICE)
    time.sleep(0.1)
def print_file():
    print(url.encode('utf-8'))
    print(address_ble.encode('utf-8'))
    print(id.encode('utf-8'))
    print(mac_config.encode('utf-8'))

read_file_init()
print_file()

 


#receive config from server websocket
async def receive_ws(websocket):
    while True:
        try:
            response = await websocket.recv()
            print(f"WS Received: {response}")
        except websockets.ConnectionClosed:
            print("Connection closed")
            break


# create format data json
def create_datajson_string(header,param1,param2, param3):
    if(header == "sensor"):
        return f'"{header}":{{"fuel":"{param1}","weight":"{param2}","flow":"{param3}"}}'
    elif(header == "gps"):
        return f'"{header}":{{"lat":"{param1}","lng":"{param2}","speed":"{param3}"}}'
    else:
        return None


# creare format data server
def create_data_server():
    gps_string = create_datajson_string("gps", lat, lng, speed)
    sensor_string = create_datajson_string("sensor", volume_s, weight_s, flow_s)
    if gps_string and sensor_string:  
        json_string = f'{{"name":"{id}",{gps_string},{sensor_string}}}'
    elif gps_string:  
        json_string = f'{{"name":"{id}",{gps_string}}}'
    elif sensor_string:  
        json_string = f'{{"name":"{id}",{sensor_string}}}'
    else:  
        json_string = f'{{"name":"{id}"}}'
    print(json_string)
    return json_string



        
async def communicate_with_server_ws():  
    global url
    while True:
        try:
            async with websockets.connect(url) as websocket:
                #receive_task = asyncio.create_task(receive_ws(websocket))
                print("WS Connected to server")
                while True:
                    await websocket.send(create_data_server())
                    print("WS Sent")
                    await asyncio.sleep(sendInterval)              
        except Exception as e:
            print(f"Error connecting to server: {e}")
        await asyncio.sleep(5)

async def main():
    s = connect_bluetooth(address_ble)
    bluetooth_task = asyncio.to_thread(receive_data, s, address_ble)
    websocket_task = asyncio.create_task(communicate_with_server_ws())
    udp_server_task = asyncio.create_task(start_udp_server())
    await asyncio.gather(bluetooth_task, websocket_task,udp_server_task)
if __name__ == "__main__":
    asyncio.run(main())
