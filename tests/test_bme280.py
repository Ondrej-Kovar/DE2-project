"""
Quick standalone testing code for bme280.py module
Assuming standard wiring: SDA on GP4, SCL on GP5
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

if __name__ == "__main__":

    i2c_bus = I2C(0, sda=Pin(4), scl=Pin(5), freq=100_000)
    
    try:
        bme = BME280Sensor(i2c_bus)
        print("Reading BME280; press Ctrl+C to stop.")
        
        while True:
            temp, hum, pres = bme.get_readings()
            print(f"Temperature: {temp:.1f} C | Humidity: {hum:.1f} % | Pressure: {pres:.1f} hPa")
            time.sleep(2)
            
    except OSError as e:
        print(f"Hardware error: {e}")
    except KeyboardInterrupt:
        print("\nTest cancelled.")