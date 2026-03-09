import time
from IMU import *
from I2CScan import *
from Vehicle import Vehicle

scan_i2c_bus()
run_imu()

this_vehicle = Vehicle()


this_vehicle.start_imu_process()
this_vehicle.start_communication_module()
this_vehicle.start_device_discovery()

# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# Start the communication module
# Start the device discovery process