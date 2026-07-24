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

# os — Lets us read environment variables (like MEOW_API_KEY) from the system.
#       Environment variables are a way to pass secret values to your code
#       without putting them directly in the source file.
import os

# sys — Provides sys.exit() which lets us stop the program immediately
#        if something is wrong (like a missing API key).
import sys

# time — Provides time.sleep() which pauses the program for a given number
#         of seconds. We use it to wait between sensor readings.
import time

# board — Maps friendly pin names (like board.D4) to the Pi's physical GPIO
#          pins. Works across different Pi models so your code doesn't need
#          to change if you switch from a Pi 3 to a Pi 4, for example.
import board

# adafruit_dht — Adafruit's library that handles the precise microsecond-level
#                 timing protocol DHT22 sensors need. The sensor communicates by
#                 sending rapid electrical pulses, and this library interprets
#                 those pulses into temperature and humidity values.
import adafruit_dht

# Meow — The main class from the meow-sdk library. It handles sending your
#         sensor data to the meow meow scratch API over the internet.
# MeowError — The general "something went wrong with the API" error. The two
#              below are more specific versions of it, so we can give you a
#              more helpful message about what to actually do:
# AuthError — your API key was rejected (wrong, expired, or not set).
# RateLimitError — you're sending data faster than your plan allows.
from meow_sdk import Meow, MeowError, AuthError, RateLimitError

# --- Configuration ---

# Read the API key from the environment variable. os.environ.get() returns
# None if the variable isn't set, rather than crashing with an error.
API_KEY = os.environ.get("MEOW_API_KEY")
if not API_KEY:
    print("Set MEOW_API_KEY environment variable")
    sys.exit(1)

# The name of your app and endpoint on meow meow scratch.
# These must match what you created in the dashboard.
APP = "pi-weather-station"
ENDPOINT = "readings"

# How many seconds to wait between readings. The DHT22 can be read at most
# once every 2 seconds, so don't set this lower than 2.
INTERVAL = 30  # seconds between readings

# Create an API client that will send data to meow meow scratch.
api = Meow(api_key=API_KEY)

# Create a sensor object on GPIO4. The library handles all low-level
# communication with the DHT22 — you just ask for .temperature or .humidity
# and it takes care of the precise timing protocol behind the scenes.
sensor = adafruit_dht.DHT22(board.D4)


def read_sensor():
    """Read temperature (°C) and humidity (%) from the DHT22."""
    try:
        temperature = sensor.temperature
        humidity = sensor.humidity

        # The sensor returns None if the read was partially successful but
        # the data was corrupted (failed a checksum verification). We only
        # return a result when both values are valid.
        if temperature is not None and humidity is not None:
            return {"temperature": round(temperature, 1), "humidity": round(humidity, 1)}

    except RuntimeError:
        # DHT sensors use very precise timing (microsecond-level). Sometimes
        # a read fails because the Pi was briefly busy doing something else
        # (like running a background process). This is completely normal and
        # expected — we just skip this reading and try again next cycle.
        pass

    return None


def main():
    print(f"Weather station running — sending every {INTERVAL}s")
    print("Press Ctrl+C to stop\n")

    # Main loop: read, check, send, sleep — repeats forever until Ctrl+C.
    while True:
        # Step 1: READ — Ask the sensor for current temperature and humidity.
        reading = read_sensor()

        if reading:
            # Step 2: SEND — If the read succeeded, push the data to the API.
            try:
                api.send(APP, ENDPOINT, reading)
                print(f"Sent: {reading['temperature']}°C, {reading['humidity']}%")
            except AuthError as e:
                # A rejected key will never fix itself, so there's no point
                # looping forever printing the same error. Stop and tell the
                # user exactly what to check.
                print(f"API key rejected: {e}")
                if e.hint:
                    print(f"Hint: {e.hint}")
                sys.exit(1)
            except RateLimitError as e:
                # You're sending faster than your plan allows. Waiting a full
                # minute is almost always enough to be allowed back in.
                print(f"Rate limited: {e}")
                time.sleep(60)
            except MeowError as e:
                # Any other API problem (network dropped, server hiccup).
                # Print it but keep the loop running -- the next reading in
                # INTERVAL seconds will probably succeed.
                print(f"Send failed: {e}")
                # .hint is a plain-English suggestion the API sends back when
                # it knows how to fix the problem. It isn't always present.
                if e.hint:
                    print(f"Hint: {e.hint}")
        else:
            print("Sensor read failed, retrying next cycle")

        # Step 3: SLEEP — Wait before taking the next reading.
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
