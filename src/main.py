"""
Main application entry point for the Smart Greenhouse System (DE2 Project).
Runs a non-blocking superloop integrating BME280, LDR, SH1106 OLED,
KY-040 rotary encoder, MOSFET fan, NeoPixel LED strip, and ThingSpeak telemetry.
"""
import time
from machine import I2C, Pin

import settings as config
from drivers.actuator import Fan
from drivers.bme280_sensor import BME280Sensor
from drivers.led_strip import LEDStrip
from drivers.light_sensor import LightSensor
from drivers.rotary import RotaryEncoder
from drivers.sh1106_display import OLEDDisplay
from drivers.thingspeak_upload import ThingSpeakUpload


def main():
    print("Initializing Smart Greenhouse System...")

    # 1. Shared I2C Bus (BME280 + SH1106 OLED)
    i2c = I2C(0, sda=Pin(config.PIN_I2C_SDA), scl=Pin(config.PIN_I2C_SCL), freq=config.I2C_FREQ)

    # 2. Initialize Display
    display = OLEDDisplay(i2c, address=0x3C)

    # 3. Initialize BME280 (graceful fallback if disconnected at boot)
    bme = None
    sensor_error = False
    try:
        bme = BME280Sensor(i2c, address=0x76)
    except OSError as e:
        print("BME280 init error:", e)
        sensor_error = True

    # 4. Initialize Light Sensor, Actuators, Encoder & Cloud Uploader
    light_sensor = LightSensor(
        pin=config.PIN_LDR,
        light_low=config.DEFAULT_LIGHT_LOW,
        light_high=config.DEFAULT_LIGHT_HIGH,
    )
    fan = Fan(pin_num=config.PIN_FAN, name="GreenhouseFan", active_high=True)
    led_strip = LEDStrip(pin=config.PIN_LED_STRIP, num_leds=config.NUM_LEDS)
    encoder = RotaryEncoder(
        clk_pin=config.PIN_ENC_CLK,
        dt_pin=config.PIN_ENC_DT,
        sw_pin=config.PIN_ENC_SW,
    )
    uploader = ThingSpeakUpload(
        api_key=config.THINGSPEAK_API_KEY,
        ssid=config.WIFI_SSID,
        password=config.WIFI_PASSWORD,
    )

    # 5. Runtime State Variables
    temp, hum, pres = 0.0, 0.0, 0.0
    light_pct = 0

    temp_lim = config.DEFAULT_TEMP_LIM
    hum_lim = config.DEFAULT_HUM_LIM

    menu_mode = 0  # 0: Monitor, 1: Temp, 2: Hum, 3: Light Low, 4: Light High
    last_led_state = -1  # Force initial write on first cycle

    now = time.ticks_ms()
    last_sensor_time = time.ticks_add(now, -config.SENSOR_INTERVAL_MS)
    last_display_time = time.ticks_add(now, -config.DISPLAY_INTERVAL_MS)
    last_upload_time = now

    print("System ready. Entering main superloop...")

    try:
        while True:
            now = time.ticks_ms()

            # 1 Encoder Button Handling (Menu State Machine) - threshold control + forced OLED refresh
            if encoder.is_button_pressed():
                menu_mode = (menu_mode + 1) % 5
                if menu_mode == 1:
                    encoder.set_range(15, 40, int(temp_lim), step=1) #set_range(self, min_val: int, max_val: int, current_val: int = None, step: int = 1):
                elif menu_mode == 2:
                    encoder.set_range(20, 95, int(hum_lim), step=1)
                elif menu_mode == 3:
                    encoder.set_range(0, light_sensor.light_high - 5, light_sensor.light_low, step=5) 
                elif menu_mode == 4:
                    encoder.set_range(light_sensor.light_low + 5, 100, light_sensor.light_high, step=5)
                # Trigger immediate display refresh
                last_display_time = time.ticks_add(now, -config.DISPLAY_INTERVAL_MS)

            # 2 Apply Encoder Value to Active Threshold
            if menu_mode == 1:
                temp_lim = float(encoder.value)
            elif menu_mode == 2:
                hum_lim = float(encoder.value)
            elif menu_mode == 3:
                light_sensor.light_low = int(encoder.value)
            elif menu_mode == 4:
                light_sensor.light_high = int(encoder.value)

            # 3 Periodic Sensor Read & Hysteresis Control (1 s)
            if time.ticks_diff(now, last_sensor_time) >= config.SENSOR_INTERVAL_MS:
                last_sensor_time = now

                # Read BME280
                if bme is not None:
                    try:
                        temp, hum, pres = bme.get_readings()
                        sensor_error = False
                    except OSError as e:
                        print("BME280 read error:", e)
                        sensor_error = True

                # Fan Hysteresis: ON if T > T_lim OR RH > RH_lim; OFF if both below hysteresis
                if not sensor_error:
                    if temp > temp_lim or hum > hum_lim:
                        fan.on()
                    elif temp < (temp_lim - config.TEMP_HYSTERESIS) and hum < (hum_lim - config.HUM_HYSTERESIS):
                        fan.off()
                else:
                    fan.off()

                # Light Sensor & NeoPixel Hysteresis
                led_state, light_pct = light_sensor.check_light()
                if led_state != last_led_state:
                    led_strip.set_state(led_state)
                    last_led_state = led_state

            # 4 Periodic OLED Refresh (250 ms)
            if time.ticks_diff(now, last_display_time) >= config.DISPLAY_INTERVAL_MS:
                last_display_time = now
                display.show_data(
                    temp=temp,
                    temp_lim=temp_lim,
                    hum=hum,
                    hum_lim=hum_lim,
                    pres=pres,
                    light_pct=light_pct,
                    light_low=light_sensor.light_low,
                    light_high=light_sensor.light_high,
                    fan_on=fan.is_active,
                    led_on=(last_led_state == 1),
                    menu_mode=menu_mode,
                    sensor_error=sensor_error,
                )

            # 5 Periodic ThingSpeak Cloud Telemetry (20 s)
            if time.ticks_diff(now, last_upload_time) >= config.UPLOAD_INTERVAL_MS:
                last_upload_time = now
                if not sensor_error:
                    uploader.upload_data(
                        temperature=temp,
                        humidity=hum,
                        pressure=pres,
                        fan_status=1 if fan.is_active else 0,
                        light_status=1 if last_led_state == 1 else 0,
                    )

            time.sleep_ms(10) #Yield briefly (lab4)

    except KeyboardInterrupt:
        print("\nShutting down safely...")
        fan.off()
        led_strip.set_state(0)
        display.off()
        uploader.disconnect()
        print("Shutdown complete.")


if __name__ == "__main__":
    main()