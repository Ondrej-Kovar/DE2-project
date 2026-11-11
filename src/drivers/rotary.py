"""
Rotary encoder driver (KY-040) with integrated push button for MicroPython.
"""

from machine import Pin
import time

class RotaryEncoder:
    """
    KY-040 Rotary Encoder driver using interrupt-driven or polled quadrature decoding.
    Includes debounced push button handling.
    """

    def __init__(self, clk_pin: int, dt_pin: int, sw_pin: int, min_val: int = 0, max_val: int = 100, step: int = 1):
        self._clk = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self._dt = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self._sw = Pin(sw_pin, Pin.IN, Pin.PULL_UP)

        self._min_val = min_val
        self._max_val = max_val
        self._step = step
        self.value = 25  # default value

        self._last_clk = self._clk.value()
        self._last_btn_state = self._sw.value()
        self._last_btn_time = time.ticks_ms()

        # Setup IRQ on CLK pin for responsive edge detection
        self._clk.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._on_rotate)

    def _on_rotate(self, pin):
        clk_state = self._clk.value()
        if clk_state != self._last_clk and clk_state == 0:
            if self._dt.value() != clk_state:
                self.value = min(self._max_val, self.value + self._step)
            else:
                self.value = max(self._min_val, self.value - self._step)
        self._last_clk = clk_state

    def is_button_pressed(self) -> bool:
        """
        Check if button was pressed with non-blocking software debounce (50 ms).
        Returns True once per click.
        """
        now = time.ticks_ms()
        val = self._sw.value()
        pressed = False

        if val == 0 and self._last_btn_state == 1:
            if time.ticks_diff(now, self._last_btn_time) > 50:
                pressed = True
                self._last_btn_time = now

        self._last_btn_state = val
        return pressed

    def set_range(self, min_val: int, max_val: int, current_val: int = None, step: int = 1):
        """Update value limits and step size."""
        self._min_val = min_val
        self._max_val = max_val
        self._step = step
        if current_val is not None:
            self.value = max(min_val, min(max_val, current_val))
