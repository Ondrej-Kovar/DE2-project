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
    def __init__(self, i2c, address=0x3C):
        """Initialize the display using a shared I2C bus."""
        self.i2c = i2c
        self.address = address
        self.oled = SH1106_I2C(i2c)

    def show_data(self, temp, temp_lim, hum, hum_lim, pres,
                  light_pct, light_low, light_high, fan_on, led_on,
                  menu_mode=0, sensor_error=False):
        """Render all greenhouse metrics, thresholds, and actuator states."""
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

            self.oled.text(f"T:{temp:.1f}/{t_lim_str}C", 0, 10)
            self.oled.text(f"H:{hum:.1f}/{h_lim_str}%", 0, 20)
            self.oled.text(f"P:{pres:.1f}hPa", 0, 30)

        # 3. Light Sensor (Relative light level in % + hysteresis limits)
        low_str = f"{int(light_low)}<" if menu_mode == 3 else f"{int(light_low)}"
        high_str = f"{int(light_high)}<" if menu_mode == 4 else f"{int(light_high)}"

        self.oled.text(f"L:{int(light_pct)}%({low_str}-{high_str})", 0, 40)

        # 4. Actuator states
        fan_str = "ON" if fan_on else "OFF"
        led_str = "ON" if led_on else "OFF"
        self.oled.text(f"FAN:{fan_str} LED:{led_str}", 0, 50)

        # 5. Footer (Overall system status)
        status = "BME ERROR" if sensor_error else "SYS OK"
        self.oled.text(status, 0, 60)

        self.oled.show()

    def off(self):
        """Clears the screen safely."""
        self.oled.fill(0)
        self.oled.show()