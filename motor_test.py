import lgpio
from Motors import L298NMotorDriver
import time

# Motor 1
IN1 = 17
IN2 = 27
ENA = 12 # PWM
ENCODER1 = 23

# Motor 2
IN3 = 23
IN4 = 24
ENB = 13 # PWM
# TODO: other encoder

# IR sensor
IR_PIN = 22

if __name__ == "__main__":

    # Initialize gpio
    chip = lgpio.gpiochip_open(0)

    # Initialize motor driver
    driver = L298NMotorDriver(
        chip=chip,
        in1=IN1, in2=IN2, ena=ENA, 
        in3=IN3, in4=IN4, enb=ENB,
    )

    encoder_count = [0] # Will need to define two callbacks (L/R motor)

    def encoder_callback(chip, gpio, level, timestamp):
        encoder_count[0] += 1
        print("Encoder count:", encoder_count[0])

    # Callback for IR sensor
    def ir_callback(chip, gpio, level, timestamp):
        if level == 0: # Falling edge (1 -> 0)
            print("Object detected!!")
            driver.motor_a_backward(50)
        else:
            print("Object gone!!")
            driver.motor_a_forward(50)

    lgpio.gpio_claim_alert(chip, ENCODER1, lgpio.RISING_EDGE)
    cb = lgpio.callback(chip, ENCODER1, lgpio.RISING_EDGE, encoder_callback)

    lgpio.gpio_claim_alert(chip, IR_PIN, lgpio.BOTH_EDGES)
    cb = lgpio.callback(chip, IR_PIN, lgpio.BOTH_EDGES, ir_callback)

    driver.motor_a_forward(50)

    time.sleep(30)

    driver.stop_all()
    driver.cleanup()
