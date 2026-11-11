.. Smart Greenhouse Monitor documentation master file

Welcome to Smart Greenhouse Monitor's documentation!
===================================================

The **Smart Greenhouse Monitor** is an embedded system prototype based on the **Raspberry Pi Pico W** running MicroPython. It monitors environmental parameters (temperature, humidity, atmospheric pressure, and ambient light), controls ventilation and artificial plant lighting, and provides an interactive local OLED user interface.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   hardware
   api

Overview
========
Developed for the **Digital Electronics 2 (DE2)** course at **Brno University of Technology (BUT)**, Faculty of Electrical Engineering and Communication (FEEC).

Authors:
- Adam Koutný
- Ondřej Kovář
- Richard Královský

Hardware Architecture
=====================
- Microcontroller: Raspberry Pi Pico W (RP2040)
- Sensors: BME280 (I2C), Photoresistor LDR (ADC0)
- Actuators: 12V Ventilation Fan (MOSFET), 5V LED Strip (MOSFET), Status RGB LED
- Display: 1.3" OLED (SH1106 via I2C)
- Input: Rotary Encoder (KY-040 with push-button)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
