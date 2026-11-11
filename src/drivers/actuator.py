"""
Driver classes for actuators (MOSFET-driven fan and LED strip) and RGB indicator.
Compatible with Raspberry Pi Pico (MicroPython).
"""

from machine import Pin, PWM

class Actuator:
    """
    Reusable abstraction for digital or PWM-controlled power actuators
    (such as a MOSFET-driven fan or LED strip).
    """

    def __init__(self, pin_num: int, name: str = "Actuator", use_pwm: bool = False, pwm_freq: int = 1000):
        self.name = name
        self.use_pwm = use_pwm
        self._state = False

        if self.use_pwm:
            self._pwm = PWM(Pin(pin_num))
            self._pwm.freq(pwm_freq)
            self._pwm.duty_u16(0)
        else:
            self._pin = Pin(pin_num, Pin.OUT)
            self._pin.value(0)

    def on(self):
        """Turn actuator fully ON."""
        self._state = True
        if self.use_pwm:
            self._pwm.duty_u16(65535)
        else:
            self._pin.value(1)

    def off(self):
        """Turn actuator OFF."""
        self._state = False
        if self.use_pwm:
            self._pwm.duty_u16(0)
        else:
            self._pin.value(0)

    def toggle(self):
        """Toggle current state."""
        if self._state:
            self.off()
        else:
            self.on()

    def set_level(self, percent: float):
        """
        Set PWM duty level in percentage (0.0 to 100.0 %).
        Automatically switches actuator state.
        """
        if not self.use_pwm:
            if percent > 0:
                self.on()
            else:
                self.off()
            return

        percent = max(0.0, min(100.0, percent))
        duty = int((percent / 100.0) * 65535)
        self._pwm.duty_u16(duty)
        self._state = percent > 0

    @property
    def is_active(self) -> bool:
        """Returns True if the actuator is currently running/on."""
        return self._state

    def __str__(self):
        return f"{self.name}(state={'ON' if self._state else 'OFF'})"


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
