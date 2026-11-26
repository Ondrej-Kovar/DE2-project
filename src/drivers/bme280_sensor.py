"""
BME280 environment sensor controller for Raspberry Pi Pico.
Provides a class-based wrapper to initialize the sensor on a shared I2C bus,
verifies hardware connection, and retrieves formatted readings.
Based on bme280_read.py from LAB6 DE2 course
Author: Adam Koutný
History:
2026-11-10 Initialization
2026-11-19 Verified functionality using test_bme280.py
2026-11-19 Verified integrated functionality in main
2026-11-20 Added docstrings for Sphinx documentation
"""
from bme280 import BME280
from machine import I2C, Pin
import time

class BME280Sensor:
    """Wrapper for the BME280 temperature, humidity, and pressure sensor over I2C."""

    def __init__(self, i2c, address=0x76):
        """Initialize the BME280 sensor and verify its presence on the I2C bus.

        :param i2c: Initialized MicroPython ``machine.I2C`` bus instance.
        :param address: 7-bit I2C address of the BME280 sensor (default ``0x76``).
        :raises OSError: If the sensor is not detected at the specified address.
        """
        self.i2c = i2c
        self.address = address
        
        # Verify the sensor is connected to the I2C bus
        if self.address not in self.i2c.scan():
            raise OSError(f"BME280 at {self.address:#04x} was not detected. Check wiring.")
        
        self.sensor = BME280(self.i2c, addr=self.address)

    def get_readings(self):
        """Read current environmental measurements from the sensor.

        :return: Tuple ``(temperature, humidity, pressure)`` in °C, % RH, and hPa.
        """
        # The underlying library returns 4 values, we discard the 4th (unused)
        temperature, humidity, pressure, _ = self.sensor.read_values()
        return temperature, humidity, pressure