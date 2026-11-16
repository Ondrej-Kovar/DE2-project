"""
Test script for the ThingSpeak data uploader.
This script allows you to test the upload functionality on a standard PC without a Raspberry Pi Pico.
It simulates (mocks) MicroPython-specific network libraries and uses the standard 'requests' library
to upload dummy sensor data (temperature, humidity, pressure, fan status, and light status) directly 
to your ThingSpeak dashboard.
"""
import sys
import time
import requests

class MockWLAN:
    def isconnected(self): 
        return True

class MockNetwork:
    STA_IF = 1
    def WLAN(self, mode):
        return MockWLAN()

class MockWifiUtils:
    def connect(self, wifi, ssid, pswd): 
        return True
    
    def disconnect(self, wifi): 
        print("Virtual Wi-Fi disconnected.")

sys.modules['network'] = MockNetwork()
sys.modules['wifi_utils'] = MockWifiUtils()
sys.modules['urequests'] = requests 


class ThingSpeakUpload:
    def __init__(self, api_key, ssid, password):
        self.api_key = api_key
        self.ssid = ssid
        self.password = password
        self.api_url = "https://api.thingspeak.com/update"
        
        import network
        self.wifi = network.WLAN(network.STA_IF)

    def _ensure_connection(self):
        import wifi_utils
        if not self.wifi.isconnected():
            print("Wi-Fi check: Not connected. Attempting to connect...")
            if not wifi_utils.connect(self.wifi, self.ssid, self.password):
                print("Failed to connect to Wi-Fi.")
                return False
        return True

    def upload_data(self, temperature, humidity, pressure, fan_status, light_status):
        if not self._ensure_connection():
            return False

        body = (
            f"api_key={self.api_key}"
            f"&field1={temperature}"
            f"&field2={humidity}"
            f"&field3={pressure}"
            f"&field4={fan_status}"
            f"&field5={light_status}"
        )
        response = None
        
        import urequests
        try:
            response = urequests.post(
                self.api_url,
                data=body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            print(f"Uploaded: T={temperature:.2f}°C | RH={humidity:.2f}% | P={pressure:.2f}hPa | Fan={fan_status} | Light={light_status} | TS_entry={response.text}")
            return True
            
        except Exception as error:
            print("Upload failed (network or server error):", error)
            return False
            
        finally:
            if response is not None:
                response.close()

    def disconnect(self):
        import wifi_utils
        wifi_utils.disconnect(self.wifi)


def clear_thingspeak_channel(channel_id, user_api_key):
    print("Clearing channel history...")
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json"
    response = requests.delete(url, data={"api_key": user_api_key})
    
    if response.status_code == 200:
        print("Channel cleared successfully.")
    else:
        print(f"Failed to clear channel: {response.text}")


if __name__ == "__main__":
    WRITE_API_KEY = "J9ZA8CSYK7X9E6JS"
    
    # Optional: Clear channel before testing (requires User API Key and Channel ID)
    # USER_API_KEY = "YOUR_USER_API_KEY"
    # CHANNEL_ID = "YOUR_CHANNEL_ID"
    # clear_thingspeak_channel(CHANNEL_ID, USER_API_KEY)
    # time.sleep(2)
    
    ts = ThingSpeakUpload(WRITE_API_KEY, "dummy_ssid", "dummy_password")
    
    print("Sending test data to ThingSpeak...")
    ts.upload_data(temperature=24.5, humidity=60.1, pressure=1013.2, fan_status=1, light_status=0)
    
    print("Waiting 16 seconds to comply with ThingSpeak rate limits...")
    time.sleep(16)
    
    ts.upload_data(temperature=23.0, humidity=62.5, pressure=1014.0, fan_status=0, light_status=1)
    
    print("Test finished. Check your ThingSpeak dashboard.")