"""
ThingSpeak IoT Telemetry Module

This module provides the `ThingSpeakUpload` class for sending smart greenhouse 
data to the cloud. It uploads BME280 sensor readings and current statuses of 
actuators (fan, light). It also ensures the Wi-Fi connection is active before 
attempting any data transfer.

Based on the 'bme280_telemetry.py' script from the DE2 course.

Author: Richard Kralovsky

History
16.11.2026 Init.
16.11.2026 Tested functionality of ThingSpeak upload (test_tsupload.py)
19.11.2026 Verified integrated functionality in main
"""
import network
import urequests
import wifi_utils

class ThingSpeakUpload:
    """Wi-Fi and ThingSpeak HTTP POST telemetry uploader."""

    def __init__(self, api_key, ssid, password):
        """Initialize the ThingSpeak data uploader.

        :param api_key: ThingSpeak channel Write API key.
        :param ssid: Wi-Fi network SSID.
        :param password: Wi-Fi network password.
        """
        self.api_key = api_key
        self.ssid = ssid
        self.password = password
        self.api_url = "https://api.thingspeak.com/update"
        self.wifi = network.WLAN(network.STA_IF)

    def _ensure_connection(self):
        """
        Internal method to check and restore the Wi-Fi connection.
        Returns True if connected, False otherwise.
        """
        if not self.wifi.isconnected():
            print("Wi-Fi check: Not connected. Attempting to connect...")
            if not wifi_utils.connect(self.wifi, self.ssid, self.password):
                print("Failed to connect to Wi-Fi.")
                return False
        return True

    def upload_data(self, temperature, humidity, pressure, fan_status, light_status):
        """Upload measured environmental data and actuator states to ThingSpeak.

        Always verifies the Wi-Fi connection before sending.

        :param temperature: Temperature in °C (field1).
        :param humidity: Relative humidity in % RH (field2).
        :param pressure: Atmospheric pressure in hPa (field3).
        :param fan_status: Fan state ``1`` (ON) or ``0`` (OFF) (field4).
        :param light_status: LED strip state ``1`` (ON) or ``0`` (OFF) (field5).
        :return: ``True`` if the upload succeeded, ``False`` otherwise.
        """
        if not self._ensure_connection():
            return False # upload is not performed if there is no network connection

        body = (
            f"api_key={self.api_key}"
            f"&field1={temperature}"
            f"&field2={humidity}"
            f"&field3={pressure}"
            f"&field4={fan_status}"
            f"&field5={light_status}"
        )
        
        response = None
        try:
            response = urequests.post(
                self.api_url,
                data=body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            print(f"Uploaded: T={temperature:.2f}°C | RH={humidity:.2f}% | P={pressure:.2f}hPa | Fan={fan_status} | Light={light_status} | TS={response.text}")
            return True
            
        except Exception as error:
            print("Upload failed (network or server error):", error)
            return False
            
        finally:
            if response is not None:
                response.close()

    def disconnect(self):
        """Disconnect from the network for a clean exit."""
        wifi_utils.disconnect(self.wifi)