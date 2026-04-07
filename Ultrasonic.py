# thanks, Gemini

import lgpio
import time

# --- Configuration ---

class UltrasonicSensor:
    def __init__(self, chip, trigger_pin, echo_pin):
        self.h = chip
        self.trigger_pin = trigger_pin
        lgpio.gpio_claim_output(self.h, self.trigger_pin)

        self.echo_pin = echo_pin
        lgpio.gpio_claim_input(self.h, self.echo_pin)

        self.pulse_start = 0
        self.distance = 0.0

        # Set up the alert (interrupt callback)
        # lgpio.SET_BOTH_EDGES captures both the start (High) and end (Low) of the pulse
        self.cb = lgpio.gpio_claim_alert(self.h, self.echo_pin, lgpio.BOTH_EDGES)
        lgpio.callback(self.h, self.echo_pin, lgpio.BOTH_EDGES, self._pulse_callback)

    def _pulse_callback(self, chip, gpio, level, tick):
        """
        This function runs automatically in a background thread 
        whenever the ECHO pin changes state.
        'tick' is a high-precision nanosecond timestamp from the kernel.
        """
        if level == 1:  # Rising edge (Echo starts)
            self.pulse_start = tick
        elif level == 0:  # Falling edge (Echo ends)
            if self.pulse_start > 0:
                duration = tick - self.pulse_start
                print(f"end tick: {tick} (duration={duration / 1000000000})")
                # Distance in cm = (nanoseconds * speed of sound) / 2 / 1,000,000
                self.distance = (duration * 343) / 2 / 1000000000
                self.pulse_start = 0

    def trigger(self):
        """Sends the 10us pulse."""
        lgpio.gpio_write(self.h, self.trigger_pin, 1)
        time.sleep(0.00001)  # 10 microseconds
        lgpio.gpio_write(self.h, self.trigger_pin, 0)
