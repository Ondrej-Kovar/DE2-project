"""
Entry point for the Smart Greenhouse System (DE2 Project).

Reads LOW_POWER_MODE from settings.py and delegates to the appropriate loop:
  LOW_POWER_MODE = False  →  main_fullpower.py  (classic superloop, ~60–80 mA)
  LOW_POWER_MODE = True   →  main_lowpower.py   (lightsleep loop,   ~40–55 mA)

Authors: Richard Kralovsky, Ondrej Kovar, Adam Koutny

History
26.11.2026  Refactored into dispatcher + main_fullpower.py + main_lowpower.py.
"""
import settings as config

if config.LOW_POWER_MODE:
    from main_lowpower import main
else:
    from main_fullpower import main

main()
