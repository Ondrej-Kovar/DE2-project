"""
Standalone test script for KY-040 Rotary Encoder and push button.
Platform: Raspberry Pi Pico W (MicroPython)

Verifies:
1. Clockwise (CW) and Counter-Clockwise (CCW) rotation detection.
2. Boundary limits (min_val and max_val clamping).
3. Push button detection with software debouncing.
4. Dynamic range and step switching using set_range().
"""
from machine import Pin
import time
import sys

# Ensure drivers and config can be imported from src
sys.path.append("src")
try:
    import settings
    PIN_CLK = settings.PIN_ENC_CLK
    PIN_DT = settings.PIN_ENC_DT
    PIN_SW = settings.PIN_ENC_SW
except (ImportError, AttributeError):
    # Default fallbacks if config is not available on path
    PIN_CLK = 16
    PIN_DT = 17
    PIN_SW = 18

try:
    from drivers import RotaryEncoder
except ImportError:
    from drivers.rotary import RotaryEncoder

print("=" * 60)
print("TEST: KY-040 Rotary Encoder & Push Button")
print(f"Pins: CLK=GP{PIN_CLK}, DT=GP{PIN_DT}, SW=GP{PIN_SW}")
print("=" * 60)
print("How to test:")
print(" 1. Rotate clockwise (CW)         -> Value increases (+step)")
print(" 2. Rotate counter-clockwise (CCW) -> Value decreases (-step)")
print(" 3. Hit the minimum or maximum    -> Value stops at limits")
print(" 4. Press the rotary button (SW)  -> Cycles test mode & range")
print(" Press Ctrl+C to terminate.")
print("-" * 60)

# Test modes for verifying set_range()
MODES = [
    {"name": "Temperature Range", "min": 15, "max": 45, "step": 1, "start": 25, "unit": "°C"},
    {"name": "Humidity Range",    "min": 30, "max": 95, "step": 5, "start": 60, "unit": "%RH"},
    {"name": "Narrow Range",      "min": 0,  "max": 5,  "step": 1, "start": 2,  "unit": "steps"},
]
current_mode_idx = 0
mode = MODES[current_mode_idx]

encoder = RotaryEncoder(
    clk_pin=PIN_CLK,
    dt_pin=PIN_DT,
    sw_pin=PIN_SW,
    min_val=mode["min"],
    max_val=mode["max"],
    step=mode["step"]
)
encoder.value = mode["start"]

last_value = encoder.value
click_count = 0

print(f"Initial Mode: {mode['name']} | Limits: [{mode['min']} .. {mode['max']} {mode['unit']}], Step: {mode['step']}, Value: {last_value}")

try:
    while True:
        # 1. Test button click with debouncing
        if encoder.is_button_pressed():
            click_count += 1
            current_mode_idx = (current_mode_idx + 1) % len(MODES)
            mode = MODES[current_mode_idx]
            encoder.set_range(
                min_val=mode["min"],
                max_val=mode["max"],
                current_val=mode["start"],
                step=mode["step"]
            )
            last_value = encoder.value
            print(f"\n>>> [BUTTON CLICK #{click_count}] Switched to: {mode['name']}")
            print(f"    Limits: [{mode['min']} .. {mode['max']} {mode['unit']}], Step: {mode['step']}, Value: {last_value}\n")

        # 2. Test rotation detection and limits
        if encoder.value != last_value:
            direction = "CW  (+)" if encoder.value > last_value else "CCW (-)"
            at_limit = ""
            if encoder.value == encoder._max_val:
                at_limit = " [MAX LIMIT REACHED]"
            elif encoder.value == encoder._min_val:
                at_limit = " [MIN LIMIT REACHED]"

            print(f"Rotated {direction} -> Current Value: {encoder.value} {mode['unit']}{at_limit}")
            last_value = encoder.value

        time.sleep_ms(20)

except KeyboardInterrupt:
    print("\nTest terminated by user.")
