# Write and read from motors and encoders
# chatgpt

import RPi.GPIO as GPIO
import time


class L298NMotorDriver:
    """
    Simple L298N motor driver class for Raspberry Pi.
    Controls two DC motors using IN1–IN4 and optional ENA/ENB (PWM).
    """

    def __init__(
        self,
        in1, in2, in3, in4,
        ena=None, enb=None,
        pwm_freq=1000
    ):
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.ena = ena
        self.enb = enb
        self.pwm_freq = pwm_freq

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in [in1, in2, in3, in4]:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        self.pwm_a = None
        self.pwm_b = None

        if ena is not None:
            GPIO.setup(ena, GPIO.OUT)
            self.pwm_a = GPIO.PWM(ena, pwm_freq)
            self.pwm_a.start(0)

        if enb is not None:
            GPIO.setup(enb, GPIO.OUT)
            self.pwm_b = GPIO.PWM(enb, pwm_freq)
            self.pwm_b.start(0)

    # ---- Motor A ----
    def motor_a_forward(self, speed=100):
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)
        self._set_speed(self.pwm_a, speed)

    def motor_a_backward(self, speed=100):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.HIGH)
        self._set_speed(self.pwm_a, speed)

    def motor_a_stop(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        self._set_speed(self.pwm_a, 0)

    # ---- Motor B ----
    def motor_b_forward(self, speed=100):
        GPIO.output(self.in3, GPIO.HIGH)
        GPIO.output(self.in4, GPIO.LOW)
        self._set_speed(self.pwm_b, speed)

    def motor_b_backward(self, speed=100):
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.HIGH)
        self._set_speed(self.pwm_b, speed)

    def motor_b_stop(self):
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)
        self._set_speed(self.pwm_b, 0)

    # ---- Helpers ----
    def stop_all(self):
        self.motor_a_stop()
        self.motor_b_stop()

    def cleanup(self):
        self.stop_all()
        if self.pwm_a:
            self.pwm_a.stop()
        if self.pwm_b:
            self.pwm_b.stop()
        GPIO.cleanup()

    @staticmethod
    def _set_speed(pwm, speed):
        if pwm is None:
            return
        speed = max(0, min(100, speed))
        pwm.ChangeDutyCycle(speed)
