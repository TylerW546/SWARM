import time
from IMU import *
from I2CScan import *
from Vehicle import Vehicle
import serial
from SerialInterface import SerialInterface
from UWBInterface import *

ser = SerialInterface()

send_uwb_message(ser, "Hello, UWB!")
send_uwb_message(ser, "Hello, UWB! 2")

print(ser.to_send_queue)


while True:
    ser.loop()

    
this_vehicle = Vehicle()
this_vehicle.start_imu_process()
this_vehicle.start_communication_module()
this_vehicle.start_device_discovery()

# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# Start the communication module
# Start the device discovery process