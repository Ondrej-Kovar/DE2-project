"""
Qucik standalone test for led_strip.py module
"""
import machine
import neopixel
import time

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

if __name__ == "__main__": 
    # Quick testing code - toggles the strip on for 2 seconds, then off
    strip = LEDStrip(2)
    
    try:
        strip.set_state(1)
        print("LED Strip on")
        time.sleep(2)

        strip.set_state(0)
        print("LED Strip off")
            
    except KeyboardInterrupt:
        # Safely turn off the strip if the test is interrupted
        strip.set_state(0)