import time
from IMU import *
from I2CScan import *
from Vehicle import Vehicle
import serial
from SerialInterface import SerialInterface
from UWBInterface import *
from enum import Enum 
from test import *

import uuid

ser = SerialInterface()
uwb = UWBInterface(ser)

uwb.assign_id(str(uuid.getnode()))

class State(Enum):
    INIT_DEVICE_DISCOVERY = 1
    INIT_PARENTING = 2
    INIT_CHILD = 3
    WANDER = 4

state = State.INIT_DEVICE_DISCOVERY


# Device discovery parameters:

while True:
    if state == State.INIT_DEVICE_DISCOVERY:
        if not uwb.is_discovering and not uwb.finished_discovery:
            uwb.send_uwb_message("RESETTING")
            uwb.enter_discovery_mode()

        if uwb.finished_discovery:
            #uwb.enter_listen_mode()
            run_test()
            if uwb.is_leader:
                state = State.INIT_PARENTING
            else:
                state = State.INIT_CHILD
                
        time.sleep(0.2)
    
        

    if uwb.uwb_messages_recieved:
        print("Received UWB messages:")
        for msg in uwb.uwb_messages_recieved:
            print(msg)
            if msg == "RESETTING":
                print("Other just reset, starting...")
        uwb.uwb_messages_recieved = []
    # elif state == State.INIT_PARENTING:
    #     print("I am the leader")

    #     ## MOVE TO POSITION 1:
    #         ## FOR CHILD, SEND RANGE INFO

    #     ## POSITIONS 2-3:

    #     ## CHILDREN WILL MOVE

    #     ## POSITIONS 4-6:
    #         ## SEND RANGE INFO

    #     # TELL CHILDREN THEIR CONSTELLATION POSITIONS

    #     # SEND MORE COMMANDS

    #     # BREAK, WANDER

    #     state = State.WANDER
    # elif state == State.INIT_CHILD:
    #     print("I am a child")

    #     ## WAIT FOR RANGE INFO 1

    #     ## WAIT FOR RANGE INFO 2

    #     ## WAIT FOR RANGE INFO 3

    #     ## TRIANGULATE

    #     ## MOVE

    #     ## REPEAT ONCE

    #     ## WAIT FOR LEADER TO ASSIGN POSITION, MOVE TO THAT POSITION

    #     ## FOLLOW LEADER COMMANDS

    #     ## IF LEADER SAYS TO WANDER, ENTER WANDER MODE:
    #     state = State.WANDER

    
    #     # Say "HI, im 0 with hash #, next available index is 1"
    #     # Listen for responses for a certain amount of time
    #         # ACK the first response
    #     # If no one responds, exponential back off and listen
    #         # If someone says HI, send an acceptance message.
    #             # Hi #, i'll be #, and heres a random hash to confirm: X
    #         # wait for them to ack your acceptance message with hash.
    #             # If acked, become child.
    #             # If not acked, back off and listen again.
            
    
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