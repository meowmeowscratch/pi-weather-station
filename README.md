# Pi Weather Station

Read temperature and humidity from a DHT22 sensor and send the data to [meow meow scratch](https://meowmeowscratch.com).

## Wiring

| DHT22 | Raspberry Pi |
|-------|-------------|
| VCC   | 3.3V (pin 1) |
| DATA  | GPIO4 (pin 7) |
| GND   | GND (pin 6) |

## Setup

```bash
pip install -r requirements.txt
export MEOW_API_KEY="your-key"
python weather_station.py
```

Sends a reading every 30 seconds. Edit `INTERVAL` in the script to change the frequency.

## API setup

Create an app called `pi-weather-station` with a collection endpoint called `readings` and add `temperature` (number) and `humidity` (number) fields.
