import lgpio
from Motors import L298NMotorDriver
from pidController import pidController
import time
from Util import *
from Ultrasonic import UltrasonicSensor

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

# Ultrasonic sensor
US_ECHO_PIN = 9
US_TRIGGER_PIN = 11

def run_test():

    # Initialize gpio
    chip = lgpio.gpiochip_open(0)

    # Initialize ultrasonic sensor
    sonar = UltrasonicSensor(chip, trigger_pin=US_TRIGGER_PIN, echo_pin=US_ECHO_PIN)

    # Initialize motor driver
    driver = L298NMotorDriver(
        chip=chip,
        in1=IN1, in2=IN2, ena=ENA,
        in3=IN3, in4=IN4, enb=ENB,
    )

    # for _ in range(1000):
    #     sonar.trigger()
    #     print(f"distance={sonar.distance:.3f}m")
        # time.sleep(0.5)

    pid = pidController(chip, driver, ENCODER_L, ENCODER_R, IR_PIN, sonar)
    pid.move_straight(35, 1)

    while (1):
        pid.update()
        if pid.state == PID_State.IDLE:
            break

        time.sleep(0.05)

    print("before")
    time.sleep(.5)
    print("after")

    pid.move_straight(-35, 1)

    while (1):
        pid.update()
        if pid.state == PID_State.IDLE:
            break

        time.sleep(0.05)

    # for _ in range(4):

    #     pid.move_straight(speed=30, distance=0.3) # forward
    #     time.sleep(0.5)
    #     pid.move_straight(speed=-30, distance=0.3) # backward
    #     time.sleep(0.5)
    #     pid.rotate_right(90) # degrees
    #     time.sleep(0.5)    
    # '''

    driver.stop_all()
    driver.cleanup()

if __name__ == "__main__":
    run_test()