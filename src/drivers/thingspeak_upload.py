"""
ThingSpeak IoT Telemetry Module

This module provides the `ThingSpeakUpload` class for sending smart greenhouse 
data to the cloud. It uploads BME280 sensor readings and current statuses of 
actuators (fan, light). It also ensures the Wi-Fi connection is active before 
attempting any data transfer.

Based on the 'bme280_telemetry.py' script from the DE2 course.
"""
import network
import time
import urequests
import wifi_utils

class ThingSpeakUpload:
    def __init__(self, api_key, ssid, password):
        """
        Initialize the ThingSpeak data uploader.
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
        """
        Uploads measured data to ThingSpeak.
        Always verifies Wi-Fi connection before sending.
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