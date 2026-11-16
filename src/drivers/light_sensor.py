"""
Light sensor module for Raspberry Pi Pico.
Reads ambient light levels via an ADC pin connected to an LDR voltage divider.
Applies software hysteresis and multi-sample averaging to determine the 
required LED strip state without flickering.

Based on optional task including LDR from LAB5-adc in DE2 course
"""
# Vcc -> LDR -> 5 kOhm -> GND (for implemetation)

import time
from machine import ADC

class LightSensor:
    def __init__(self, pin, v_low=0.5, v_high=1.0):
        self.adc = ADC(pin)
        self.light_on = False
        self.v_low = v_low
        self.v_high = v_high

    def read_voltage(self, samples=10):
        total = 0
        for _ in range(samples):
            total += self.adc.read_u16()
        
        average = round(total / samples)
        voltage = average * 3.3 / 65535
        return voltage

    def check_light(self):
        voltage = self.read_voltage()
        
        if voltage < self.v_low:
            self.light_on = True   # Dark - turn the light on
        elif voltage > self.v_high:
            self.light_on = False  # Light - turn the light off
        
        # Returns a tuple: (status 1/0, measured voltage)
        return (1 if self.light_on else 0), voltage
    
if __name__ == "__main__": 
    # Quick testing code - validates functionality of voltage divider and LED command
    sensor = LightSensor(26)
    
    try:
        while True:
            # check_light() directly returns both the LED status and the voltage
            led_command, voltage = sensor.check_light()
            
            print(f"U: {voltage:.2f} V | LED command: {led_command}")
            time.sleep_ms(500)
    except KeyboardInterrupt:
        pass