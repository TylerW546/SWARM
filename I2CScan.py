import smbus
import time

BUS_NUMBER = 2

def scan_i2c_bus():
    bus = smbus.SMBus(BUS_NUMBER)

    print("Scanning I2C bus for devices...")

    found_devices = []
    for addr in range(0x03, 0x78):
        try:
            bus.read_byte(addr)
            found_devices.append(addr)
        except:
            pass

    if found_devices:
        print("Found I2C devices at addresses:", [hex(a) for a in found_devices])
    else:
        print("No I2C devices found on bus", BUS_NUMBER)

    # -------------------------------
    # Attempt to read WHO_AM_I from common addresses
    # -------------------------------
    candidate_addresses = found_devices
    WHO_AM_I = 0x0F

    for addr in candidate_addresses:
        try:
            device_id = bus.read_byte_data(addr, WHO_AM_I)
            print(f"Address {hex(addr)} WHO_AM_I = {hex(device_id)}")
        except Exception as e:
            print(f"Address {hex(addr)}: cannot read WHO_AM_I ({e})")

    print("\nOnce you find the address returning 0x33 (LIS2DE12),")
    print("update DEVICE_ADDRESS in your code and test reading accelerometer values.")