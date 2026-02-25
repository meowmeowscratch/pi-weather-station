# Pi Weather Station

Build your own weather station! This project reads the temperature and humidity from a DHT22 sensor and sends the data to the internet every 30 seconds. Track the weather in your room, your greenhouse, or outdoors — and check it from anywhere on your phone.

---

## What you'll learn

- **How digital temperature/humidity sensors work** — The DHT22 sensor converts temperature and humidity into a digital signal that your Raspberry Pi can read through a single wire.
- **Handling unreliable sensor reads gracefully** — Real-world sensors sometimes fail to respond. You'll learn how to write code that expects failures and handles them cleanly instead of crashing.
- **Periodic data collection** — How to set up a loop that takes a reading at regular intervals (every 30 seconds) and keeps running until you stop it.
- **Sending data to an API** — How to push your sensor data to the internet so you can view it from any device.

---

## What you'll need

### Hardware

| Component | What it is | Why you need it |
|-----------|-----------|-----------------|
| **Raspberry Pi** | Any model with GPIO pins (the two rows of metal pins along one edge). Pi Zero, Pi 3, Pi 4, Pi 5 — they all work. | This is the small computer that runs your code and talks to the sensor. |
| **DHT22 sensor** | Also called AM2302. A small blue or white rectangular sensor with a grid of holes on the front. Measures temperature from -40 to 80 degrees C and humidity from 0 to 100%. Communicates using a single data wire. | This is the sensor that actually measures the temperature and humidity. |
| **3 jumper wires** | Small wires with connectors on each end (you need female-to-female if your sensor has pins, or female-to-male if it has a pin header). One red, one yellow/green, one black is the convention, but any colors work. | These connect the sensor to the Pi. |

> **About DHT22 modules:** Some DHT22 modules come on a small circuit board with 3 pins (VCC, DATA, GND) and a built-in pull-up resistor. If yours has 4 bare pins, you'll also need a **10K ohm resistor** between VCC and DATA. The resistor "pulls up" the data line so the sensor can communicate reliably. If you bought a module on a small blue or red breakout board with only 3 pins, the resistor is already built in and you don't need to worry about it.

### Software

