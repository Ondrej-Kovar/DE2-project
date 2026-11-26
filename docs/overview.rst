Project Overview
================

Problem Statement
-----------------
Maintaining an optimal microclimate inside a greenhouse is essential for healthy plant growth.
Sudden temperature spikes or excessive humidity can damage crops or lead to mold and fungal infections.
Manual monitoring is time-consuming and often responds too late.

Solution Summary
----------------
The **Smart Greenhouse Monitor** is an automated microclimate control and monitoring unit based on the
**Raspberry Pi Pico W** running MicroPython. It:

1. Continuously monitors environmental conditions (temperature, humidity, atmospheric pressure) using an I2C **BME280** sensor.
2. Automatically turns on supplemental **NeoPixel WS2812B** lighting based on an **LDR** ambient light sensor.
3. Provides a local visual interface (**SH1106 OLED**) showing live measurements, thresholds, and actuator states.
4. Automatically activates an extraction fan via a MOSFET driver when temperature or humidity exceeds target thresholds.
5. Allows users to configure temperature, humidity, and light thresholds using a **KY-040 rotary encoder**.
6. Transmits telemetry data and actuator states over Wi-Fi to **ThingSpeak**.

Timing & Power Modes
--------------------
The application entry point (`main.py`) reads ``LOW_POWER_MODE`` from ``settings.py`` and selects one of two loops:

* **Full-power mode** (``main_fullpower.py``, ``LOW_POWER_MODE = False``):
  Non-blocking superloop using ``machine.idle()`` between ticks (~60–80 mA).
  Sensors are read every 1 s, the OLED refreshes every 250 ms, and telemetry uploads every 20 s.
* **Low-power mode** (``main_lowpower.py``, ``LOW_POWER_MODE = True``):
  Uses ``machine.lightsleep()`` between 250 ms display ticks while keeping SRAM, RTC, and encoder GPIO
  interrupts active (~40–55 mA average). Sensor reads and ThingSpeak uploads run every ``ACTIVE_CYCLE_INTERVAL_MS`` (default 60 s).
