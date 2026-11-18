"""
Light sensor module for Raspberry Pi Pico.
Reads ambient light levels via an ADC pin connected to an LDR voltage divider.
Applies software hysteresis and multi-sample averaging to determine the
required LED strip state without flickering.

Based on optional task including LDR from LAB5 adc_read.py in DE2 course.
"""
# Vcc -> LDR -> 5 kOhm -> GND (for implementation)

from machine import ADC

class LightSensor:
    def __init__(self, pin, light_low=15, light_high=30):
        self.adc = ADC(pin)
        self.light_on = False
        self.light_low = light_low
        self.light_high = light_high

    def read_voltage(self, samples=10):
        """Return averaged raw voltage (0.0 to 3.3 V)."""
        total = 0
        for _ in range(samples):
            total += self.adc.read_u16()

        average = round(total / samples)
        voltage = average * 3.3 / 65535
        return voltage

    def read_percentage(self, samples=10):
        """Convert averaged voltage to a relative light level (0 to 100%)."""
        voltage = self.read_voltage(samples)
        pct = int(round((voltage / 3.3) * 100))
        return max(0, min(100, pct)) #backup so we dont exceed 100 or go below 0 %

    def check_light(self):
        """Apply hysteresis and return (led_state 1/0, light_pct)."""
        light_pct = self.read_percentage()

        if light_pct < self.light_low:
            self.light_on = True   # Dark - turn the light on
        elif light_pct > self.light_high:
            self.light_on = False  # Bright - turn the light off

        # Returns a tuple: (status 1/0, relative light level in %)
        return (1 if self.light_on else 0), light_pct