"""
Low-power variant of the Smart Greenhouse System main loop.

Strategy
--------
The display + encoder UI run continuously (they are interrupt-driven or polled
at a short 250 ms tick), while the expensive "measure & upload" work happens
only once per ACTIVE_CYCLE_INTERVAL_MS (default 60 s).

Between display refreshes the CPU drops into machine.lightsleep(), which halts
the core clock and most peripherals but keeps:
  - SRAM alive (all variables preserved)
  - GPIO interrupts active (encoder still usable)
  - RTC / time counter running (ticks_ms() stays accurate after wakeup)

Power budget comparison (Pico W @ 3.3 V, rough estimates)
  Original superloop with idle()   ~ 60–80 mA
  This variant (Wi-Fi kept on)     ~ 40–55 mA average (CPU sleeping ~248 ms
                                     out of every 250 ms display tick)

Incompatibilities / caveats
  - lightsleep() can interfere with USB-serial REPL on Pico W when sleeping
    for >100 ms; fine on a standalone device, but may drop Thonny connection.
    If you debug via USB, comment out the lightsleep call and use idle() instead.

Authors: Richard Kralovsky, Ondrej Kovar, Adam Koutny

History
  26.11.2026  Created as low-power alternative to main.py.
               Measure/upload active only during ACTIVE_CYCLE_INTERVAL_MS.
               Display + encoder remain fully responsive.
               CPU uses lightsleep() between 250 ms display ticks.
"""

import time
from machine import I2C, Pin, lightsleep

import settings as config
from drivers.actuator import Fan
from drivers.bme280_sensor import BME280Sensor
from drivers.led_strip import LEDStrip
from drivers.light_sensor import LightSensor
from drivers.rotary import RotaryEncoder
from drivers.sh1106_display import OLEDDisplay
from drivers.thingspeak_upload import ThingSpeakUpload


# ---------------------------------------------------------------------------
# Low-power tuning – values come from settings.py
# ---------------------------------------------------------------------------

# How often to wake up for a full measure + upload cycle (ms).
# Keep >= UPLOAD_INTERVAL_MS (ThingSpeak free tier minimum is 15 s).
# Set ACTIVE_CYCLE_INTERVAL_MS in settings.py (default 60 s).
ACTIVE_CYCLE_INTERVAL_MS = config.ACTIVE_CYCLE_INTERVAL_MS


def main():
    """Initialize hardware peripherals and run the low-power lightsleep superloop."""
    print("Initializing Smart Greenhouse System (low-power mode)...")

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
    fan   = Fan(pin_num=config.PIN_FAN, name="GreenhouseFan", active_high=True)
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
    hum_lim  = config.DEFAULT_HUM_LIM

    menu_mode    = 0   # 0: Monitor, 1: Temp, 2: Hum, 3: Light Low, 4: Light High
    last_led_state = -1  # Force initial write on first cycle

    now = time.ticks_ms()
    last_display_time = time.ticks_add(now, -config.DISPLAY_INTERVAL_MS)

    # Trigger the first measure+upload immediately (at t=0)
    last_active_time = time.ticks_add(now, -ACTIVE_CYCLE_INTERVAL_MS)

    print("System ready. Entering low-power superloop...")
    print(f"  Display refresh : {config.DISPLAY_INTERVAL_MS} ms")
    print(f"  Measure+upload  : every {ACTIVE_CYCLE_INTERVAL_MS // 1000} s")

    try:
        while True:
            now = time.ticks_ms()

            # ----------------------------------------------------------------
            # A  Encoder Button – Menu State Machine (runs every wake-up)
            # ----------------------------------------------------------------
            if encoder.is_button_pressed():
                menu_mode = (menu_mode + 1) % 5
                if menu_mode == 1:
                    encoder.set_range(15, 40, int(temp_lim), step=config.TEMP_STEP)
                elif menu_mode == 2:
                    encoder.set_range(20, 95, int(hum_lim), step=config.HUM_STEP)
                elif menu_mode == 3:
                    encoder.set_range(0, light_sensor.light_high - 5, light_sensor.light_low, step=config.LIGHT_STEP)
                elif menu_mode == 4:
                    encoder.set_range(light_sensor.light_low + 5, 100, light_sensor.light_high, step=config.LIGHT_STEP)
                # Trigger immediate display refresh
                last_display_time = time.ticks_add(now, -config.DISPLAY_INTERVAL_MS)

            # ----------------------------------------------------------------
            # B  Apply Encoder Value to Active Threshold (runs every wake-up)
            # ----------------------------------------------------------------
            if menu_mode == 1:
                temp_lim = float(encoder.value)
            elif menu_mode == 2:
                hum_lim = float(encoder.value)
            elif menu_mode == 3:
                light_sensor.light_low = int(encoder.value)
            elif menu_mode == 4:
                light_sensor.light_high = int(encoder.value)

            # ----------------------------------------------------------------
            # C  ACTIVE CYCLE – Sensor Read, Actuators, Upload  (every 60 s)
            # ----------------------------------------------------------------
            if time.ticks_diff(now, last_active_time) >= ACTIVE_CYCLE_INTERVAL_MS:
                last_active_time = now

                # C1  Read BME280
                if bme is not None:
                    try:
                        temp, hum, pres = bme.get_readings()
                        sensor_error = False
                    except OSError as e:
                        print("BME280 read error:", e)
                        sensor_error = True

                # C2  Fan Hysteresis
                if not sensor_error:
                    if temp > temp_lim or hum > hum_lim:
                        fan.on()
                    elif temp < (temp_lim - config.TEMP_HYSTERESIS) and hum < (hum_lim - config.HUM_HYSTERESIS):
                        fan.off()
                else:
                    fan.off()

                # C3  Light Sensor & NeoPixel Hysteresis
                led_state, light_pct = light_sensor.check_light()
                if led_state != last_led_state:
                    led_strip.set_state(led_state)
                    last_led_state = led_state

                # C4  ThingSpeak Upload
                if not sensor_error:
                    uploader.upload_data(
                        temperature=temp,
                        humidity=hum,
                        pressure=pres,
                        fan_status=1 if fan.is_active else 0,
                        light_status=1 if last_led_state == 1 else 0,
                    )

            # ----------------------------------------------------------------
            # D  Periodic OLED Refresh (every DISPLAY_INTERVAL_MS = 250 ms)
            #    Runs even during sleep cycles so the UI stays responsive.
            # ----------------------------------------------------------------
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

            # ----------------------------------------------------------------
            # E  Sleep until the next display tick
            #    lightsleep() halts the CPU but keeps SRAM and RTC alive.
            #    The encoder uses GPIO interrupts internally (RotaryEncoder
            #    driver), so it will still register turns during sleep.
            # ----------------------------------------------------------------
            ms_until_next_display = config.DISPLAY_INTERVAL_MS - time.ticks_diff(
                time.ticks_ms(), last_display_time
            )
            if ms_until_next_display > 2:   # only sleep if worth it
                lightsleep(ms_until_next_display)

    except KeyboardInterrupt:
        print("\nShutting down safely...")
        fan.off()
        led_strip.set_state(0)
        display.off()
        uploader.disconnect()
        print("Shutdown complete.")


if __name__ == "__main__":
    main()
