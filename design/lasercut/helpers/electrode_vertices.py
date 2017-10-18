#!/usr/bin/env python

from __future__ import division
import numpy as np

# all units in mm unless otherwise noted
center_x = 0.0
center_y = 38.7450
# maybe a little less?
min_half_length = 28
min_width = 6.5
between_electrodes = 1
electrode_width = 1


curr_x = center_x + (between_electrodes / 2.0)
points = []

while curr_x < min_half_length:


