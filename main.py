import time
from IMU import *
from I2CScan import *
from Vehicle import Vehicle
import serial
from SerialInterface import SerialInterface
from UWBInterface import *
from enum import Enum 

import uuid

ser = SerialInterface()
uwb = UWBInterface(ser)

uwb.assign_id(str(uuid.getnode()()))

class State(Enum):
    INIT_DEVICE_DISCOVERY = 1
    INIT_PARENTING = 2
    INIT_CHILD = 3

state = State.INIT_DEVICE_DISCOVERY


# Device discovery parameters:

uwb.enter_discovery_mode()
while True:
    if state == State.INIT_DEVICE_DISCOVERY:
        if not uwb.is_discovering:
            if uwb.is_leader:
                state = State.INIT_PARENTING
            else:
                state = State.INIT_CHILD
        time.sleep(0.2)

        # Say "HI, im 0 with hash #, next available index is 1"
        # Listen for responses for a certain amount of time
            # ACK the first response
        # If no one responds, exponential back off and listen
            # If someone says HI, send an acceptance message.
                 # Hi #, i'll be #, and heres a random hash to confirm: X
            # wait for them to ack your acceptance message with hash.
                # If acked, become child.
                # If not acked, back off and listen again.
            
    
    # run vehicle processes

    # run communication processes




    
    uwb.loop()

    
this_vehicle = Vehicle()
this_vehicle.start_imu_process()
this_vehicle.start_communication_module()
this_vehicle.start_device_discovery()

# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# Start the communication module
# Start the device discovery process