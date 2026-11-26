"""
OLED Display Controller for Raspberry Pi Pico.
Provides a class-based wrapper for the SH1106 OLED (128x64) to format and
display environmental data, light hysteresis limits (%), and actuator states.
Based on oled_display.py from DE2 course lab6
Author: Adam Koutny

History:
2026-11-11 Initialization
2026-11-19 Tested via test_oled.py, wrong I2C input (fixed)
2026-11-19 Verified functionality via test_oled.py
2026-11-19 Verified integrated functionality in main
"""
from sh1106 import SH1106_I2C


class OLEDDisplay:
    """OLED display controller for the 128x64 SH1106 screen over I2C."""

    def __init__(self, i2c, address=0x3C):
        """Initialize the display using a shared I2C bus.

        :param i2c: Initialized MicroPython ``machine.I2C`` bus instance.
        :param address: 7-bit I2C address of the SH1106 display (default ``0x3C``).
        """
        self.i2c = i2c
        self.address = address
        self.oled = SH1106_I2C(i2c)

    def show_data(self, temp, temp_lim, hum, hum_lim, pres,
                  light_pct, light_low, light_high, fan_on, led_on,
                  menu_mode=0, sensor_error=False):
        """Render all greenhouse metrics, thresholds, and actuator states.

        :param temp: Measured temperature (°C).
        :param temp_lim: Active temperature limit (°C).
        :param hum: Measured relative humidity (% RH).
        :param hum_lim: Active humidity limit (% RH).
        :param pres: Measured atmospheric pressure (hPa).
        :param light_pct: Ambient light level (%).
        :param light_low: Lower light threshold (%).
        :param light_high: Upper light threshold (%).
        :param fan_on: ``True`` if the fan is currently ON.
        :param led_on: ``True`` if the LED strip is currently ON.
        :param menu_mode: Active menu index (``0`` = monitor, ``1..4`` = editing).
        :param sensor_error: ``True`` to show a BME280 wiring/read error banner.
        """
        self.oled.fill(0)

        # 1. Header (Menu state)
        if menu_mode == 1:
            self.oled.text("SET TEMP LIMIT", 0, 0)
        elif menu_mode == 2:
            self.oled.text("SET HUM LIMIT", 0, 0)
        elif menu_mode == 3:
            self.oled.text("SET LIGHT LOW", 0, 0)
        elif menu_mode == 4:
            self.oled.text("SET LIGHT HIGH", 0, 0)
        else:
            self.oled.text("GREENHOUSE MON", 0, 0)

        # 2. BME280 Data (Temperature, humidity, pressure)
        if sensor_error:
            self.oled.text("BME280 ERROR", 0, 18)
            self.oled.text("CHECK I2C WIRING", 0, 30)
        else:
            t_lim_str = f"{temp_lim:.1f}<" if menu_mode == 1 else f"{temp_lim:.1f}"
            h_lim_str = f"{hum_lim:.1f}<" if menu_mode == 2 else f"{hum_lim:.1f}"

            self.oled.text(f"T:{temp:.1f}/{t_lim_str}C", 0, 9)
            self.oled.text(f"H:{hum:.1f}/{h_lim_str}%", 0, 18)
            self.oled.text(f"P:{pres:.1f}hPa", 0, 27)

        # 3. Light Sensor (Relative light level in % + hysteresis limits)
        low_str = f"{int(light_low)}<" if menu_mode == 3 else f"{int(light_low)}"
        high_str = f"{int(light_high)}<" if menu_mode == 4 else f"{int(light_high)}"

        self.oled.text(f"L:{int(light_pct)}%({low_str}-{high_str})", 0, 36)

        # 4. Actuator states
        fan_str = "ON" if fan_on else "OFF"
        led_str = "ON" if led_on else "OFF"
        self.oled.text(f"FAN:{fan_str} LED:{led_str}", 0, 45)

        # 5. Footer (Overall system status)
        status = "BME ERROR" if sensor_error else "SYS OK"
        self.oled.text(status, 0, 54)

        self.oled.show()

    def off(self):
        """Clears the screen safely."""
        self.oled.fill(0)
        self.oled.show()