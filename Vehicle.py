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

        # Initialize motor driver
        self.driver = L298NMotorDriver(
            chip=self.chip,
            in1=IN1, in2=IN2, ena=ENA,
            in3=IN3, in4=IN4, enb=ENB,
        )
        self.pid = pidController(self.chip, self.driver, ENCODER_L, ENCODER_R)

    def start_test(self):
        for _ in range(4):
            self.movement_queue.append(("straight", 30, 1)) # forward
            self.movement_queue.append(("wait", 0.5)) # wait
            self.movement_queue.append(("straight", -30, 1)) # backward
            self.movement_queue.append(("wait", 0.5)) # wait
            self.movement_queue.append(("rotate_right", 90)) # degrees
            self.movement_queue.append(("wait", 0.5)) # wait


    def update(self):
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
        
    def start_imu_process(self):
        pass

    def start_communication_module(self):
        pass

    def start_device_discovery(self):
        pass