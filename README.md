# Smart Greenhouse Monitor (Raspberry Pi Pico W)

[![MicroPython](https://img.shields.io/badge/MicroPython-1.22+-blue.svg)](https://micropython.org/)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%20Pico%20W-red.svg)](https://www.raspberrypi.com/products/raspberry-pi-pico-w/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Embedded systems term project for the **Digital Electronics 2 (DE2)** course at the **Faculty of Electrical Engineering and Communication (FEEC), Brno University of Technology (BUT)**.

---

## Team Members & Responsibilities

| Name | Responsibilities |
|---|---|
| **Adam Koutný** | Block diagram, Wiring diagram, BME sensor, OLED display, Poster |
| **Ondřej Kovář** | Encoder, Drivers, Low power mode, Documentation, README |
| **Richard Královský** | LED strip control, Wi-Fi data transmission, Full power mode, README |

---

## Project Overview

### Problem Statement
Maintaining an optimal microclimate inside a greenhouse is essential for healthy plant growth. Sudden temperature spikes or excessive humidity can damage crops or lead to mold and fungal infections. Manual monitoring is time-consuming and often responds too late.

### Solution Summary
The **Smart Greenhouse Monitor** is an automated microclimate control and monitoring unit based on the **Raspberry Pi Pico W** running MicroPython. It:
1. Continuously monitors environmental conditions (temperature, humidity, atmospheric pressure) using an I2C sensor **BME280**.
2. Automatically turns on light (**Light sensor**) after sunset to ensure constant growth.
3. Provides a local visual interface (**OLED display**) showing live measurements and system status.
4. Automatically activates an extraction fan via a MOSFET driver when conditions exceed target thresholds.
5. Allows users to configure temperature, humidity and light setpoints (thresholds) using physical inputs (**Rotary encoder**). 
6. Transmits telemetry data, light and fan status over Wi-Fi to ThingSpeak.
7. Supports selectable **Full-Power** and **Low-Power** (`machine.lightsleep()`) operating modes via `settings.py`.

---

**Live Telemetry Dashboard:** [View Public ThingSpeak Channel](https://thingspeak.com/channels/3558132)

---

## Hardware Inventory & Wiring

### Bill of Materials (BOM)
| Component | Description / Specifications | Interface / Protocol | Supply Voltage |
|---|---|---|---|
| [**Raspberry Pi Pico W**](https://pip.raspberrypi.com/documents/RP-008312-DS-pico-w-datasheet.pdf) | RP2040 microcontroller with 2.4 GHz Wi-Fi | Core controller | 5 V (VBUS) / 3.3 V logic |
| [**BME280**](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf) | Temperature, Relative Humidity, Pressure sensor | I2C (SDA/SCL) | 3.3 V |
| **Light Sensor** | Ambient light sensor in voltage divider circuit (LDR + 5 kΩ resistor) | Analog (ADC0 / GP26) | 3.3 V |
| [**OLED Display SH1106**](https://cdn.velleman.eu/downloads/29/infosheets/sh1106_datasheet.pdf) | 1.3" OLED (SH1106 driver, 128x64 px) | I2C (SDA/SCL) | 3.3 V |
| **Fan** | 5 V DC ventilation fan | Digital switching via MOSFET | 5 V VBUS |
| [**LED Strip NeoPixel WS2812B**](https://www.laskakit.cz/user/related_files/ws2812b.pdf) | Individually addressable RGB LED strip | Digital data (via neopixel library) | External 3 V DC supply |
| **Fan Driver** | N-channel logic-level MOSFET [STP36NF06L](https://www.st.com/resource/en/datasheet/stb36nf06l.pdf) + 100 kΩ resistor | Digital GPIO | - |
| **Flyback diode** | Schottky or fast Si diode | Across fan terminals | 5 V VBUS |
| [**Rotary Encoder KY-040**](https://www.handsontec.com/dataspecs/module/Rotary%20Encoder.pdf) | Rotary Encoder with integrated push-button for input control | 3x Digital GPIO (internal pull-up) | 3.3 V |
| **External power supply 3 V** | External DC power adapters for the LED strip (3V) | Power rails / DC jack | 3 V |

### Pinout & Wiring Plan

| Pico W Pin | Pin Name / Function | Connected Module & Pin | Notes / Description |
|---|---|---|---|
| **GP2** | GPIO Input | Encoder CLK (A) | Direction & step detection (Pull-up) |
| **GP3** | GPIO Input | Encoder DT (B) | Direction & step detection (Pull-up) |
| **GP4** | I2C0 SDA | BME280 SDA & SH1106 OLED SDA | Shared I2C0 bus data line (pull-up resistors) |
| **GP5** | I2C0 SCL | BME280 SCL & SH1106 OLED SCL | Shared I2C0 bus clock line |
| **GP12** | GPIO Input | Encoder button (SW) | Threshold select button (Pull-up) |
| **GP14** | GPIO | LED Strip Data | NeoPixel LED strip lighting control |
| **GP15** | GPIO | Fan Driver Gate (MOSFET) | Switched 5 V ventilation fan control |
| **GP26** | ADC0 Analog Input | Light Sensor | Ambient light level measurement (0–3.3 V) |
| **3V3** | Pico Power Output | 3.3 V Power Rail | Powers BME280, SH1106 OLED, KY-040, and Light Sensor |
| **VBUS** | Pico 5V Power Output | Fan VCC (+5) | Powers Fan |
| **3V** | External Power Supply | LED Strip | Dedicated external power for the 3 V LED strip lighting |
| **GND** | Common Ground | System Ground (GND) | Shared common ground for Pico, 3.3 V, 5 V VBUS, 3 V external circuits |

---

## System Architecture & Design

### Block Diagram
![Block Diagram](Images/Block_diagram.png)

### Wiring Diagram
![Wiring Diagram](Images/Wiring.png)

---

## Timing & Concurrency Plan

To achieve a responsive user experience (UX), the software avoids long blocking `time.sleep()` calls in favor of a **non-blocking "superloop"** based on `time.ticks_ms()` paired with **Hardware Interrupts (IRQs)** for both rotary encoder rotation and button presses.

To accommodate the 100 kHz I2C bus speed without overloading the CPU, sensor readings, OLED updates, and cloud telemetry are decoupled into independent time intervals.

| Logical Task | Interval / Trigger | Estimated Duration | Responsibility |
|---|---|---|---|
| `RotaryEncoder` IRQs (`_on_rotate`, `_on_button`) | On `CLK` change / `SW` falling edge (IRQ) | < 0.1 ms (Microseconds) | Captures encoder rotation (`CLK`, `DT`) and debounced button presses (`SW`, 200 ms) in the background so inputs are never missed. |
| **Input Handling** | Every 10 ms | < 1 ms | Checks the IRQ button flag (`is_button_pressed()`), cycles menu modes (0–4), and applies the active encoder value to thresholds. |
| **OLED Refresh** | Every 250 ms *(or on button click)* | ~ 80–100 ms | Renders environmental data, thresholds, cursor, and actuator states to the SH1106 display over I2C. |
| **Sensors & Control** | Every 1000 ms (1 s) | ~ 10–15 ms | Reads BME280 (I2C) and 10-sample averaged LDR (ADC), evaluates hysteresis logic, and updates the MOSFET fan and NeoPixel LED strip (LED writes occur only on state change). |
| **Cloud Telemetry** | Every 30 seconds | ~ 1–3 s *(up to 10 s if reconnecting)* | Verifies Wi-Fi connection and uploads sensor readings and actuator states to ThingSpeak via HTTP POST. *(IRQs ensure encoder rotation and button presses are still captured during network requests).* |

---

### Execution Time Breakdown:
- **Sensors & Logic:** The LDR reading uses 10-sample averaging via ADC (~**0.5 ms**). Reading the BME280 via I2C at 100 kHz takes **~10 ms**. NeoPixel updates (50 LEDs) take **~1.5 ms** and are triggered only when the light state changes.
- **OLED Display:** Pushing the 128×64 frame buffer to the SH1106 over 100 kHz I2C takes **~80–100 ms**. Running this every 250 ms leaves plenty of headroom for the 10 ms input loop while keeping the UI responsive.
- **Cloud Telemetry:** Wi-Fi HTTP POST requests are the main bottleneck (**1–3 seconds**), but running every 30 seconds (respecting the ThingSpeak 15 s free-tier limit) keeps local operation smooth.
### Operating Modes & Power Management
The application supports two operating modes selected via `LOW_POWER_MODE` in `src/settings.py` (dispatched by `src/main.py`):

| Feature | Full-Power Mode (`fullpower.py`) | Low-Power Mode (`lowpower.py`) |
|---|---|---|
| **CPU Idle Strategy** | `time.sleep_ms(10)` (active polling) | `machine.lightsleep()` between 250 ms display ticks |
| **Sensors & Actuators** | Every 1 s | Combined with upload every `ACTIVE_CYCLE_INTERVAL_MS` (default 60 s) |
| **Cloud Telemetry** | Every `UPLOAD_INTERVAL_MS` (default 30 s) | Every `ACTIVE_CYCLE_INTERVAL_MS` (default 60 s) |
| **OLED & Encoder UI** | Continuous (250 ms refresh / 10 ms poll) | Continuous (250 ms refresh / wake-up on tick & IRQ) |
| **Est. Pico W Current** | ~60–80 mA | ~40–55 mA (CPU sleeps ~248 ms per 250 ms tick) |

> **Note:** `machine.lightsleep()` may drop the USB-serial REPL connection in Thonny/VS Code when sleeping longer than 100 ms. Use **Full-Power Mode** for USB debugging and **Low-Power Mode** for standalone deployment.

---

## Repository Structure
```text
DE2-project
├─ docs/                                 # Sphinx project documentation
│  ├─ conf.py                            # Sphinx build configuration
│  └─ index.rst                          # Documentation entry point
├─ Images/                               # System diagrams and dashboard captures
│  ├─ Block_diagram.png                  # High-level system architecture diagram
│  ├─ ThingSpeak.png                     # ThingSpeak live telemetry dashboard screenshot
│  └─ Wiring.png                         # Raspberry Pi Pico W hardware wiring schematic
├─ presentation/                         # Project presentation slides and materials
├─ README.md                             # Project overview, pinout, and documentation
├─ src/                                  # Main MicroPython source code
│  ├─ drivers/                           # Modular hardware driver wrappers
│  │  ├─ actuator.py                     # Digital MOSFET fan switch driver
│  │  ├─ bme280_sensor.py                # BME280 temperature, humidity & pressure wrapper
│  │  ├─ led_strip.py                    # WS2812B NeoPixel LED strip controller
│  │  ├─ light_sensor.py                 # LDR ambient light sensor (ADC) with hysteresis
│  │  ├─ rotary.py                       # KY-040 rotary encoder & button driver (IRQ-based)
│  │  ├─ sh1106_display.py               # SH1106 128×64 OLED display UI wrapper
│  │  ├─ thingspeak_upload.py            # Wi-Fi & ThingSpeak HTTP POST telemetry uploader
│  │  └─ __init__.py                     # Driver package exports
│  ├─ fullpower.py                       # Full-power non-blocking superloop
│  ├─ lowpower.py                        # Low-power lightsleep loop (60 s active cycle)
│  ├─ main.py                            # Entry point & mode dispatcher (reads LOW_POWER_MODE)
│  └─ settings.py                        # Pinout, credentials, power mode, thresholds & intervals
└─ tests/                                # Standalone hardware & integration test scripts
   ├─ test_actuators.py                  # MOSFET fan switching test
   ├─ test_bme280.py                     # BME280 sensor reading test
   ├─ test_i2c_scan.py                   # I2C bus device address scanner
   ├─ test_ldr.py                        # Raw LDR ADC voltage test
   ├─ test_led_strip.py                  # NeoPixel LED strip color/state test
   ├─ test_LightControl.py               # Integrated LDR + LED strip control test
   ├─ test_light_sensor.py               # LightSensor class percentage & hysteresis test
   ├─ test_oled.py                       # SH1106 OLED display rendering test
   ├─ test_results/                      # Hardware test screenshots & verification photos
   │  ├─ test_result_bme280.png          # BME280 terminal output capture
   │  ├─ test_result_i2c_scan.png        # I2C scan output (0x76 & 0x3C detected)
   │  ├─ test_result_LightControl.png    # Integrated light control terminal output
   │  ├─ test_result_LightControl_off.png# LED strip OFF state (sufficient ambient light)
   │  ├─ test_result_LightControl_on.png # LED strip ON state (low ambient light)
   │  ├─ test_result_oled.png            # OLED display rendering test photo
   │  ├─ test_result_oled_state0.png     # OLED monitor screen (menu mode 0)
   │  └─ test_result_rotary.png          # Rotary encoder & button test output
   ├─ test_rotary.py                     # KY-040 rotary encoder & button test
   └─ test_tsupload.py                   # ThingSpeak cloud upload test
```

---

## Setup & Installation Instructions

### Prerequisites
1. **Raspberry Pi Pico W** flashed with the latest MicroPython firmware 
2. **Thonny IDE** or **Visual Studio Code (with MicroPico extension)** installed on your computer.
3. **Firmware:** MicroPython **v1.22+** *(tested on RP2040 / Pico W)*

### Libraries & Dependencies
- **Built-in MicroPython modules:** `machine`, `time`, `neopixel`, `network`, `urequests`
- **External / Course libraries** *(must be uploaded to `/lib` or root on Pico W)*:
  - `bme280.py` – BME280 I2C sensor driver
  - `sh1106.py` – SH1106 128×64 OLED display driver
  - `wifi_utils.py` – Wi-Fi connection helper (from DE2 course labs)

### Quick Start
1. Clone this repository:
   ```bash
   git clone https://github.com/Ondrej-Kovar/DE2-project.git
   ```
2. **Configure `src/settings.py` (Required):** Before uploading, open `src/settings.py` and set:
   - `WIFI_SSID`, `WIFI_PASSWORD`, and `THINGSPEAK_API_KEY`
   - `LOW_POWER_MODE` (`False` for standard full-power superloop, `True` for `lightsleep()` mode)
   - `ACTIVE_CYCLE_INTERVAL_MS` *(optional, default `60000` ms for low-power measure & upload cycle)*
3. Connect your Pico W to your computer via USB.
4. Upload all files from `src/` to the root filesystem of your Pico W (ensure `bme280.py`, `sh1106.py`, and `wifi_utils.py` are present in `/lib` or root).
5. Run `main.py` directly from your IDE or reset the Pico W to execute automatically on boot.

---

## Testing & Verification

### 1. Sensor Verification (BME280)
- **I2C Bus Coexistence:** Verified shared 100 kHz I2C bus addressing (`0x76` for BME280, `0x3C` for SH1106) using `test_i2c_scan.py`.
- **Module Testing:** Hardware communication and data parsing were successfully verified using the standalone `test_bme280.py` script.

### 2. Fan Driver & Actuation Test
- **Driver Switching Test:** Verified reliable MOSFET switching at 3.3 V logic levels using `test_actuators.py`.
- **Hysteresis Control:** Fan turns ON when $T > T_{threshold}$ OR $RH > RH_{threshold}$, and turns OFF when both $T < T_{threshold} - \Delta T$ AND $RH < RH_{threshold} - \Delta RH$ to prevent rapid on/off oscillation.

### 3. Automated Light Control (LDR & LED Strip)
- **Logic & Hysteresis Validation:** Verified LDR voltage divider readings via ADC with a 10-sample averaging filter. Confirmed that the NeoPixel LED strip correctly toggles based on ambient light without flickering due to software hysteresis.
- **Integration Test:** Successfully validated hardware response and software logic using the dedicated `test_LightControl.py` script.

### 4. OLED Display
- **Non-blocking Updates:** Verified smooth screen refreshes without stuttering input recognition.
- **Module Testing:** Verified rendering and layout formatting using the `test_oled.py` script.

### 5. Cloud Telemetry (ThingSpeak)
- **Wi-Fi & API Connection:** Verified stable network connection and successful HTTP POST requests using the `test_tsupload.py` script.
- **Data Integrity:** Confirmed that local environmental data and actuator states (fan/light) are correctly formatted and accurately visualized on the ThingSpeak cloud dashboard.

### 6. Rotary Encoder & User Input (KY-040)
- **Module Testing:** Verified CW/CCW quadrature decoding, min/max clamping, dynamic range switching (`set_range()`), and initial 100 ms (later changed to 200 ms) IRQ button debouncing using `test_rotary.py`.

### 7. Full System Integration (`main.py`)
- **First integration test:** Button was not debounced enough (occasionally two changes were detected per click) - changed button debouncing to 200 ms
- **Second integration test:** Everything working properly, putting Pico into sleep/idle state was suggested for lower power consumption
- **Third integration test:** Low power consumption mode was added (`lowpower.py`), former `main.py` was renamed to `fullpower.py`, `main.py` only decides which mode should be used based on `LOW_POWER_MODE` variable in `settings.py`, everything working properly, [TS result](Images/ThingSpeak.png)

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

- **Project Poster:** [Link to Poster PDF](presentation/poster.pdf)
- **Demo Video:** [Video Link](https://youtube.com/...)

---

## References & Acknowledgments

- Raspberry Pi Pico W documentation: [https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
- MicroPython documentation: [https://docs.micropython.org/](https://docs.micropython.org/)
- `machine` library: [https://docs.micropython.org/en/latest/library/machine.html](https://docs.micropython.org/en/latest/library/machine.html)
- `time` library: [https://docs.micropython.org/en/latest/library/time.html](https://docs.micropython.org/en/latest/library/time.html)
- `neopixel` library: [https://docs.micropython.org/en/latest/library/neopixel.html#class-neopixel](https://docs.micropython.org/en/latest/library/neopixel.html#class-neopixel)
- `network` library: [https://docs.micropython.org/en/latest/library/network.html](https://docs.micropython.org/en/latest/library/network.html)
- `urequests` library: [https://makeblock-micropython-api.readthedocs.io/en/latest/public_library/Third-party-libraries/urequests.html](https://makeblock-micropython-api.readthedocs.io/en/latest/public_library/Third-party-libraries/urequests.html)
- Rotary Encoder Guide (CZ): [https://navody.dratek.cz/navody-k-produktum/rotacni-enkoder-ky-040.html](https://navody.dratek.cz/navody-k-produktum/rotacni-enkoder-ky-040.html)
- DE2 Course lab exercises: [BUT FEEC DE2 MicroPython Labs](https://gitlab.fekt.vut.cz/fryza/micropython-course-labs)