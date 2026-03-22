import time
from IMU import *
from I2CScan import *
from Vehicle import Vehicle
import serial
from SerialInterface import SerialInterface

ser = SerialInterface()
i = 0
while True:
    ser.loop()

    if i % 10 == 0:
        print("Performing periodic tasks...")
        ser.add_to_send_queue(f"*Periodic message {i//10}~")

    i += 1

    
this_vehicle = Vehicle()
this_vehicle.start_imu_process()
this_vehicle.start_communication_module()
this_vehicle.start_device_discovery()

# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# Start the communication module
# Start the device discovery process