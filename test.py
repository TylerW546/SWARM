import lgpio
from Motors import L298NMotorDriver
from pidController import pidController
import time

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

def run_test():

    # Initialize gpio
    chip = lgpio.gpiochip_open(0)

    # Initialize motor driver
    driver = L298NMotorDriver(
        chip=chip,
        in1=IN1, in2=IN2, ena=ENA,
        in3=IN3, in4=IN4, enb=ENB,
    )

    pid = pidController(chip, driver, ENCODER_L, ENCODER_R)

    for _ in range(4):
        
        pid.straight_forward(speed=30, meters=1)
        pid.rotate_right(90) # degrees
        time.sleep(0.5)
    
    driver.stop_all()
    driver.cleanup()

if __name__ == "__main__":
    run_test()
