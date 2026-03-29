import lgpio
from Motors import L298NMotorDriver
from pidController import pidController

# Right motor
IN1 = 17
IN2 = 27
ENA = 22 # PWM
ENCODER_R = 18

# Left motor
IN3 = 23
IN4 = 24
ENB = 25 # PWM
ENCODER_L = 4

# IR sensor
IR_PIN = 26

if __name__ == "__main__":

    # Initialize gpio
    chip = lgpio.gpiochip_open(0)

    # Initialize motor driver
    driver = L298NMotorDriver(
        chip=chip,
        in1=IN1, in2=IN2, ena=ENA,
        in3=IN3, in4=IN4, enb=ENB,
    )

    pid = pidController(chip, driver, ENCODER_L, ENCODER_R)

    pid.straight_forward(speed=30, seconds=2)
    pid.rotate_right(180) # degrees
    driver.stop_all()
    driver.cleanup()
