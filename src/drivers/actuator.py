"""
Driver classes for actuators (MOSFET-driven digital fan switch) and RGB indicator.
Compatible with Raspberry Pi Pico (MicroPython).
"""

from machine import Pin


class Actuator:
    """
    Digital ON/OFF power actuator driver (e.g. for a MOSFET-switched fan).
    Operates via standard GPIO output without PWM.
    """

    def __init__(self, pin_num: int, name: str = "Fan", active_high: bool = True, **kwargs):
        """
        Initialize digital actuator.
        :param pin_num: GPIO pin number.
        :param name: Human-readable identifier.
        :param active_high: True if HIGH level turns actuator ON (standard N-MOSFET).
        """
        self.name = name
        self._active_high = active_high
        self._state = False

        self._pin = Pin(pin_num, Pin.OUT)
        self.off()

    def on(self):
        """Turn actuator fully ON."""
        self._state = True
        self._pin.value(1 if self._active_high else 0)

    def off(self):
        """Turn actuator OFF."""
        self._state = False
        self._pin.value(0 if self._active_high else 1)

    def toggle(self):
        """Toggle current state."""
        if self._state:
            self.off()
        else:
            self.on()

    def set_state(self, state: bool):
        """Explicitly set actuator state (True=ON, False=OFF)."""
        if state:
            self.on()
        else:
            self.off()

    def set_level(self, percent: float):
        """
        Compatibility fallback for level-based control.
        Switches ON if percent > 0, otherwise switches OFF.
        """
        if percent > 0:
            self.on()
        else:
            self.off()

    @property
    def is_active(self) -> bool:
        """Returns True if the actuator is currently running/on."""
        return self._state

    def __str__(self):
        return f"{self.name}(state={'ON' if self._state else 'OFF'})"


# Convenient alias
Fan = Actuator


class RGBIndicator:
    """
    Reusable abstraction for 3-channel RGB status LED (common cathode or common anode).
    """

    def __init__(self, r_pin: int, g_pin: int, b_pin: int, common_anode: bool = False):
        self._r = Pin(r_pin, Pin.OUT)
        self._g = Pin(g_pin, Pin.OUT)
        self._b = Pin(b_pin, Pin.OUT)
        self._invert = common_anode
        self.off()

    def set_color(self, red: bool, green: bool, blue: bool):
        """Set individual color channels (True=ON, False=OFF)."""
        r_val = not red if self._invert else red
        g_val = not green if self._invert else green
        b_val = not blue if self._invert else blue

        self._r.value(1 if r_val else 0)
        self._g.value(1 if g_val else 0)
        self._b.value(1 if b_val else 0)

    def off(self):
        """Turn off all LED channels."""
        self.set_color(False, False, False)

    def ok(self):
        """Green: normal operating state."""
        self.set_color(False, True, False)

    def warning(self):
        """Yellow / Orange (Red + Green): threshold exceeded / active regulation."""
        self.set_color(True, True, False)

    def alert(self):
        """Red: critical state or sensor fault."""
        self.set_color(True, False, False)

    def connecting(self):
        """Blue: connecting or transmitting."""
        self.set_color(False, False, True)
