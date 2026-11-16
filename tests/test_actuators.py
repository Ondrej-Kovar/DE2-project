"""
Standalone test script for Fan MOSFET driver.
"""
from machine import Pin
import time
import sys

# Add src to path to import driver
sys.path.append("src")
from drivers.actuator import Actuator

PIN_FAN = 15

print("Testing Fan driver...")
fan = Actuator(PIN_FAN, name="Fan")

try:
    print("Testing Fan switching (3 seconds ON)...")
    fan.on()
    time.sleep(3)
    
    print("Turning Fan OFF...")
    fan.off()

    print("\nFan actuator test completed successfully!")
    
except KeyboardInterrupt:
    fan.off()
    print("\nTest cancelled.")