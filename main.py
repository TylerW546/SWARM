import time
from Vehicle import Vehicle

this_vehicle = Vehicle()


this_vehicle.start_imu_process()
this_vehicle.start_communication_module()
this_vehicle.start_device_discovery()
import smbus

# Initialize SMBus object for I2C bus 1
bus = smbus.SMBus(1)

# Define device address and register
DEVICE_ADDRESS = 0x18 # Replace with your device's address
REGISTER = 0x0F # Replace with your register address

# Write a byte to the device

# Read a byte from the device
data = bus.read_byte_data(DEVICE_ADDRESS, REGISTER)
print(f"Data read: {data}")
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