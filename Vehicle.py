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
    frame = camera.capture_array()

    # Convert to HSV
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # For tracking something bright orange
    lower = np.array([104, 150, 150])
    upper = np.array([120, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)

    h, w, _ = frame.shape
    pixel_count = cv2.countNonZero(mask)

    # Find centroid
    cx, cy = None, None
    moments = cv2.moments(mask)
    if moments["m00"] > 0:
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])

    return cx, cy, pixel_count

    #     # draw for debugging
    #     cv2.circle(frame, center=(cx, cy), radius=100, color=(255, 0, 0), thickness=2)

    # cv2.imshow("frame", frame)
    # cv2.imshow("mask", mask)



import uuid

class Vehicle:
    def __init__(self):
        self.index = 0

        self.ser = SerialInterface()
        self.uwb = UWBInterface(self.ser)
        self.uwb.assign_id(str(uuid.getnode()))

        self.camera = Picamera2()
        self.camera.configure(self.camera.create_preview_configuration(main={"size": (IMAGE_WIDTH, IMAGE_HEIGHT)}))
        self.camera.start()
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
        self.pid = pidController(self.chip, self.driver, ENCODER_L, ENCODER_R, IR_PIN, self.us)

    def start_test(self):
        self.movement_state = MovementState.FOLLOW_TARGET_COLOR
        self.pid.state = PID_State.OVERRIDE
        self.movement_data = {}
        # self.movement_state = MovementState.HUB_SPOKE
        # self.movement_data = {"iterations": 4, "current_iteration": 0, "current_command_index": 0, "last_forward_time": 1}

    def update(self):
        if self.pid.state == PID_State.IDLE or self.pid.state == PID_State.OVERRIDE:
            if self.movement_state == MovementState.HUB_SPOKE:
                self.hub_spoke_movement()
            elif self.movement_state == MovementState.BOUSTROPHEDON:
                pass
            elif self.movement_state == MovementState.FOLLOW_TARGET_COLOR:
                self.follow_target_color()

        if self.pid.state == PID_State.IDLE and len(self.movement_queue) > 0 and self.movement_state != MovementState.FOLLOW_TARGET_COLOR:
            command = self.movement_queue.pop(0)
            if command[0] == "straight":
                self.pid.move_straight(speed=command[1], seconds=command[2])
            elif command[0] == "rotate_right":
                self.pid.rotate_right(degrees=command[1])
            elif command[0] == "rotate_left":
                self.pid.rotate_left(degrees=command[1])
            elif command[0] == "wait":
                self.pid.wait(seconds=command[1])

        
        self.uwb.update()
        self.pid.update()

    def follow_target_color(self):
        # If we see the target, move towards it
        cx, cy, pixel_count = camera_process(self.camera)
        print(f"Pixel count: {pixel_count}, Centroid: ({cx}, {cy})")
        if pixel_count > PIXEL_COUNT_UPPER_THRESHOLD:
            self.driver.stop_all()
            print(" Target acquired! Stopping motors.")
            return
        
        if pixel_count > PIXEL_COUNT_THRESHOLD and cx is not None and cy is not None:
            print("Target detected, adjusting movement.")
            # Simple proportional controller to center the target
            # positive if the target is to the right
            error_x = -(cx - IMAGE_WIDTH // 2)

            pix_frac = min((pixel_count - PIXEL_COUNT_THRESHOLD) // (PIXEL_COUNT_UPPER_THRESHOLD - PIXEL_COUNT_THRESHOLD), 1)
            if abs(error_x) < 20:
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
                ("wait", 0, 0.5),
                ("straight", -MOTOR_SPEED, 1), # backward
                ("wait", 0, 0.5),
                ("rotate_right", 360/self.movement_data["iterations"], None), # degrees
                ("wait", 0, 0.5),
            ]
            if self.movement_data["current_command_index"] < len(commands):
                command = commands[self.movement_data["current_command_index"]]

                if self.movement_data["current_command_index"] == 1:
                    self.movement_data["last_forward_time"] = self.pid.state_values.get("time_elapsed", 0)
                if self.movement_data["current_command_index"] == 2:
                    # Adjust backward time based on how long the forward command took
                    forward_time = self.movement_data.get("last_forward_time", 1)
                    command = ("straight", -MOTOR_SPEED, forward_time)
                        
                self.movement_data["current_command_index"] += 1
                self.movement_queue.append(command)
            else:
                self.movement_data["current_iteration"] += 1
                self.movement_data["current_command_index"] = 0

    def boustrophedon_init(self):
        self.movement_state = MovementState.BOUSTROPHEDON
        self.movement_data = {
            "state": BoustrophedonState.IDLE, 
            "current_lane": 0, 
            "total_lanes": 10
            }

    def boustrophedon_movement(self):
        if self.pid.state != PID_State.IDLE:
            return
        
        data = self.movement_data
        state = data["state"]

        if state == BoustrophedonState.IDLE:
            data["state"] = BoustrophedonState.LONG

        elif state == BoustrophedonState.LONG:
            self.pid.move_straight(speed=MOTOR_SPEED, seconds=3)
            if data["current_lane"] % 2 == 0: 
                data["state"] = BoustrophedonState.TURNING_RIGHT_LONG
            else:
                data["state"] = BoustrophedonState.TURNING_LEFT_LONG

        elif state == BoustrophedonState.TURNING_RIGHT_LONG:
            self.pid.rotate_right(degrees=90)
            data["state"] = BoustrophedonState.SHORT

        elif state == BoustrophedonState.TURNING_LEFT_LONG:
            self.pid.rotate_left(degrees=90)
            data["state"] = BoustrophedonState.SHORT 

        elif state == BoustrophedonState.SHORT:
            self.pid.move_straight(speed=MOTOR_SPEED, seconds=1)
            if data["current_lane"] % 2 == 0: 
                data["state"] = BoustrophedonState.TURNING_RIGHT_SHORT
            else:
                data["state"] = BoustrophedonState.TURNING_LEFT_SHORT

            data["current_lane"] += 1

        elif state == BoustrophedonState.TURNING_RIGHT_SHORT:
            if data["current_lane"] >= data["total_lanes"]:
                data["state"] = BoustrophedonState.DONE
            else:
                self.pid.rotate_right(degrees=90)
                data["state"] = BoustrophedonState.LONG

        elif state == BoustrophedonState.TURNING_LEFT_SHORT:
            if data["current_lane"] >= data["total_lanes"]:
                data["state"] = BoustrophedonState.DONE
            else:
                self.pid.rotate_left(degrees=90)
                data["state"] = BoustrophedonState.LONG

        elif state == BoustrophedonState.DONE:
                print("Boustrophedon complete!")  
                self.movement_state = MovementState.IDLE
                data["state"] = BoustrophedonState.IDLE