"""
NeoPixel LED strip controller module for Raspberry Pi Pico.
Provides a simple class-based interface to initialize the strip, 
change the active color, and toggle the LEDs on or off.
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