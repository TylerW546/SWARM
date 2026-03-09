import time
from IMU import *
from I2CScan import *
from Vehicle import Vehicle
import serial

# Replace with your serial port
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

time.sleep(2)  # Wait for module to initialize

# Send a command (depends on firmware)
ser.write(b'info\r\n')

# Read response
while True:
    line = ser.readline().decode('utf-8').strip()
    if line:
        print(line)

this_vehicle = Vehicle()


this_vehicle.start_imu_process()
this_vehicle.start_communication_module()
this_vehicle.start_device_discovery()

# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# Start the communication module
# Start the device discovery process