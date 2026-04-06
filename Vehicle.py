import uuid

from Communications import *
from Environment import *
from Motors import *
import UWBInterface
from SerialInterface import SerialInterface
from UWBInterface import *
from Util import *
from pidController import pidController
import serial


import uuid

# Right motor
IN1 = 17
IN2 = 27
ENA = 22 # PWM
ENCODER_R = 16

# Left motor
IN3 = 23
IN4 = 24
ENB = 25 # PWM
ENCODER_L = 19

# IR sensor
IR_PIN = 26

class Vehicle:
    def __init__(self):
        self.index = 0

        self.ser = SerialInterface()
        self.uwb = UWBInterface(self.ser)
        self.uwb.assign_id(str(uuid.getnode()))
        
        self.uwb.ser.add_to_send_queue(f"*MY_IP={get_ip()}~")

        self.state = State.INIT_DEVICE_DISCOVERY
        
        # Initialize gpio
        self.chip = lgpio.gpiochip_open(0)

        self.movement_queue = []
        self.movement_state = MovementState.IDLE
        self.movement_data = {}

        # Initialize motor driver
        self.driver = L298NMotorDriver(
            chip=self.chip,
            in1=IN1, in2=IN2, ena=ENA,
            in3=IN3, in4=IN4, enb=ENB,
        )
        self.pid = pidController(self.chip, self.driver, ENCODER_L, ENCODER_R, IR_PIN)

    def start_test(self):
        self.movement_state = MovementState.HUB_SPOKE
        self.movement_data = {"iterations": 4, "current_iteration": 0, "current_command_index": 0, "last_forward_time": None}

    def update(self):
        if self.pid.state == PID_State.IDLE:
            if self.movement_state == MovementState.HUB_SPOKE:
                self.hub_spoke_movement()
            if self.movement_state == MovementState.Boustrophedon:
                self.boustrophedon_movement()
                
        if self.pid.state == PID_State.IDLE and len(self.movement_queue) > 0:
            command = self.movement_queue.pop(0)
            if command[0] == "straight":
                self.pid.move_straight(speed=command[1], seconds=command[2])
            elif command[0] == "rotate_right":
                self.pid.rotate_right(degrees=command[1])
            elif command[0] == "wait":
                self.pid.wait(seconds=command[1])

        
        self.uwb.update()
        self.pid.update()

    def hub_spoke_movement(self):
        if self.movement_data["current_iteration"] >= self.movement_data["iterations"]:
            self.movement_state = MovementState.IDLE
            print("Test complete!")
        else:
            commands = [
                ("straight", 30, 1), # forward
                ("wait", 0, 0.5),
                ("straight", -30, 1), # backward
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
                    command = ("straight", -50, forward_time)
                        
                self.movement_data["current_command_index"] += 1
                if command[0] == "straight":
                    self.movement_queue.append(command)
                elif command[0] == "rotate_right":
                    self.movement_queue.append(command)
                elif command[0] == "wait":
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
            self.pid.move_straight(speed=30, seconds=3)
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
            self.pid.move_straight(speed=30, seconds=1)
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

    
        
    def start_imu_process(self):
        pass

    def start_communication_module(self):
        pass

    def start_device_discovery(self):
        pass