"""
Main application for Smart Greenhouse Monitor.
Runs cooperative concurrent tasks using MicroPython uasyncio.
Platform: Raspberry Pi Pico W
"""

import uasyncio as asyncio
from machine import Pin, I2C, ADC
import time

import config
from drivers import BME280, SH1106_I2C, RotaryEncoder, Actuator, RGBIndicator

# ==============================================================================
# Shared Application State
# ==============================================================================
class GreenhouseState:
    def __init__(self):
        # Sensor measurements
        self.temperature = 22.0
        self.humidity = 50.0
        self.pressure = 1013.25
        self.light_level_raw = 30000

        # User setpoints / Thresholds
        self.temp_threshold = config.DEFAULT_TEMP_THRESHOLD
        self.hum_threshold = config.DEFAULT_HUM_THRESHOLD

        # Actuator states
        self.fan_active = False
        self.light_active = False

        # System status
        self.sensor_error = False
        self.menu_mode = 0  # 0: View status, 1: Edit Temp Threshold, 2: Edit Hum Threshold


# Instantiate global state
state = GreenhouseState()

# ==============================================================================
# Hardware Initialization
# ==============================================================================
print("Initializing I2C bus...")
i2c = I2C(config.I2C_ID, sda=Pin(config.PIN_SDA), scl=Pin(config.PIN_SCL), freq=config.I2C_FREQ)

print("Initializing Sensors & Actuators...")
# BME280 Sensor
bme = None
try:
    bme = BME280(i2c, addr=0x76)
    print("BME280 initialized successfully.")
except Exception as e:
    print(f"Warning: BME280 initialization failed: {e}")
    state.sensor_error = True

# OLED Display SH1106
oled = None
try:
    oled = SH1106_I2C(width=128, height=64, i2c=i2c, addr=0x3C)
    print("SH1106 OLED initialized successfully.")
except Exception as e:
    print(f"Warning: OLED initialization failed: {e}")

# Photoresistor (LDR) ADC
ldr_adc = ADC(Pin(config.PIN_LDR_ADC))

# Actuators
fan = Actuator(config.PIN_FAN, name="Fan_12V")
light_strip = Actuator(config.PIN_LIGHT, name="Grow_LED", use_pwm=True)
rgb = RGBIndicator(config.PIN_RGB_R, config.PIN_RGB_G, config.PIN_RGB_B)

# Rotary Encoder
encoder = RotaryEncoder(config.PIN_ENC_CLK, config.PIN_ENC_DT, config.PIN_ENC_SW, min_val=15, max_val=40, step=1)
encoder.value = int(state.temp_threshold)

# ==============================================================================
# Async Tasks
# ==============================================================================

async def task_inputs():
    """High frequency task: handles encoder rotation and push button debounce."""
    while True:
        # Check if button was clicked to cycle menus
        if encoder.is_button_pressed():
            state.menu_mode = (state.menu_mode + 1) % 3
            if state.menu_mode == 1:
                encoder.set_range(15, 45, int(state.temp_threshold), step=1)
            elif state.menu_mode == 2:
                encoder.set_range(30, 95, int(state.hum_threshold), step=5)

        # Update setpoint value depending on active menu
        if state.menu_mode == 1:
            state.temp_threshold = float(encoder.value)
        elif state.menu_mode == 2:
            state.hum_threshold = float(encoder.value)

        await asyncio.sleep_ms(25)


async def task_sensors():
    """Medium frequency task: reads BME280 and LDR sensor."""
    while True:
        try:
            if bme:
                t, p, h = bme.read_compensated_data()
                state.temperature = t
                state.pressure = p
                state.humidity = h
                state.sensor_error = False
        except Exception as e:
            print(f"Sensor read error: {e}")
            state.sensor_error = True

        # Read ambient light level (16-bit unsigned integer: 0 to 65535)
        state.light_level_raw = ldr_adc.read_u16()

        await asyncio.sleep_ms(500)


async def task_control():
    """Control logic: evaluates thresholds with hysteresis and updates outputs."""
    while True:
        # 1. Climate / Fan Regulation with Hysteresis
        turn_on_temp = state.temp_threshold
        turn_off_temp = state.temp_threshold - config.TEMP_HYSTERESIS

        if state.temperature >= turn_on_temp or state.humidity >= state.hum_threshold:
            fan.on()
            state.fan_active = True
        elif state.temperature < turn_off_temp and state.humidity < (state.hum_threshold - 5.0):
            fan.off()
            state.fan_active = False

        # 2. Lighting Regulation (LDR threshold)
        if state.light_level_raw < config.LIGHT_THRESHOLD_ADC:
            light_strip.set_level(100.0)
            state.light_active = True
        else:
            light_strip.set_level(0.0)
            state.light_active = False

        # 3. Status RGB Indicator
        if state.sensor_error:
            rgb.alert()
        elif state.fan_active or state.light_active:
            rgb.warning()
        else:
            rgb.ok()

        await asyncio.sleep_ms(500)


async def task_display():
    """Display task: renders live data and user menu onto OLED."""
    while True:
        if oled:
            oled.fill(0)

            # Header / Status bar
            if state.menu_mode == 0:
                oled.text("GREENHOUSE MON", 0, 0)
            elif state.menu_mode == 1:
                oled.text("SET TEMP LIMIT", 0, 0)
            elif state.menu_mode == 2:
                oled.text("SET HUM LIMIT", 0, 0)

            oled.hline(0, 10, 128, 1)

            # Live Measurements
            oled.text(f"Temp: {state.temperature:4.1f} C", 0, 15)
            oled.text(f"Humi: {state.humidity:4.1f} %", 0, 27)
            oled.text(f"Light: {state.light_level_raw:5d}", 0, 39)

            # Setpoints & Actuators
            fan_str = "ON" if state.fan_active else "OFF"
            light_str = "ON" if state.light_active else "OFF"
            oled.text(f"F:{fan_str}  L:{light_str}", 0, 52)

            # Active setpoint indicator
            if state.menu_mode == 1:
                oled.text(f"[*T:{int(state.temp_threshold)}C]", 68, 52)
            elif state.menu_mode == 2:
                oled.text(f"[*H:{int(state.hum_threshold)}%]", 68, 52)

            oled.show()

        await asyncio.sleep_ms(200)


async def task_telemetry():
    """Telemetry task: periodic telemetry reporting over Wi-Fi / MQTT."""
    while True:
        # Example telemetry output to serial console (and Wi-Fi/MQTT when configured)
        print(f"[Telemetry] Temp={state.temperature:.1f}C, Hum={state.humidity:.1f}%, "
              f"Light={state.light_level_raw}, Fan={state.fan_active}, LightStrip={state.light_active}")
        await asyncio.sleep_ms(15000)


# ==============================================================================
# Application Entry Point
# ==============================================================================
async def main():
    print("Starting Smart Greenhouse concurrent loop...")
    await asyncio.gather(
        task_inputs(),
        task_sensors(),
        task_control(),
        task_display(),
        task_telemetry(),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user. Turning off actuators.")
        fan.off()
        light_strip.off()
        rgb.off()
