"""
Standalone I2C Bus Scanner test script for Raspberry Pi Pico W.
Scans for devices like BME280 (0x76 or 0x77) and OLED SH1106 (0x3C).
"""
from machine import Pin, I2C
import time

I2C_ID = 0
PIN_SDA = 0
PIN_SCL = 1

print("Initializing I2C bus...")
i2c = I2C(I2C_ID, sda=Pin(PIN_SDA), scl=Pin(PIN_SCL), freq=400_000)

print(f"Scanning I2C bus (SDA=GP{PIN_SDA}, SCL=GP{PIN_SCL})...")
devices = i2c.scan()

if devices:
    print(f"Found {len(devices)} device(s):")
    for d in devices:
        hex_addr = hex(d)
        desc = ""
        if d in (0x76, 0x77):
            desc = "(likely BME280 sensor)"
        elif d in (0x3C, 0x3D):
            desc = "(likely SH1106 / SSD1306 OLED display)"
        print(f"  - Decimal: {d:3d} | Hex: {hex_addr} {desc}")
else:
    print("No I2C devices found! Check your wiring, pull-ups, and 3.3V power.")
