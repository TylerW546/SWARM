import time
from IMU import *
from I2CScan import *
from Vehicle import Vehicle
import serial

# Replace with your serial port
PORT = '/dev/ttyAMA0'  # or 'COM3' on Windows
BAUDRATE = 115200

ser = serial.Serial(PORT, BAUDRATE, timeout=1)
# Try reading initial data in a loop to check if firmware is responding
print("Checking for firmware response...")
while True:
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"Received: {line}")
            if "Firmware Version" in line:
                print("Firmware is responding!")
                break   
        else:
            print("No response yet, retrying...")
    except OSError as e:
        print(f"Serial I/O error: {e}")
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        

    time.sleep(1)

this_vehicle = Vehicle()
this_vehicle.start_imu_process()
this_vehicle.start_communication_module()
this_vehicle.start_device_discovery()

# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# Start the communication module
# Start the device discovery process