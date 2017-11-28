#!/usr/bin/env python

from __future__ import division
import numpy as np

"""
Measured with 100V from power supply across fly, then across 100K 0.1% resistor.

Measured with two flies loaded, but generally just one making contact at a time.
Contacts were bridged to just have one high voltage grid and one low(er).

Voltage across resistor measured with oscilloscope of 1M input impedance (Assumed to be 
purely resistive, which I think is reasonable. They list input capacitance as well.)

Room temperature and low room humidity (despite often using humidity in experiments)

Ignoring burden voltage caused by 1M input resistance b/c it should be negligible.
"""

# 200 mV
approx_median_volts_with_fly_walking = 0.2

"""
V_in = 100V
R_shunt = 100K
V_out ~= 0.2V

Voltage divider equation
V_out = V_in * R_shunt / (R_shunt + R_fly)

V_out * R_shunt + V_out * R_fly = V_in * R_shunt
V_out * R_fly = V_in * R_shunt - V_out * R_shunt
R_fly = (V_in * R_shunt - V_out * R_shunt) / V_out

"""

V_in = 100
V_out = 0.2
R_shunt = 1e5
R_fly = (V_in * R_shunt - V_out * R_shunt) / V_out

print R_fly
