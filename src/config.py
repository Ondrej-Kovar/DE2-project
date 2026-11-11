"""
Hardware configuration and default settings for Smart Greenhouse Monitor.
Platform: Raspberry Pi Pico W (MicroPython)
"""

# ==============================================================================
# I2C Bus Configuration (Shared by BME280 and SH1106 OLED)
# ==============================================================================
I2C_ID = 0
PIN_SDA = 0
PIN_SCL = 1
I2C_FREQ = 400_000

# ==============================================================================
# Actuator Outputs (MOSFET Drivers via PWM / Digital GPIO)
# ==============================================================================
PIN_FAN = 14        # Switched 12V DC ventilation fan
PIN_LIGHT = 15      # Switched 5V DC grow / white LED strip

# ==============================================================================
# Input Controls (KY-040 Rotary Encoder)
# ==============================================================================
PIN_ENC_CLK = 16    # Encoder Clock / Channel A
PIN_ENC_DT = 17     # Encoder Data / Channel B
PIN_ENC_SW = 18     # Push button switch

# ==============================================================================
# Status Indicator (RGB LED)
# ==============================================================================
PIN_RGB_R = 20      # Red channel (via ~220 Ohm resistor)
PIN_RGB_G = 21      # Green channel (via ~330 Ohm resistor)
PIN_RGB_B = 22      # Blue channel (via ~330 Ohm resistor)

# ==============================================================================
# Analog Inputs (ADC)
# ==============================================================================
PIN_LDR_ADC = 26    # ADC0 (GP26) for photoresistor voltage divider

# ==============================================================================
# Default Thresholds & Control Parameters
# ==============================================================================
DEFAULT_TEMP_THRESHOLD = 26.0    # °C (Activate fan if temperature exceeds setpoint)
TEMP_HYSTERESIS = 1.5           # °C (Deactivate fan when T < setpoint - hysteresis)
DEFAULT_HUM_THRESHOLD = 75.0     # %RH (Activate fan if humidity is too high)

# Ambient light threshold for grow light activation (ADC raw 16-bit range: 0 - 65535)
# Set according to your LDR resistor divider configuration:
LIGHT_THRESHOLD_ADC = 20_000

# ==============================================================================
# Telemetry & Wi-Fi Settings (Do NOT commit sensitive passwords to public repo)
# ==============================================================================
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_TELEMETRY = "vut/de2/greenhouse/telemetry"
