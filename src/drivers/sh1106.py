"""
OLED Display Controller for Raspberry Pi Pico.
Provides a class-based wrapper for the SH1106 OLED (128x64) to format and 
display environmental data, light hysteresis limits, and actuator states.
"""
from sh1106 import SH1106_I2C

class OLEDDisplay:
    def __init__(self, i2c, address=0x3C):
        """Initialize the display using a shared I2C bus."""
        self.i2c = i2c
        self.address = address
        self.oled = SH1106_I2C(128, 64, self.i2c, addr=self.address)

    def show_data(self, temp, temp_lim, hum, hum_lim, pres, 
                  light_v, v_low, v_high, fan_on, led_on, 
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
            # Add dynamic cursor '<' if currently editing the limit
            t_lim_str = f"{temp_lim:.1f}<" if menu_mode == 1 else f"{temp_lim:.1f}"
            h_lim_str = f"{hum_lim:.1f}<" if menu_mode == 2 else f"{hum_lim:.1f}"
            
            self.oled.text(f"T:{temp:.1f}/{t_lim_str}C", 0, 9)
            self.oled.text(f"H:{hum:.1f}/{h_lim_str}%", 0, 18)
            self.oled.text(f"P:{pres:.1f}hPa", 0, 27)

        # 3. Light Sensor (Current V + V_low and V_high with dynamic cursor)
        v_low_str = f"{v_low:.1f}<" if menu_mode == 3 else f"{v_low:.1f}"
        v_high_str = f"{v_high:.1f}<" if menu_mode == 4 else f"{v_high:.1f}"
        
        # Max length is exactly 16 characters e.g., "L:1.2V(0.5<-1.0)"
        self.oled.text(f"L:{light_v:.1f}V({v_low_str}-{v_high_str})", 0, 36)
        
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