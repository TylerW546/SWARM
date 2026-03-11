import time
from IMU import *
from I2CScan import *
from Vehicle import Vehicle
import serial

# Replace with your serial port
SERIAL_PORT = '/dev/ttyAMA0'
BAUDRATE = 115200

def open_serial():
    while True:
        try:
            ser = serial.Serial(
                SERIAL_PORT,
                BAUDRATE,
                timeout=1,        # 1 second timeout
                write_timeout=1
            )
            print(f"Serial port {SERIAL_PORT} opened.")
            return ser
        except Exception as e:
            print(f"Failed to open serial port: {e}")
            time.sleep(2)

ser = open_serial()

while True:
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode(errors="ignore").strip()
            print(f"Received: {line}")
        else:
            print("No response yet, retrying...")
            time.sleep(0.2)
    except OSError as e:
        print(f"Serial I/O error: {e}")
        try:
            ser.close()
        except:
            pass
        time.sleep(1)
        ser = open_serial()

this_vehicle = Vehicle()
this_vehicle.start_imu_process()
this_vehicle.start_communication_module()
this_vehicle.start_device_discovery()

# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# Start the communication module
# Start the device discovery process