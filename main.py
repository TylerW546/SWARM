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
CTRL_REG4 = 0x23  # Example: full scale ±2g, high-resolution mode
OUT_X_L = 0x28    # Base register for accelerometer X-axis LSB
OUT_Y_L = 0x2A    # Base register for Y-axis LSB
OUT_Z_L = 0x2C    # Base register for Z-axis LSB

# -------------------------------
# Initialize bus
# -------------------------------
bus = smbus.SMBus(BUS_NUMBER)

WHO_AM_I = 0x0F
device_id = bus.read_byte_data(DEVICE_ADDRESS, WHO_AM_I)
print(f"LIS2DE12 WHO_AM_I: {device_id:#04x}")

bus.write_byte_data(DEVICE_ADDRESS, CTRL_REG1, 0x57)  # 0b01010111

# CTRL_REG4 (0x23): Full scale ±2g, high-resolution mode
bus.write_byte_data(DEVICE_ADDRESS, CTRL_REG4, 0x08)  # 0b00001000

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

def read_accel():
    # LIS2DE12 outputs LSB first (little-endian)
    x = read_word(OUT_X_L)
    y = read_word(OUT_Y_L)
    z = read_word(OUT_Z_L)
    return x * 0.001, y * 0.001, z * 0.001


from collections import deque

SMOOTHING_WINDOW = 5  # Number of samples to average

# Deques to store last N readings for smoothing
x_window = deque(maxlen=SMOOTHING_WINDOW)
y_window = deque(maxlen=SMOOTHING_WINDOW)
z_window = deque(maxlen=SMOOTHING_WINDOW)

def smooth_accel(x, y, z):
    """Add the latest reading and compute the moving average"""
    x_window.append(x)
    y_window.append(y)
    z_window.append(z)
    
    x_avg = sum(x_window) / len(x_window)
    y_avg = sum(y_window) / len(y_window)
    z_avg = sum(z_window) / len(z_window)
    
    return x_avg, y_avg, z_avg

ALPHA = 0.2  # smaller = smoother, larger = more responsive

# Initialize smoothed values
x_smooth = y_smooth = z_smooth = 0.0
first_reading = True

def smooth_accel_ema(x, y, z):
    global x_smooth, y_smooth, z_smooth, first_reading
    if first_reading:
        x_smooth, y_smooth, z_smooth = x, y, z
        first_reading = False
    else:
        x_smooth = ALPHA * x + (1 - ALPHA) * x_smooth
        y_smooth = ALPHA * y + (1 - ALPHA) * y_smooth
        z_smooth = ALPHA * z + (1 - ALPHA) * z_smooth
    return x_smooth, y_smooth, z_smooth

try:
    i = 0
    while True:
        i += 1
        x, y, z = read_accel()
        x_ema, y_ema, z_ema = smooth_accel_ema(x, y, z)
        x_f, y_f, z_f = smooth_accel(x_ema, y_ema, z_ema)
        if i % 10 == 0:  # Print every 10 samples
            print(f"Sample {i} - X: {x_f:.3f}, Y: {y_f:.3f}, Z: {z_f:.3f}")
        time.sleep(0.05)
except Exception as e:
    print("[Test 4] I2C error during continuous read:", e)

# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# Start the communication module
# Start the device discovery process