import uuid

from Motors import *
import UWBInterface
from SerialInterface import SerialInterface
from UWBInterface import *
from Util import *
from pidController import pidController
from Ultrasonic import *
import serial
import numpy as np

from picamera2 import Picamera2
import cv2

def camera_process(camera):
    if camera is None:
        return None, None, 0, 0

    frame = camera.capture_array()
    #downsample for faster processing
    frame = frame[::2, ::2]
    frame = cv2.flip(frame, -1)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    R = frame_rgb[:, :, 0]
    G = frame_rgb[:, :, 1]
    B = frame_rgb[:, :, 2]

    r = 1.1
    # Create mask: red dominant pixels
    red_mask = (((R.astype(float) / (G.astype(float) + 1)) > r) &
            (R.astype(float) / (B.astype(float) + 1) > r).astype(np.uint8) * 255)

    blue_mask = (((B.astype(float) / (G.astype(float) + 1)) > r) &
            (B.astype(float) / (R.astype(float) + 1) > r).astype(np.uint8) * 255)
    
    expanded_blue_mask = cv2.dilate(blue_mask, np.ones((7,7), np.uint8), iterations=1)
    expanded_blue_and_red_mask = cv2.bitwise_and(red_mask, red_mask, mask=expanded_blue_mask)
    
    frame = cv2.GaussianBlur(frame, (5,5), 0)
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    # red_mask = cv2.bitwise_and(frame_rgb, frame_rgb, mask=red_mask)
    lab = cv2.bitwise_and(lab, lab, mask=expanded_blue_and_red_mask)
    
    l_min = 0
    a_min = 130
    b_min = 140

    l_max = 255
    a_max = 255
    b_max = 255

    lower = np.array([l_min, a_min, b_min])
    upper = np.array([l_max, a_max, b_max])

    orange = cv2.inRange(lab, lower, upper)

    small_kernel = np.ones((2,2), np.uint8)
    kernel = np.ones((5,5), np.uint8)

    # orange = cv2.morphologyEx(orange, cv2.MORPH_OPEN, small_kernel)
    orange = cv2.morphologyEx(orange, cv2.MORPH_OPEN, small_kernel)
    orange = cv2.morphologyEx(orange, cv2.MORPH_DILATE, kernel)

    orange_circles = cv2.HoughCircles(
        orange, cv2.HOUGH_GRADIENT,
        dp=1, minDist=20,
        param1=50, param2=30,
        minRadius=5, maxRadius=1000
    )
    if VISUALIZE:
        cv2.circle(lab, (IMAGE_WIDTH//2, IMAGE_HEIGHT//2), 10, (0, 0, 255), 2)

        cv2.imshow("lab", lab)
        cv2.imshow("red_mask", red_mask)
        cv2.imshow("orange", orange)
        cv2.imshow("double_mask", expanded_blue_and_red_mask)

    if cv2.waitKey(1) == 27:
        return None, None, 0, 0
    
    # blue_circles = cv2.HoughCircles(blue, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=30, minRadius=5, maxRadius=1000)
    if orange_circles is not None:
        orange_circles = np.uint16(np.around(orange_circles))
        for i in orange_circles[0, :]:
            if VISUALIZE: 
                # draw the outer circle
                cv2.circle(red_mask, (i[0], i[1]), i[2], (0, 255, 0), 2)
                # draw the center of the circle
                cv2.circle(red_mask, (i[0], i[1]), 2, (0, 0, 255), 3)
                cv2.imshow("red_mask", red_mask)
            return i[0], i[1], i[2], cv2.countNonZero(orange)

    return None, None, 0, 0

import uuid

class Vehicle:
    def __init__(self):
        self.index = 0

        self.ser = SerialInterface()
        self.uwb = UWBInterface(self.ser)
        self.uwb.assign_id(str(uuid.getnode()))

        self.dist_to_other = 0

        try:
            self.camera = Picamera2()
            config = self.camera.create_preview_configuration({"size": (IMAGE_WIDTH, IMAGE_HEIGHT), "format": "RGB888"})
            self.camera.configure(config)
            self.camera.start()
        except Exception as e:
            print("Camera initialization failed:", e)
            self.camera = None
            
        time.sleep(0.2)
        
        self.uwb.ser.add_to_send_queue(f"*MY_IP={get_ip()}~")

        self.state = State.INIT_DEVICE_DISCOVERY
        
        # Initialize gpio
        self.chip = lgpio.gpiochip_open(0)

        self.us = UltrasonicSensor(self.chip, trigger_pin=US_TRIGGER_PIN, echo_pin=US_ECHO_PIN)

        self.movement_queue = []
        self.movement_state = MovementState.IDLE
        self.movement_data = {}

        # Initialize motor driver
        self.driver = L298NMotorDriver(
            chip=self.chip,
            in1=IN1, in2=IN2, ena=ENA,
            in3=IN3, in4=IN4, enb=ENB,
        )
        self.pid = pidController(self.chip, self.driver, ENCODER_L, ENCODER_R, self.us)

    def close_all(self):
        self.camera.stop()
        self.pid.close()
        self.driver.stop_all()
        lgpio.gpiochip_close(self.chip)

    def start_test(self, state):
        if state == MovementState.FOLLOW_TARGET_COLOR:
            self.movement_state = MovementState.FOLLOW_TARGET_COLOR
            self.pid.state = PID_State.OVERRIDE
            self.movement_data = {}
        elif state == MovementState.HUB_SPOKE:
            self.movement_state = MovementState.HUB_SPOKE
            self.movement_data = {"iterations": 4, "current_iteration": 0, "current_command_index": 0, "last_forward_time": 1}
        elif state == MovementState.BOUSTROPHEDON:
            self.boustrophedon_init()

    def update(self):
        if self.pid.state == PID_State.IDLE or self.pid.state == PID_State.OVERRIDE:
            if self.movement_state == MovementState.HUB_SPOKE:
                self.hub_spoke_movement()
            elif self.movement_state == MovementState.BOUSTROPHEDON:
                self.boustrophedon_movement()
            elif self.movement_state == MovementState.FOLLOW_TARGET_COLOR:
                self.follow_target_color()
            elif self.movement_state == MovementState.CELEBRATION:
                self.celebration_movement()
            elif self.movement_state == MovementState.CONVERGENCE:
                self.convergence_movement()

        cx, cy, cr, pixel_count = camera_process(self.camera)
        if cr > 0 and self.movement_state != MovementState.CELEBRATION:
            print(f"Detected object in path at ({cx}, {cy}) with radius {cr} and pixel count {pixel_count}. Stopping movement.")
            self.movement_data["seen_target_count"] = self.movement_data.get("seen_target_count", 0) + 1
            print(f"Seen target count: {self.movement_data['seen_target_count']}")
            if self.movement_data.get("seen_target_count", 0) >= SEEN_FRAMES_THRESHOLD:
                self.movement_queue = []
                self.movement_state = MovementState.CELEBRATION
                self.movement_data = {"degrees": 360*2} 
                return
        else:
            self.movement_data["seen_target_count"] = 0

        if self.pid.state == PID_State.IDLE and len(self.movement_queue) > 0 and self.movement_state != MovementState.FOLLOW_TARGET_COLOR:
            command = self.movement_queue.pop(0)
            if command[0] == "straight":
                self.pid.move_straight(speed=command[1], distance=command[2])
            elif command[0] == "rotate_right":
                self.pid.rotate_right(degrees=command[1])
            elif command[0] == "rotate_left":
                self.pid.rotate_left(degrees=command[1])
            elif command[0] == "wait":
                self.pid.wait(seconds=command[1])

        
        self.uwb.update()
        self.pid.update()

    def celebration_movement(self): 
        if self.movement_data.get("done_rotation", False) == False:
            self.movement_queue.append(("rotate_right", self.movement_data["degrees"]))
            self.movement_data["done_rotation"] = True
        else:
            if self.movement_data.get("timer", 0) >= 10:
                self.movement_data["timer"] = 0
                self.uwb.send_message("FOUND_TARGET")
            else:
                self.movement_data["timer"] = self.movement_data.get("timer", 0) + 1
                

    def start_convergence(self):
        self.movement_state = MovementState.CONVERGENCE
        self.movement_data = {"done_hub_spoke": False, "initial_distance": self.uwb.dist, 
                              "iterations": 4, "current_iteration": 0, "current_command_index": 0}
        self.movement_queue.append(("wait", 1))

    def convergence_movement(self):
        if self.movement_data.get("done_hub_spoke", False) == False:
            self.movement_data["done_hub_spoke"] = True
            self.movement_data["initial_distance"] = self.uwb.dist
            self.hub_spoke_movement()
            if self.movement_state == MovementState.IDLE: # hub spoke complete
                self.movement_state = MovementState.CONVERGENCE
                self.movement_data["done_hub_spoke"] = True
                self.movement_data["hub_spoke_result"] = "failed"
                
            elif self.movement_data["current_command_index"] == 2: # after waiting command
                if self.uwb.dist < self.movement_data["initial_distance"]:
                    self.movement_data["done_hub_spoke"] = True
                    self.movement_data["hub_spoke_result"] = "closer"
        else:
            if self.movement_data["hub_spoke_result"] == "closer":
                self.movement_queue.append(("straight", MOTOR_SPEED, 0.5))
            
            
        
    def follow_target_color(self):
        # If we see the target, move towards it
        cx, cy, cr, pixel_count = camera_process(self.camera)
        print(f"Pixel count: {pixel_count}, Centroid: ({cx}, {cy}), Radius: {cr}")
        if cr > 100:
            self.driver.stop_all()
            print(" Target acquired! Stopping motors.")
            return
        
        if cr < 100 and cx is not None and cy is not None:
            print("Target detected, adjusting movement.")
            # Simple proportional controller to center the target
            # positive if the target is to the right
            error_x = -(cx - IMAGE_WIDTH // 2)

            pix_frac = min((pixel_count - PIXEL_COUNT_THRESHOLD) // (PIXEL_COUNT_UPPER_THRESHOLD - PIXEL_COUNT_THRESHOLD), 1)
            if abs(error_x) < 50:
                print("Target centered, moving forward.")
                self.driver.motor_left_rotate(MOTOR_SPEED * (1-pix_frac))
                self.driver.motor_right_rotate(MOTOR_SPEED * (1-pix_frac))
                return

            # fraction of how many pixels we have between the threshold and upper threshold
            # pix_fraction = (min(pixel_count) - PIXEL_COUNT_THRESHOLD) // (PIXEL_COUNT_UPPER_THRESHOLD - PIXEL_COUNT_THRESHOLD)

            # Convert pixel error to motor speed adjustments
            k_px = 0.05

            speed_x = TURN_SPEED + int(k_px * error_x)
            # Cap speeds to max values

            # Set motor speeds (simple differential drive logic)
            left_speed = speed_x
            right_speed = -speed_x


            self.driver.motor_left_rotate(left_speed)
            self.driver.motor_right_rotate(right_speed)

        else:
            print("No target detected, searching...")
            # If we don't see the target, stop or search
            self.driver.motor_left_rotate(TURN_SPEED)
            self.driver.motor_right_rotate(-TURN_SPEED)

    def hub_spoke_movement(self):
        if self.movement_data["current_iteration"] >= self.movement_data["iterations"]:
            self.movement_state = MovementState.IDLE
            print("Test complete!")
        else:
            commands = [
                ("straight", MOTOR_SPEED, 1), # forward
                ("wait", 0.5),
                ("straight", -MOTOR_SPEED, 1), # backward
                ("wait", 0.5),
                ("rotate_right", 360/self.movement_data["iterations"], None), # degrees
                ("wait", 0.5),
            ]
            if self.movement_data["current_command_index"] < len(commands):
                command = commands[self.movement_data["current_command_index"]]

                if self.movement_data["current_command_index"] == 1:
                    self.movement_data["last_forward_distance"] = self.pid.state_values.get("final_distance_traveled", 1)
                if self.movement_data["current_command_index"] == 2:
                    # Adjust backward time based on how long the forward command took
                    forward_distance = self.movement_data.get("last_forward_distance", 1)
                    command = ("straight", -MOTOR_SPEED, forward_distance)
                        
                self.movement_data["current_command_index"] += 1
                self.movement_queue.append(command)
            else:
                self.movement_data["current_iteration"] += 1
                self.movement_data["current_command_index"] = 0

    def boustrophedon_init(self):
        self.movement_state = MovementState.BOUSTROPHEDON
        self.movement_data = {
            "current_lane": 0, 
            "total_lanes": 10,
            "first_rotate_right": 1, # 1 for right first, 0 for left first 

            "current_command_index": 0,
            }

    def boustrophedon_movement(self):
        if self.pid.state != PID_State.IDLE:
            return

        if self.movement_data["current_lane"] >= self.movement_data["total_lanes"]:
            self.movement_state = MovementState.IDLE
            print("Test complete!")
        else:
            commands = [
                ("straight", MOTOR_SPEED, 1), # forward     # 0
                ("wait", 0.5),                              # 1
                ("rotate", 90), # degrees                   # 2
                ("wait", 0.5),                              # 3
                ("straight", MOTOR_SPEED, 0.2), # forward   # 4
                ("wait", 0.5),                              # 5        
                ("rotate", 90), # degrees                   # 6
                ("wait", 0.5),                              # 7
            ]
            
            if self.movement_data["current_command_index"] < len(commands):
                command = commands[self.movement_data["current_command_index"]]

                # if self.movement_data["current_command_index"] == 1:
                #     self.movement_data["last_forward_distance"] = self.pid.state_values.get("final_distance_traveled", 1)
                # if self.movement_data["current_command_index"] == 2:
                #     # Adjust backward time based on how long the forward command took
                #     forward_distance = self.movement_data.get("last_forward_distance", 1)
                #     command = ("straight", -MOTOR_SPEED, forward_distance)

                if command[0] == "rotate":
                    # if first rotate is right (1), then even lanes (0) rotate right. so != => right turn
                    if self.movement_data["current_lane"] % 2 != self.movement_data["first_rotate_right"]:
                        command = ("rotate_right", command[1])
                    else:
                        command = ("rotate_left", command[1])
                        
                self.movement_data["current_command_index"] += 1
                self.movement_queue.append(command)
            else:
                self.movement_data["current_lane"] += 1
                self.movement_data["current_command_index"] = 0
                