import time
import smbus
from mpu6050 import MPU6050

from Vehicle import Vehicle

this_vehicle = Vehicle()


this_vehicle.start_imu_process()
this_vehicle.start_communication_module()
this_vehicle.start_device_discovery()
BUS_NUMBER = 2
DEVICE_ADDRESS = 0x37
WHO_AM_I = 0x0F
CTRL_REG1 = 0x20  # Example: enable XYZ axes, 100Hz
OUT_X_L = 0x28    # Base register for accelerometer X-axis LSB
OUT_Y_L = 0x2A    # Base register for Y-axis LSB
OUT_Z_L = 0x2C    # Base re

i2c_bus = 2
device_address = 0x37
freq_divider = 0x04

# Make an MPU6050
mpu = MPU6050(i2c_bus, device_address, freq_divider)

# Initiate your DMP
mpu.dmp_initialize()
mpu.set_DMP_enabled(True)

packet_size = mpu.DMP_get_FIFO_packet_size()
FIFO_buffer = [0]*64

while True: # infinite loop
    if mpu.isreadyFIFO(packet_size): # Check if FIFO data are ready to use...
        
        FIFO_buffer = mpu.get_FIFO_bytes(packet_size) # get all the DMP data here
        
        q = mpu.DMP_get_quaternion_int16(FIFO_buffer)
        grav = mpu.DMP_get_gravity(q)
        roll_pitch_yaw = mpu.DMP_get_euler_roll_pitch_yaw(q)
        
        print('roll: ' + str(roll_pitch_yaw.x))
        print('pitch: ' + str(roll_pitch_yaw.y))
        print('yaw: ' + str(roll_pitch_yaw.z))
        print('\n')
        
# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# from mpu6050 import MPU6050

# i2c_bus = 1
# device_address = 0x29
# freq_divider = 0x04

# # Make an MPU6050
# mpu = MPU6050(i2c_bus, device_address, freq_divider)

# # Initiate your DMP
# mpu.dmp_initialize()
# mpu.set_DMP_enabled(True)

# packet_size = mpu.DMP_get_FIFO_packet_size()
# FIFO_buffer = [0]*64

# while True: # infinite loop
#     if mpu.isreadyFIFO(packet_size): # Check if FIFO data are ready to use...
        
#         FIFO_buffer = mpu.get_FIFO_bytes(packet_size) # get all the DMP data here
        
#         q = mpu.DMP_get_quaternion_int16(FIFO_buffer)
#         grav = mpu.DMP_get_gravity(q)
#         roll_pitch_yaw = mpu.DMP_get_euler_roll_pitch_yaw(q)
        
#         print('roll: ' + str(roll_pitch_yaw.x))
#         print('pitch: ' + str(roll_pitch_yaw.y))
#         print('yaw: ' + str(roll_pitch_yaw.z))
#         print('\n')
        
# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# Start the communication module
# Start the device discovery process