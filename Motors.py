# Write and read from motors and encoders
# thanks chatgpt

import lgpio


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
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.ena = ena
        self.enb = enb
        self.pwm_freq = pwm_freq

        for pin in [in1, in2, in3, in4]:
            lgpio.gpio_claim_output(self.h, pin)
            lgpio.gpio_write(self.h, pin, 0)

        lgpio.gpio_claim_output(self.h, ena)
        lgpio.gpio_claim_output(self.h, enb)

        self._set_speed(self.ena, 0)
        self._set_speed(self.enb, 0)

    # ---- Motor A ----
    def motor_a_forward(self, speed=100):
        lgpio.gpio_write(self.h, self.in1, 1)
        lgpio.gpio_write(self.h, self.in2, 0)
        self._set_speed(self.ena, speed)

    def motor_a_backward(self, speed=100):
        lgpio.gpio_write(self.h, self.in1, 0)
        lgpio.gpio_write(self.h, self.in2, 1)
        self._set_speed(self.ena, speed)

    def motor_a_stop(self):
        lgpio.gpio_write(self.h, self.in1, 0)
        lgpio.gpio_write(self.h, self.in2, 0)
        self._set_speed(self.ena, 0)

    # ---- Motor B ----
    def motor_b_forward(self, speed=100):
        lgpio.gpio_write(self.h, self.in3, 1)
        lgpio.gpio_write(self.h, self.in4, 0)
        self._set_speed(self.enb, speed)

    def motor_b_backward(self, speed=100):
        lgpio.gpio_write(self.h, self.in3, 0)
        lgpio.gpio_write(self.h, self.in4, 1)
        self._set_speed(self.enb, speed)

    def motor_b_stop(self):
        lgpio.gpio_write(self.h, self.in3, 0)
        lgpio.gpio_write(self.h, self.in4, 0)
        self._set_speed(self.enb, 0)

    # ---- Helpers ----
    def stop_all(self):
        self.motor_a_stop()
        self.motor_b_stop()

    def cleanup(self):
        self.stop_all()

    def _set_speed(self, pin, speed):
        speed = max(0, min(100, speed))
        duty = speed  # lgpio expects duty cycle in %
        lgpio.tx_pwm(self.h, pin, self.pwm_freq, duty)
