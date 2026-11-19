"""
Configuration parameters, pin assignments, and default thresholds
for the Smart Greenhouse Monitoring & Control System.
"""

# Wi-Fi & ThingSpeak
# MUST BE CONFIGURED BEFORE IPLEMENTATION
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
THINGSPEAK_API_KEY = "YOUR_TS_API_KEY"

# Pinout (Raspberry Pi Pico W)
PIN_I2C_SDA = 4
PIN_I2C_SCL = 5
I2C_FREQ = 100_000

PIN_ENC_CLK = 2
PIN_ENC_DT = 3
PIN_ENC_SW = 12

PIN_LED_STRIP = 14
NUM_LEDS = 50

PIN_FAN = 15
PIN_LDR = 26

# Default Thresholds & Hysteresis
DEFAULT_TEMP_LIM = 25.0   # °C
DEFAULT_HUM_LIM = 60.0    # % RH
TEMP_HYSTERESIS = 1.0     # °C (Fan OFF below T_lim - 1.0)
HUM_HYSTERESIS = 5.0      # % RH (Fan OFF below RH_lim - 5.0)
LIGHT_STEP = 5               # % (for rotary encoder adjustment)
TEMP_STEP = 1                # °C (for rotary encoder adjustment)
HUM_STEP = 5                 # % RH (for rotary encoder adjustment)

DEFAULT_LIGHT_LOW = 15    # % (LED ON below this)
DEFAULT_LIGHT_HIGH = 30   # % (LED OFF above this)

# Non-blocking Superloop Intervals (ms)
SENSOR_INTERVAL_MS = 1000     # Read sensors & update actuators every 1 s
DISPLAY_INTERVAL_MS = 250     # Refresh OLED every 250 ms (snappy encoder UI)
UPLOAD_INTERVAL_MS = 20_000   # ThingSpeak upload every 20 s (free tier min is 15 s)