"""
Standalone test script for Fan and LED Strip MOSFET drivers, and RGB LED.
"""
from machine import Pin
import time
import sys

# Add src to path to import driver
sys.path.append("src")
from drivers.actuator import Actuator, RGBIndicator

PIN_FAN = 14
PIN_LIGHT = 15
PIN_RGB_R = 20
PIN_RGB_G = 21
PIN_RGB_B = 22

print("Testing Fan, Light strip, and RGB LED...")
fan = Actuator(PIN_FAN, name="Fan", use_pwm=False)
light = Actuator(PIN_LIGHT, name="LightStrip", use_pwm=True)
rgb = RGBIndicator(PIN_RGB_R, PIN_RGB_G, PIN_RGB_B)

try:
    print("1. Testing RGB LED sequences...")
    print(" - Green (OK)"); rgb.ok(); time.sleep(1)
    print(" - Yellow (Warning)"); rgb.warning(); time.sleep(1)
    print(" - Red (Alert)"); rgb.alert(); time.sleep(1)
    rgb.off()

    print("2. Testing Fan switching (3 seconds ON)...")
    fan.on()
    time.sleep(3)
    fan.off()

    print("3. Testing LED Strip PWM dimming (0% -> 100% -> 0%)...")
    for brightness in range(0, 101, 20):
        print(f" - Brightness: {brightness}%")
        light.set_level(brightness)
        time.sleep(0.5)
    light.off()

    print("\nAll actuator tests completed successfully!")
except KeyboardInterrupt:
    fan.off()
    light.off()
    rgb.off()
    print("\nTest cancelled.")
