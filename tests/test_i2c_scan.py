"""
Standalone I2C scann test script for Raspberry Pi Pico W.
Scans for devices like BME280 (0x76 or 0x77) and OLED SH1106 (0x3C).
Imported from DE2 LAB6 i2c_scan.py
"""
from machine import I2C, Pin


def main():
    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100_000)

    print("Scanning I2C...", end="")
    addresses = i2c.scan()
    print(f"{len(addresses)} device(s) detected")

    for address in addresses:
        print(f"Decimal: {address:3d}  Hex: {address:#04x}")


if __name__ == "__main__":
    main()
