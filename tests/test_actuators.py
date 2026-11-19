"""
Standalone test script for Fan MOSFET driver.
Compatible with Raspberry Pi Pico / Pico W (MicroPython).
"""
import time
import sys

# Ensure driver modules can be found
for path in ("src", "src/drivers", "."):
    if path not in sys.path:
        sys.path.append(path)

from drivers.actuator import Actuator

# Pin assignment (matches config.py)
PIN_FAN = 15

print("=== Starting Fan Driver ===")
fan = Actuator(PIN_FAN, name="Fan_12V")

try:
    print("\n1. Testing Fan digital switching...")
    print(f" Initial state: {fan}")

    print(" - Switching Fan ON for 3 seconds...")
    fan.on()
    print(f" State: {fan} (is_active={fan.is_active})")
    time.sleep(3)

    print(" - Switching Fan OFF...")
    fan.off()
    print(f" State: {fan} (is_active={fan.is_active})")
    time.sleep(3)

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
    print("All outputs safely turned OFF.")
