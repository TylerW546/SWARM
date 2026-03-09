import time
from Vehicle import Vehicle

this_vehicle = Vehicle()


this_vehicle.start_imu_process()
this_vehicle.start_communication_module()
this_vehicle.start_device_discovery()

while True:
    time.sleep(1)
    print("Hello")

# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# Start the communication module
# Start the device discovery process