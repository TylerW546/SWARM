import time
from IMU import *
from I2CScan import *
from Vehicle import Vehicle
import serial

# Replace with your serial port
PORT = '/dev/ttyACM0'  # or 'COM3' on Windows
BAUDRATE = 115200

ser = serial.Serial(PORT, BAUDRATE, timeout=1)

# Try reading initial data
line = ser.readline().decode('utf-8', errors='ignore').strip()
if line:
    print("Firmware responded:", line)
else:
    print("No response — firmware may not be installed")
this_vehicle = Vehicle()


this_vehicle.start_imu_process()
this_vehicle.start_communication_module()
this_vehicle.start_device_discovery()

# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# Start the communication module
# Start the device discovery process