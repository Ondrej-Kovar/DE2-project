# Smart Greenhouse Monitor (Raspberry Pi Pico W)

# Smart Greenhouse Monitor (Raspberry Pi Pico W)

[![MicroPython](https://img.shields.io/badge/MicroPython-1.22+-blue.svg)](https://micropython.org/)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%20Pico%20W-red.svg)](https://www.raspberrypi.com/products/raspberry-pi-pico-w/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Embedded systems term project for the **Digital Electronics 2 (DE2)** course at the **Faculty of Electrical Engineering and Communication (FEEC), Brno University of Technology (BUT)**.

---

## Team Members & Responsibilities

| Name | Responsibilities |
|---|---|
| **Adam Koutný** | Block diagram, Wiring diagram, BME sensor, LED display |
| **Ondřej Kovář** | Encoder, Drivers, Main Code |
| **Richard Královský** | Led strip control, Wi-Fi data transmission, Main Code |

---

## Project Overview

### Problem Statement
Maintaining an optimal microclimate inside a greenhouse is essential for healthy plant growth. Sudden temperature spikes or excessive humidity can damage crops or lead to mold and fungal infections. Manual monitoring is time-consuming and often responds too late.

### Solution Summary
The **Smart Greenhouse Monitor** is an automated microclimate control and monitoring unit based on the **Raspberry Pi Pico W** running MicroPython. It:
1. Continuously monitors environmental conditions (temperature, humidity, atmospheric pressure) using an I2C sensor **BME280**.
2. Provides a local visual interface (**OLED display & RGB status LED**) showing live measurements and system status.
3. Allows users to configure temperature and humidity setpoints (thresholds) using physical inputs (**rotary encoder**).
4. Automatically activates an extraction fan via a transistor/MOSFET driver when conditions exceed target thresholds.
5. Automatically turns on light after sunset to ensure constant growth
6. Transmits telemetry data over Wi-Fi to ThingSpeak.

---

## Hardware Inventory & Wiring

### Bill of Materials (BOM)
| Component | Description / Specifications | Interface / Protocol | Supply Voltage |
|---|---|---|---|
| **Raspberry Pi Pico W** | RP2040 microcontroller with 2.4 GHz Wi-Fi | Core controller | 5 V (VBUS) / 3.3 V logic |
| **BME280** | Temperature, Relative Humidity, Pressure sensor | I2C (SDA/SCL) | 3.3 V |
| **Light Sensor (LDR)** | Ambient light sensor in voltage divider circuit (LDR + 10 kΩ resistor) | Analog (ADC0 / GP26) | 3.3 V |
| **Display** | 1.3" OLED (SH1106 driver, 128x64 px) | I2C (SDA/SCL) | 3.3 V |
| **Actuator (Fan)** | 12 V DC ventilation / extraction fan | PWM / Digital switching via MOSFET | External 12 V DC supply |
| **Actuator (Light)** | 5 V DC LED lighting strip (grow / white light) | PWM / Digital switching via MOSFET | External 5 V DC supply |
| **Power Driver** | N-channel logic-level MOSFET (e.g. IRLZ44N, 2N7000 or AO3400) + flyback diode for inductive fan load | Digital GPIO / PWM | - |
| **Input Controls** | Rotary Encoder (KY-040) with integrated push-button | 3x Digital GPIO (internal/external pull-up) | 3.3 V |
| **External power supply 5V, 12V** | External DC power adapters for the LED strip (5 V) and extraction fan (12 V) | Power rails / DC jack | 5 V / 12 V |
<!--| **Status Indicator** | Common cathode/anode RGB LED with current-limiting resistors (e.g. 220–330 Ω) | 3x GPIO / PWM | 3.3 V |-->

### Pinout & Wiring Plan

| Pico W Pin | Pin Name / Function | Connected Module & Pin | Notes / Description |
|---|---|---|---|
| **GP2** | GPIO Input | KY-040 Encoder CLK (A) | Direction & step detection (Pull-up) |
| **GP3** | GPIO Input | KY-040 Encoder DT (B) | Direction & step detection (Pull-up) |
| **GP4** | I2C0 SDA | BME280 SDA & SH1106 OLED SDA | Shared I2C0 bus data line (pull-up resistors) |
| **GP5** | I2C0 SCL | BME280 SCL & SH1106 OLED SCL | Shared I2C0 bus clock line |
| **GP12** | GPIO Input | KY-040 Encoder SW (Switch) | Menu select / mode change button (Pull-up) |
| **GP14** | GPIO / PWM Output | LED Strip Data | Switched 5 V LED strip lighting control |
| **GP15** | GPIO / PWM Output | Fan Driver Gate (MOSFET) | Switched 12 V ventilation fan control |
| **GP26** | ADC0 Analog Input | Photoresistor (LDR) divider | Ambient light level measurement (0–3.3 V) |
| **3V3** | Power Output | 3.3 V Power Rail | Powers BME280, SH1106 OLED, KY-040, and LDR divider |
| **5V** | External Power Supply | LED Strip VCC (+5V) | Dedicated external power for the 5 V LED strip lighting |
| **12V** | External Power Supply | Actuator (Fan) VCC (+12V) | Dedicated external power for the 12 V ventilation fan |
| **GND** | Common Ground | System Ground (GND) | Shared common ground for Pico, 3.3 V, 5 V, and 12 V circuits |

---

## System Architecture & Design

### Block Diagram
![Block Diagram](docs/Images/Block_diagram.png)

### Wiring Diagram
![Wiring Diagram](docs/Images/Wiring.png)

<!--
## Timing & Concurrency Plan

To keep the system responsive without blocking user input or display updates, the software employs cooperative multitasking using MicroPython's **`uasyncio`**:

| Task Name | Interval / Trigger | Priority / Type | Responsibility |
|---|---|---|---|
| `task_inputs` | 10–25 ms | High (Async task) | Continuously monitors and debounces rotary encoder (CLK, DT) and button (SW); adjusts menu and threshold values. |
| `task_sensors` | 500–1000 ms | Medium (Async task) | Reads raw values from BME280 via I2C and ambient light level from LDR via ADC0; validates sensor ranges. |
| `task_control` | 500 ms | Medium (Async task) | Evaluates climate conditions (fan control with hysteresis) and ambient light (LED strip control). Updates RGB LED indicator. |
| `task_display` | 150–250 ms | Low/Medium (Async task) | Updates SH1106 OLED frame buffer with current readings, threshold setpoints, and fan/light status icons. |
| `task_telemetry` | 15–30 s | Background (Optional) | Formats JSON telemetry payload and publishes to MQTT broker via Wi-Fi; handles network reconnects non-blockingly. |

---
-->

## Repository Structure

text
├── docs/                       # Sphinx documentation source files
│   ├── conf.py                 # Sphinx configuration
│   ├── index.rst               # Documentation root
│   └── api/                    # Auto-generated or manual class documentation
├── Images/                     # Images
│   ├── Block_diagram.png       
│   └── Wiring.png              
├── src/                        # MicroPython production code
│   ├── main.py                 # Application entry point & uasyncio task loop
│   ├── config.py               # Hardware pin definitions & default thresholds
│   ├── drivers/                # Reusable component driver classes
│   │   ├── bme280.py           # BME280 I2C driver
│   │   ├── display.py          # Display abstraction (OLED / Nokia)
│   │   ├── fan_controller.py   # Fan PWM / digital driver class
│   │   └── button.py           # Debounced button / input handler class
│   └── lib/                    # Third-party libraries (if any)
├── tests/                      # Component unit / isolation test scripts
│   ├── test_bme280.py          # Standalone sensor test
│   ├── test_fan.py             # Driver circuit validation test
│   └── test_display.py         # Display rendering test
├── presentation/               # Poster and demonstration assets
│   ├── poster.pdf              # Final A3 project poster
│   └── video_link.txt          # Link to 1-2 min demonstration video
├── LICENSE                     # License file (e.g. MIT)
└── README.md                   # This project report & documentation
---

## Setup & Installation Instructions

### Prerequisites
1. **Raspberry Pi Pico W** flashed with the latest MicroPython firmware (v1.22 or newer).
2. **Thonny IDE** or **Visual Studio Code (with MicroPico extension)** installed on your computer.

### Quick Start
1. Clone this repository:
   ```bash
   git clone https://github.com/Ondrej-Kovar/DE2-project.git
   ```
2. Connect your Pico W to your computer via USB.
3. Upload files from `src/` to the root filesystem of your Pico W.
4. Run `main.py` directly from your IDE or reset the Pico W to execute automatically on boot.

---

## Testing & Verification


### 1. Sensor Verification (BME280)
- **Measurement Range Tested:** Temp [°C], Humidity [%RH], Pressure [hPa].
- **Sampling Stability:** Observed sensor noise, calibration offset, and response time when subjected to elevated temperature or humidity.

### 2. Fan Driver & Actuation Test
- **Driver switching test:** Verified switching voltage with multimeter/oscilloscope.
- **Hysteresis control:** Fan turns ON when $T > T_{threshold}$ and OFF when $T < T_{threshold} - \Delta T$ to prevent rapid on/off oscillation.

### 3. Display Refresh Rate & Responsiveness
- Verified non-blocking screen updates without stuttering input recognition.

---

## Sphinx Documentation

The project includes Sphinx documentation for all custom driver classes and public APIs.

### Building documentation locally:
```bash
cd docs
pip install sphinx sphinx-rtd-theme
make html
```
View the generated output in `docs/_build/html/index.html`.

---

## Presentation & Deliverables

- **Project Poster (A3):** [Link to Poster PDF](presentation/poster.pdf) *(TODO: Add link)*
- **Demo Video (1–2 minutes):** [YouTube / Video Link](https://youtube.com/...) *(TODO: Add video URL)*

---

## References & Acknowledgments

- MicroPython documentation: [https://docs.micropython.org/](https://docs.micropython.org/)
- Raspberry Pi Pico W documentation: [https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
- Course lab exercises: [BUT FEEC DE2 MicroPython Labs](https://github.com/tomas-fryza/esp-micropython)
