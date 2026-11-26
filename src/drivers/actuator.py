"""
File:        actuator.py
Project:     Smart Greenhouse Monitor (DE2)
Platform:    Raspberry Pi Pico W (MicroPython)
Authors:     Ondřej Kovář
Description: Driver classes for actuators (MOSFET-driven digital fan switch).


Changelog:
    - 2026-11-08: Initial implementaiton.
    - 2026-11-12: Added set_level() method for compatibility with level-based control.
    - 2026-11-19: Added is_active property for state checking.
    - 2026-11-23: Removing set_level() method, as it is not needed for digital actuators.
    - 2026-11-26: Added file header and documentation updates
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


    @property
    def is_active(self) -> bool:
        """Returns True if the actuator is currently running/on."""
        return self._state

    def __str__(self):
        return f"{self.name}(state={'ON' if self._state else 'OFF'})"


Fan = Actuator  # Alias for backward compatibility with legacy code