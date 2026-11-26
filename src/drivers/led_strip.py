"""
NeoPixel LED strip controller module for Raspberry Pi Pico.
Provides a simple class-based interface to initialize the strip, 
change the active color, and toggle the LEDs on or off.

Author: Richard Kralovsky

History
12.11.2026 Init.
12.11.2026 Tested functionality (test_led_strip.py + test_LightControl.py) decided whether to use white or purple light -> purple
19.11.2026 Verified integrated functionality in main
"""
import machine
import neopixel

class LEDStrip:
    """Controller for an addressable WS2812B NeoPixel LED strip."""

    def __init__(self, pin, num_leds=1000):
        """Initialize the NeoPixel LED strip on the given GPIO pin.

        :param pin: GPIO pin number connected to the LED strip data line.
        :param num_leds: Number of addressable LEDs in the strip.
        """
        self.np = neopixel.NeoPixel(machine.Pin(pin), num_leds)
        self.on_color = (200, 0, 200) # purple

    def set_state(self, state):
        """Turn the entire LED strip ON or OFF.

        :param state: ``1`` to turn on using ``on_color``, ``0`` to turn off.
        """
        if state == 1:
            self.np.fill(self.on_color)
        else:
            self.np.fill((0, 0, 0))
        self.np.write()

    def set_color(self, r, g, b):
        """Change the active RGB color used when the strip is turned ON.

        :param r: Red channel intensity (0–255).
        :param g: Green channel intensity (0–255).
        :param b: Blue channel intensity (0–255).
        """
        self.on_color = (r, g, b)