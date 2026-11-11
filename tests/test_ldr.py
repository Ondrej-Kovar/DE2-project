"""
Standalone test script for LDR (photoresistor) analog sensor on ADC0 (GP26).
"""
from machine import Pin, ADC
import time

PIN_LDR_ADC = 26
ldr = ADC(Pin(PIN_LDR_ADC))

print("Testing Photoresistor (LDR) on ADC0 (GP26)...")
print("Cover and illuminate the sensor to observe changes. Press Ctrl+C to stop.")

try:
    while True:
        raw_val = ldr.read_u16()             # 0 to 65535
        voltage = (raw_val / 65535.0) * 3.3  # Volts (approx)
        print(f"LDR Raw ADC: {raw_val:5d} | Voltage: {voltage:.2f} V")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nTest finished.")
