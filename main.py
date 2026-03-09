import time
import smbus

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
OUT_Z_L = 0x2C    # Base register for Z-axis LSB

# -------------------------------
# Initialize bus
# -------------------------------
bus = smbus.SMBus(BUS_NUMBER)

# -------------------------------
# Helper functions
# -------------------------------
def read_word(register_l):
    """Read 16-bit signed value from two registers (little endian)"""
    lsb = bus.read_byte_data(DEVICE_ADDRESS, register_l)
    msb = bus.read_byte_data(DEVICE_ADDRESS, register_l + 1)
    value = (msb << 8) | lsb
    if value >= 32768:
        value -= 65536
    return value

# -------------------------------
# Test 1: WHO_AM_I
# -------------------------------
try:
    whoami = bus.read_byte_data(DEVICE_ADDRESS, WHO_AM_I)
    print(f"[Test 1] WHO_AM_I: 0x{whoami:X}")
except Exception as e:
    print("[Test 1] I2C error:", e)

# -------------------------------
# Test 2: Basic initialization
# -------------------------------
try:
    bus.write_byte_data(DEVICE_ADDRESS, CTRL_REG1, 0x57)
    time.sleep(0.1)
    print("[Test 2] Device initialized (CTRL_REG1 set)")
except Exception as e:
    print("[Test 2] I2C error during initialization:", e)

# -------------------------------
# Test 3: Read accelerometer once
# -------------------------------
try:
    x = read_word(OUT_X_L)
    y = read_word(OUT_Y_L)
    z = read_word(OUT_Z_L)
    print(f"[Test 3] Accel raw readings - X: {x}, Y: {y}, Z: {z}")
except Exception as e:
    print("[Test 3] I2C error during accelerometer read:", e)

# -------------------------------
# Test 4: Continuous accelerometer read
# -------------------------------
print("[Test 4] Continuous accelerometer read (5 samples):")
try:
    for i in range(5):
        x = read_word(OUT_X_L)
        y = read_word(OUT_Y_L)
        z = read_word(OUT_Z_L)
        print(f"Sample {i+1} - X: {x}, Y: {y}, Z: {z}")
        time.sleep(0.5)
except Exception as e:
    print("[Test 4] I2C error during continuous read:", e)
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