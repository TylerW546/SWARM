import time
from IMU import *
from Vehicle import *
from test import *
from picamera2 import Picamera2
import cv2
import numpy as np

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()
time.sleep(1)

def camera_process():
    frame = picam2.capture_array()

    # Convert to HSV
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # For tracking something bright orange
    lower = np.array([104, 150, 150])
    upper = np.array([120, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)

    h, w, _ = frame.shape
    pixel_count = cv2.countNonZero(mask)
    print("Pixel count:", pixel_count)

    # Find centroid
    cx, cy = None, None
    moments = cv2.moments(mask)
    if moments["m00"] > 0:
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        print("Found at:", cx, cy)

    return cx, cy, pixel_count

    #     # draw for debugging
    #     cv2.circle(frame, center=(cx, cy), radius=100, color=(255, 0, 0), thickness=2)

    # cv2.imshow("frame", frame)
    # cv2.imshow("mask", mask)



    



# Device discovery parameters:
v = Vehicle()

last_frame_time = time.time()

while True:
    frame_start = time.time()
    # print("Frame time: ", frame_start - last_frame_time)
    last_frame_time = frame_start
    
    if v.state == State.INIT_DEVICE_DISCOVERY:
        if not v.uwb.is_discovering and not v.uwb.finished_discovery:
            v.uwb.send_uwb_message("RESETTING")
            v.uwb.enter_discovery_mode()

        if v.uwb.finished_discovery:
            v.uwb.enter_listen_mode()
            if v.uwb.is_leader:
                v.state = State.INIT_PARENTING
            else:
                v.state = State.INIT_CHILD
                
        time.sleep(0.2)

    if v.state == State.INIT_PARENTING:
        print("I am leader")
        v.start_test()
        # uwb.enter_ranging_mode()
        time.sleep(1)
        v.state = State.WANDER
        
    if v.state == State.INIT_CHILD:
        time.sleep(1)
        

    if v.uwb.uwb_messages_recieved:
        print("Received UWB messages:")
        for msg in v.uwb.uwb_messages_recieved:
            print(msg)
            if msg == "RESETTING":
                print("Other just reset, starting...")
        v.uwb.uwb_messages_recieved = []
    # elif v.state == State.INIT_PARENTING:
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

    #     v.state = State.WANDER
    # elif v.state == State.INIT_CHILD:
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

    cx, cy, pixel_count = camera_process()
    if pixel_count > PIXEL_COUNT_THRESHOLD: 
        print(f"Object detected at ({cx}, {cy}) with pixel count {pixel_count}")

    v.update()

    while time.time() - frame_start < 0.05:
        pass

this_vehicle = Vehicle()
this_vehicle.start_imu_process()
this_vehicle.start_communication_module()
this_vehicle.start_device_discovery()


# Initialization:
# Create a vehicle object

# Start the IMU process to continually track
# Start the communication module
# Start the device discovery process