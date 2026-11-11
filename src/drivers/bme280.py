"""
MicroPython BME280 sensor driver via I2C.
Reads Temperature (°C), Relative Humidity (%), and Pressure (hPa).
"""

import time
import struct
from machine import I2C

# BME280 default I2C addresses (0x76 or 0x77)
BME280_I2C_ADDR = 0x76

class BME280:
    """
    Reusable I2C driver for Bosch Sensortec BME280 sensor.
    """

    def __init__(self, i2c: I2C, addr: int = BME280_I2C_ADDR):
        self.i2c = i2c
        self.addr = addr
        self._read_calibration()

        # Set normal mode, 16x oversampling
        self.i2c.writeto_mem(self.addr, 0xF2, b'\x01')  # hum oversampling x1
        self.i2c.writeto_mem(self.addr, 0xF4, b'\x27')  # temp x1, press x1, normal mode
        self.i2c.writeto_mem(self.addr, 0xF5, b'\xa0')  # config: 1000ms standby

        self.t_fine = 0

    def _read_calibration(self):
        calib = self.i2c.readfrom_mem(self.addr, 0x88, 26)
        self.dig_T1, self.dig_T2, self.dig_T3 = struct.unpack('<Hhh', calib[0:6])
        self.dig_P1, self.dig_P2, self.dig_P3, self.dig_P4, self.dig_P5, self.dig_P6, self.dig_P7, self.dig_P8, self.dig_P9 = struct.unpack('<Hhhhhhhhh', calib[6:24])

        self.dig_H1 = self.i2c.readfrom_mem(self.addr, 0xA1, 1)[0]
        h_calib = self.i2c.readfrom_mem(self.addr, 0xE1, 7)
        self.dig_H2 = struct.unpack('<h', h_calib[0:2])[0]
        self.dig_H3 = h_calib[2]
        self.dig_H4 = (h_calib[3] << 4) | (h_calib[4] & 0x0F)
        self.dig_H5 = (h_calib[5] << 4) | (h_calib[4] >> 4)
        self.dig_H6 = struct.unpack('<b', h_calib[6:7])[0]

    def read_raw(self):
        """Read raw ADC measurement data."""
        data = self.i2c.readfrom_mem(self.addr, 0xF7, 8)
        raw_press = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        raw_temp = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        raw_hum = (data[6] << 8) | data[7]
        return raw_temp, raw_press, raw_hum

    def read_compensated_data(self):
        """
        Reads and returns compensated (temperature in °C, pressure in hPa, humidity in %).
        """
        raw_temp, raw_press, raw_hum = self.read_raw()

        # Compensate Temperature
        var1 = (((raw_temp >> 3) - (self.dig_T1 << 1)) * self.dig_T2) >> 11
        var2 = (((((raw_temp >> 4) - self.dig_T1) * ((raw_temp >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        self.t_fine = var1 + var2
        temp = (self.t_fine * 5 + 128) >> 8
        temperature = temp / 100.0

        # Compensate Pressure
        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = ((var1 * var1 * self.dig_P3) >> 8) + ((var1 * self.dig_P2) << 12)
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33

        if var1 == 0:
            pressure = 0.0
        else:
            p = 1048576 - raw_press
            p = (((p << 31) - var2) * 3125) // var1
            var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
            var2 = (self.dig_P8 * p) >> 19
            p = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)
            pressure = (p / 256.0) / 100.0

        # Compensate Humidity
        v_x1 = self.t_fine - 76800
        v_x1 = (((((raw_hum << 14) - (self.dig_H4 << 20) - (self.dig_H5 * v_x1)) + 16384) >> 15) *
                (((((((v_x1 * self.dig_H6) >> 10) * (((v_x1 * self.dig_H3) >> 11) + 32768)) >> 10) + 2097152) *
                  self.dig_H2 + 8192) >> 14))
        v_x1 = v_x1 - (((((v_x1 >> 15) * (v_x1 >> 15)) >> 7) * self.dig_H1) >> 4)
        v_x1 = 0 if v_x1 < 0 else v_x1
        v_x1 = 419430400 if v_x1 > 419430400 else v_x1
        humidity = (v_x1 >> 12) / 1024.0

        return temperature, pressure, humidity

    @property
    def temperature(self) -> float:
        t, _, _ = self.read_compensated_data()
        return t

    @property
    def humidity(self) -> float:
        _, _, h = self.read_compensated_data()
        return h

    @property
    def pressure(self) -> float:
        _, p, _ = self.read_compensated_data()
        return p