| Software | What it is |
|----------|-----------|
| **Python 3** | The programming language this project is written in. It comes pre-installed on Raspberry Pi OS. |
| **meow meow scratch account** | A free account at [meowmeowscratch.com](https://meowmeowscratch.com) where your weather data gets sent. You'll get an API key (a secret password that lets your code talk to the website). |

---

## Wiring diagram

Connect your DHT22 sensor to the Raspberry Pi using three jumper wires. The diagram below shows which pins to connect:

```
    Raspberry Pi               DHT22 Sensor
    +-----------+              +---------+
    |           |              | ======= |  (grid side facing you)
    | 3.3V   o--+----- red ----+-- VCC   |
    | (pin 1)   |              |         |
    |           |              |         |
    | GPIO4  o--+--- yellow ---+-- DATA  |
    | (pin 7)   |              |         |
    |           |              |         |
    | GND    o--+---- black ---+-- GND   |
    | (pin 6)   |              +---------+
    +-----------+
```

### Pin reference table

| DHT22 pin | What it does | Connects to | Pi pin number |
|-----------|-------------|-------------|---------------|
| **VCC** | Power supply for the sensor (3.3 volts) | 3.3V | Pin 1 (top-left pin on the Pi) |
| **DATA** | Sends temperature and humidity readings to the Pi | GPIO4 | Pin 7 |
| **GND** | Ground (completes the electrical circuit) | GND | Pin 6 |

> **Tip:** "Pin 1" and "Pin 7" refer to the physical pin numbers on the Pi's GPIO header. If you look at the Pi with the USB ports facing you, pin 1 is the top-left pin. You can find a full pinout diagram by running `pinout` in the terminal on your Pi.

---

## Step-by-step setup

### Step 1: Install the system library

The DHT22 sensor library needs a system-level library called `libgpiod2` to communicate with the Pi's GPIO pins. Open a terminal on your Pi and run:

```bash
sudo apt install libgpiod2
```

> **What is `sudo apt install`?** `sudo` means "run this as an administrator" (it will ask for your password). `apt install` is how you install software packages on Raspberry Pi OS (and other Debian/Ubuntu-based systems). `libgpiod2` is a library that lets programs talk to GPIO pins.

### Step 2: Install Python packages

This project needs two Python packages (libraries of code that other people wrote so you don't have to):

```bash
pip install -r requirements.txt
```

> **What is `pip`?** `pip` is the package installer for Python. It downloads and installs Python libraries from the internet. The `-r requirements.txt` flag tells pip to read a file called `requirements.txt` and install everything listed in it.

This installs:

- **`adafruit-circuitpython-dht`** — Adafruit's library that handles the precise timing protocol the DHT22 needs. The DHT22 communicates by sending rapid pulses on the data wire, and each pulse needs to be measured down to the microsecond. This library handles all of that complexity for you.
- **`meow-sdk`** — The Python library for sending data to your meow meow scratch account.

> **If `pip` doesn't work:** On newer versions of Raspberry Pi OS, you may need to use `pip install --break-system-packages -r requirements.txt` or create a virtual environment first with `python3 -m venv venv && source venv/bin/activate` and then run the pip install command.

### Step 3: Set up your API key

Your code needs to know your meow meow scratch API key so it can send data. You set this using an **environment variable** — a value that is stored in your terminal session and can be read by any program you run.

```bash
export MEOW_API_KEY="your-key-here"
```

Replace `your-key-here` with your actual API key from your meow meow scratch account (keep the quotes).

> **What is an environment variable?** Think of it like a sticky note that your terminal remembers. When your Python code runs `os.environ.get("MEOW_API_KEY")`, it reads that sticky note. This way, your secret API key stays out of your code and won't accidentally get shared.

> **Note:** This environment variable only lasts for your current terminal session. If you close the terminal and open a new one, you'll need to run the `export` command again. To make it permanent, you can add the line to your `~/.bashrc` file.

### Step 4: Set up your API endpoint

Before you can send data, you need to create a place to store it on meow meow scratch. See the [API setup](#api-setup) section below.

### Step 5: Run the weather station

```bash
python weather_station.py
```

You should see output like this:

```
Weather station running — sending every 30s
Press Ctrl+C to stop

Sent: 22.3°C, 45.1%
Sent: 22.4°C, 44.8%
Sensor read failed, retrying next cycle
Sent: 22.3°C, 45.0%
```

The "Sensor read failed" message is normal — see the troubleshooting section below for details. Press `Ctrl+C` to stop the program.

---

## How the code works

Here's a plain-English walkthrough of what the code does. Open `weather_station.py` in a text editor and follow along.

### 1. Setting up the sensor

```python
sensor = adafruit_dht.DHT22(board.D4)
```

This creates a sensor object connected to **GPIO pin 4** (written as `board.D4` in the code). The `board` library maps friendly pin names like `board.D4` to the actual hardware pins, so the same code works on different Pi models. From this point on, you can ask `sensor` for the temperature and humidity.

### 2. Reading the sensor

```python
def read_sensor():
    try:
        temperature = sensor.temperature
        humidity = sensor.humidity
        if temperature is not None and humidity is not None:
            return {"temperature": round(temperature, 1), "humidity": round(humidity, 1)}
    except RuntimeError:
        pass
    return None
```

DHT sensors use precise timing to communicate — sometimes the timing gets slightly off, and a read fails. This is normal and expected, which is why the code catches `RuntimeError` and just tries again next cycle. The code also checks that neither value is `None`, because occasionally the sensor returns a partial read where the data got corrupted on the way.

When a read succeeds, it returns a **dictionary** (a collection of named values) with the temperature and humidity, each rounded to one decimal place.

### 3. The main loop

```python
while True:
    reading = read_sensor()
    if reading:
        api.send(APP, ENDPOINT, reading)
    time.sleep(INTERVAL)
```

This is the core pattern: **read, check, send, sleep**.

1. **Read** — Ask the sensor for the current temperature and humidity.
2. **Check** — If the read succeeded (not `None`), continue. If it failed, skip to sleep.
3. **Send** — Push the data to your meow meow scratch API.
4. **Sleep** — Wait 30 seconds, then repeat.

This loop runs forever until you press `Ctrl+C`.

---

## Troubleshooting

### "Sensor read failed, retrying next cycle"

**This is normal!** DHT sensors use very precise microsecond-level timing to send data. Sometimes the Raspberry Pi is briefly busy doing something else (running background tasks, updating the screen, etc.) and misses part of the signal. The code is designed to handle this — it just skips the failed read and tries again 30 seconds later. If you see this message occasionally, everything is working as expected.

### Every single read fails (you never see a successful "Sent" message)

- **Check your wiring.** Make sure VCC goes to 3.3V (not 5V), DATA goes to GPIO4, and GND goes to GND. A loose wire is the most common cause.
- **Try 5V instead of 3.3V.** Some DHT22 modules work more reliably with 5V power. Move the VCC wire from pin 1 (3.3V) to pin 2 (5V).
- **Check your pull-up resistor.** If your sensor has 4 bare pins (not on a breakout board), you need a 10K ohm resistor between VCC and DATA.

### `ImportError: libgpiod` or similar `libgpiod` errors

You need to install the system GPIO library. Run:

```bash
sudo apt install libgpiod2
```

Then try running the script again.

### Temperature seems wrong (too high or in the wrong units)

The DHT22 returns temperature in **Celsius** by default. If you're used to Fahrenheit, you can convert with this formula:

```
Fahrenheit = (Celsius * 9/5) + 32
```

For example, 22°C = 71.6°F. If the reading seems wildly off (like 0°C when it's warm), check your wiring.

### `RuntimeError: DHT sensor not found`

- Make sure the sensor is connected to **GPIO4** (physical pin 7). If you connected it to a different GPIO pin, you'll need to change `board.D4` in the code to match.
- Make sure the sensor is getting power (VCC connected to 3.3V or 5V).

### `Set MEOW_API_KEY environment variable`

You need to set your API key before running the script. Run:

```bash
export MEOW_API_KEY="your-key-here"
```

in the same terminal window where you run the Python script. See [Step 3](#step-3-set-up-your-api-key) above.

---

## API setup

Before your weather station can send data, you need to create a place to store it on meow meow scratch.

1. **Log in** to your account at [meowmeowscratch.com](https://meowmeowscratch.com).
2. **Create a new app** called `pi-weather-station`.
3. **Create a collection endpoint** inside that app called `readings`.
4. **Add two fields** to the `readings` endpoint:
   - `temperature` — type: **number**
   - `humidity` — type: **number**

Once this is set up, the code will send data to:

```
POST /apps/pi-weather-station/readings
```

with a JSON body like:

```json
{
  "temperature": 22.3,
  "humidity": 45.1
}
```

Every 30 seconds, a new reading gets added to your collection. You can view your data on the meow meow scratch dashboard.

---

## Changing the reading interval

By default, the station sends a reading every 30 seconds. To change this, open `weather_station.py` and find this line near the top:

```python
INTERVAL = 30  # seconds between readings
```

Change `30` to however many seconds you want between readings. The DHT22 can be read at most once every 2 seconds, so don't set it lower than that.
