"""
Pi Weather Station
==================
Reads temperature and humidity from a DHT22 sensor
and sends the data to your meow meow scratch API.

Wiring (DHT22 → Pi):
  VCC  → 3.3V (pin 1)
  DATA → GPIO4 (pin 7)
  GND  → GND  (pin 6)

Setup:
  pip install -r requirements.txt
  export MEOW_API_KEY="your-key"
  python weather_station.py
"""

import os
import sys
import time
import board
import adafruit_dht
from meow_sdk import Meow, MeowError

API_KEY = os.environ.get("MEOW_API_KEY")
if not API_KEY:
    print("Set MEOW_API_KEY environment variable")
    sys.exit(1)

APP = "pi-weather-station"
ENDPOINT = "readings"
INTERVAL = 30  # seconds between readings

api = Meow(api_key=API_KEY)
sensor = adafruit_dht.DHT22(board.D4)


def read_sensor():
    """Read temperature (°C) and humidity (%) from the DHT22."""
    try:
        temperature = sensor.temperature
        humidity = sensor.humidity
        if temperature is not None and humidity is not None:
            return {"temperature": round(temperature, 1), "humidity": round(humidity, 1)}
    except RuntimeError:
        # DHT sensors occasionally fail to read — just skip this cycle
        pass
    return None


def main():
    print(f"Weather station running — sending every {INTERVAL}s")
    print("Press Ctrl+C to stop\n")

    while True:
        reading = read_sensor()
        if reading:
            try:
                api.send(APP, ENDPOINT, reading)
                print(f"Sent: {reading['temperature']}°C, {reading['humidity']}%")
            except MeowError as e:
                print(f"Send failed: {e}")
        else:
            print("Sensor read failed, retrying next cycle")

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
