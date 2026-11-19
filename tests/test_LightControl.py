"""
Code used to test the automated light control system. (led_strip.py + light_sensor.py)
It reads the voltage from an LDR voltage divider and controls a NeoPixel LED strip 
based on ambient light levels using software hysteresis to prevent flickering.
"""
import time
from machine import ADC

# Module light sensor measures voltage from voltage divider using ADC 
# and decides if light is turned on or off (hysteresis)
# For better stability averaging is used
# Vcc -> LDR -> 5 kOhm -> GND
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


import machine
import neopixel

class LEDStrip:
    def __init__(self, pin, num_leds=1000):
        self.np = neopixel.NeoPixel(machine.Pin(pin), num_leds)
        self.on_color = (200, 0, 200) # purple

    def set_state(self, state):
        """Accepts 1 (turn on) or 0 (turn off)."""
        if state == 1:
            self.np.fill(self.on_color)
        else:
            self.np.fill((0, 0, 0))
        self.np.write()

    def set_color(self, r, g, b):
        """Optional method to change color during runtime."""
        self.on_color = (r, g, b)


def main():
    # Initialize the sensor on pin GP26 (ADC0) with hysteresis thresholds
    sensor = LightSensor(26, v_low=1.5, v_high=2)
    
    # Initialize the LED strip on pin GP14
    strip = LEDStrip(14)
    
    print("Starting automated light control. Press Ctrl+C to stop.")
    
    try:
        while True:
            # 1. Evaluate the sensor (unpack both returned values)
            light_state, voltage = sensor.check_light()
            
            # 2. Pass the command directly to the LED strip
            strip.set_state(light_state)
            
            # Console status output with voltage
            if light_state == 1:
                print(f"U_LDR: {voltage:.2f} V | It is dark -> LED strip is ON")
            else:
                print(f"U_LDR: {voltage:.2f} V | Enough light -> LED strip is OFF")
            
            # 3. Sleep for 1 second
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nProgram stopped.")
    finally:
        # Safely turn off the strip upon interruption
        strip.set_state(0)

if __name__ == "__main__":
    main()