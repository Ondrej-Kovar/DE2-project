"""
Standalone test script for Fan MOSFET driver and RGB status LED.
Compatible with Raspberry Pi Pico / Pico W (MicroPython).
"""
import time
import sys

# Ensure driver modules can be found
for path in ("src", "src/drivers", "."):
    if path not in sys.path:
        sys.path.append(path)

from drivers.actuator import Actuator, RGBIndicator

# Pin assignment (matches config.py)
PIN_FAN = 14
PIN_RGB_R = 20
PIN_RGB_G = 21
PIN_RGB_B = 22

print("=== Starting Fan Driver and RGB LED Test ===")
fan = Actuator(PIN_FAN, name="Fan_12V")
rgb = RGBIndicator(PIN_RGB_R, PIN_RGB_G, PIN_RGB_B)

try:
    print("\n1. Testing RGB LED sequences...")
    print(" - Green (OK)...")
    rgb.ok()
    time.sleep(1)

    print(" - Yellow/Orange (Warning)...")
    rgb.warning()
    time.sleep(1)

    print(" - Red (Alert)...")
    rgb.alert()
    time.sleep(1)

    print(" - Blue (Connecting)...")
    rgb.connecting()
    time.sleep(1)

    rgb.off()
    print(" - RGB LED turned OFF.")

    print("\n2. Testing Fan digital switching...")
    print(f" Initial state: {fan}")

    print(" - Switching Fan ON for 3 seconds...")
    fan.on()
    print(f" State: {fan} (is_active={fan.is_active})")
    time.sleep(3)

    print(" - Switching Fan OFF...")
    fan.off()
    print(f" State: {fan} (is_active={fan.is_active})")
    time.sleep(1)

    print(" - Testing toggle ON (1.5 seconds)...")
    fan.toggle()
    print(f" State: {fan} (is_active={fan.is_active})")
    time.sleep(1.5)

    print(" - Testing toggle OFF...")
    fan.toggle()
    print(f" State: {fan} (is_active={fan.is_active})")

    print("\n=== All actuator tests completed successfully! ===")

except KeyboardInterrupt:
    print("\nTest interrupted by user.")
finally:
    # Ensure safe shutdown of all outputs
    fan.off()
    rgb.off()
    print("All outputs safely turned OFF.")
