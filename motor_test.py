import lgpio
from Motors import L298NMotorDriver
import time

# Left motor
IN1 = 17
IN2 = 27
ENA = 22 # PWM
ENCODER_L = 4

# Motor 2
IN3 = 23
IN4 = 24
ENB = 25 # PWM
ENCODER_R = 18

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

    encoder_count = {"left": 0, "right": 0}

    def encoder_left_callback(chip, gpio, level, timestamp):
        encoder_count["left"] += 1
        print("[left]: Encoder count =", encoder_count["left"])

    def encoder_right_callback(chip, gpio, level, timestamp):
        encoder_count["right"] += 1
        print("[right]: Encoder count =", encoder_count["right"])

    # Callback for IR sensor
    def ir_callback(chip, gpio, level, timestamp):
        if level == 0: # Falling edge (1 -> 0)
            print("Object detected!!")
            driver.motor_left_backward(50)
            driver.motor_right_backward(50)
        else:
            print("Object gone!!")
            driver.motor_left_forward(50)
            driver.motor_right_forward(50)

    lgpio.gpio_claim_alert(chip, ENCODER_L, lgpio.RISING_EDGE)
    cb = lgpio.callback(chip, ENCODER_L, lgpio.RISING_EDGE, encoder_left_callback)

    lgpio.gpio_claim_alert(chip, ENCODER_R, lgpio.RISING_EDGE)
    cb = lgpio.callback(chip, ENCODER_R, lgpio.RISING_EDGE, encoder_right_callback)

    lgpio.gpio_claim_alert(chip, IR_PIN, lgpio.BOTH_EDGES)
    cb = lgpio.callback(chip, IR_PIN, lgpio.BOTH_EDGES, ir_callback)

    driver.motor_left_forward(50)
    driver.motor_right_forward(50)

    time.sleep(5)

    driver.stop_all()
    driver.cleanup()
