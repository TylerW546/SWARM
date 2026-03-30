# Write and read from motors and encoders
# thanks chatgpt

import lgpio
import time
import math

class L298NMotorDriver:
    """
    Simple L298N motor driver class for Raspberry Pi using lgpio.
    Controls two DC motors using IN1-IN4 and ENA/ENB (PWM).
    """

    def __init__(
        self,
        chip,
        in1, in2, in3, in4,
        ena, enb,
        pwm_freq=1000
    ):
        self.h = chip

        # Left motor
        self.in1 = in1
        self.in2 = in2
        self.ena = ena

        # Right motor
        self.in3 = in3
        self.in4 = in4
        self.enb = enb
        self.pwm_freq = pwm_freq

        for pin in [in1, in2, in3, in4]:
            lgpio.gpio_claim_output(self.h, pin)
            lgpio.gpio_write(self.h, pin, 0)

        lgpio.gpio_claim_output(self.h, ena)
        lgpio.gpio_claim_output(self.h, enb)

        self._set_speed(self.ena, 0)
        self._set_speed(self.enb, 0)

    # ---- Motor left ----
    def motor_left_forward(self, speed=100):
        lgpio.gpio_write(self.h, self.in1, 1)
        lgpio.gpio_write(self.h, self.in2, 0)
        self._set_speed(self.ena, speed)

    def motor_left_backward(self, speed=100):
        lgpio.gpio_write(self.h, self.in1, 0)
        lgpio.gpio_write(self.h, self.in2, 1)
        self._set_speed(self.ena, speed)

    def motor_left_stop(self):
        lgpio.gpio_write(self.h, self.in1, 0)
        lgpio.gpio_write(self.h, self.in2, 0)
        self._set_speed(self.ena, 0)

    # ---- Motor right ----
    def motor_right_forward(self, speed=100):
        lgpio.gpio_write(self.h, self.in3, 1)
        lgpio.gpio_write(self.h, self.in4, 0)
        self._set_speed(self.enb, speed)

    def motor_right_backward(self, speed=100):
        lgpio.gpio_write(self.h, self.in3, 0)
        lgpio.gpio_write(self.h, self.in4, 1)
        self._set_speed(self.enb, speed)

    def motor_right_stop(self):
        lgpio.gpio_write(self.h, self.in3, 0)
        lgpio.gpio_write(self.h, self.in4, 0)
        self._set_speed(self.enb, 0)

    # ---- Rotation ----
    def rotate_motors(self, duration, speed=100):
        self.motor_left_forward(self, speed=100)
        self.motor_right_backward(self, speed=100)
        time.sleep(duration)
        self.stop_all()

    def degrees_turn(self, degrees, speed=100):
        duration = degrees/360
        rotate_motors(self, duration, speed=100)
        self.stop_all()

    def move_to_coord(self, dx, dy, speed=100): #(dx dy) = (target position - current position)
        dist = math.sqrt(dx**2 + dy**2)
        duration = dist/speed
        angle = math.atan2(dy,dx) * (180/math.pi)
        self.degree_turn(self, angle, speed=100)
        self.motor_left_forward(self, speed=100)
        self.motor_right_forward(self, speed=100)
        time.sleep(duration)
        self.stop_all()
    
    # ---- Helpers ----
    def stop_all(self):
        self.motor_left_stop()
        self.motor_right_stop()

    def cleanup(self):
        self.stop_all()

    def _set_speed(self, pin, speed):
        speed = max(0, min(100, speed))
        duty = speed  # lgpio expects duty cycle in %
        lgpio.tx_pwm(self.h, pin, self.pwm_freq, duty)
