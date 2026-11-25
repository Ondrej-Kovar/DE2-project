"""
BME280 environment sensor controller for Raspberry Pi Pico.
Provides a class-based wrapper to initialize the sensor on a shared I2C bus,
verifies hardware connection, and retrieves formatted readings.
Based on bme280_read.py from LAB6 DE2 course
Author: Adam Koutný
History:
2026-11-10 Initialization
2026-11-19 Verified functionality using test_bme280.py
"""
from bme280 import BME280
from machine import I2C, Pin
import time

class BME280Sensor:
    def __init__(self, i2c, address=0x76):
        self.i2c = i2c
        self.address = address
        
        # Verify the sensor is connected to the I2C bus
        if self.address not in self.i2c.scan():
            raise OSError(f"BME280 at {self.address:#04x} was not detected. Check wiring.")
        
        self.sensor = BME280(self.i2c, addr=self.address)

    def get_readings(self):
        """
        Reads the sensor and returns a tuple of floats: 
        (temperature, humidity, pressure)
        """
        # The underlying library returns 4 values, we discard the 4th (unused)
        temperature, humidity, pressure, _ = self.sensor.read_values()
        return temperature, humidity, pressure