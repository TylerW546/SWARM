import lgpio
from Motors import L298NMotorDriver
from pidController import pidController
import time
from Util import *
from Ultrasonic import UltrasonicSensor

import matplotlib.pyplot as plt

def run_test_file():

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

    encoder_count = {"left": 0, "right": 0}

    # def encoder_left_callback(chip, gpio, level, timestamp):
    #     encoder_count["left"] += 1
    #     # print("[left]: Encoder count =", encoder_count["left"])

    # def encoder_right_callback(chip, gpio, level, timestamp):
    #     encoder_count["right"] += 1
    #     # print("[right]: Encoder count =", encoder_count["right"])

    # lgpio.gpio_claim_alert(chip, ENCODER_L, lgpio.RISING_EDGE)
    # lgpio.gpio_claim_alert(chip, ENCODER_R, lgpio.RISING_EDGE)

    # ecbl = lgpio.callback(chip, ENCODER_L, lgpio.RISING_EDGE, encoder_left_callback)
    # ecbr = lgpio.callback(chip, ENCODER_R, lgpio.RISING_EDGE, encoder_right_callback)

    # driver.motor_left_rotate(100)
    # driver.motor_right_rotate(100)

    now = time.perf_counter()
    time.sleep(1)
    print(time.perf_counter() - now)

    # print(COUNT_TO_METERS)

    # print(encoder_count)

    pid = pidController(chip, driver, ENCODER_L, ENCODER_R, sonar)
    # pid.move_straight(45, 1)

    # start = time.perf_counter()
    # while (1):
    #     pid.update()
    #     if pid.state == PID_State.IDLE:
    #         break

    #     time.sleep(0.05)

    # elapsed = time.perf_counter() - start
    # print(f"All done. Elapsed: {elapsed:.2f}s")

    start = time.perf_counter()
    target_speed = 30
    # pid.move_straight(-target_speed, 1)
    pid.rotate_right(90)
    while (1):
        pid.update()
        if pid.state == PID_State.IDLE:
            break

        time.sleep(0.03)

    elapsed = time.perf_counter() - start
    print(f"All done. Elapsed: {elapsed}s")

    driver.stop_all()
    driver.cleanup()

    left_signals = []
    left_speeds = []
    right_speeds = []
    right_signals = []
    for i in range(len(pid.signal_history)):
        left_signals.append(pid.signal_history[i]["left"])
        left_speeds.append(pid.speed_history[i]["left"])
        right_signals.append(pid.signal_history[i]["right"])
        right_speeds.append(pid.speed_history[i]["right"])
    plt.plot(left_speeds, label="l_speeds")
    plt.plot(right_speeds, label="r_speeds")
    plt.axhline(target_speed, linestyle="--")
    # plt.plot(left_signals, label="l_signals")
    # plt.plot(right_signals, label="r_signals")

    plt.legend()
    plt.show()



if __name__ == "__main__":
    run_test_file()
