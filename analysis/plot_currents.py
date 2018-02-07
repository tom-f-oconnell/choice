#!/usr/bin/env python

"""
Plots currents recorded to a ROS bagfile in the choice/ChannelMeasurementStamped
message type. These messages are published in the
channel_measurement_splitter.py node, which reformats the
choice/ChannelMeasurementMicros messages published from the Arduino, via the
rosserial_python interface.
"""

from __future__ import print_function

import sys
import choice_util
import matplotlib.pyplot as plt
import seaborn as sns

if len(sys.argv) != 2:
    print("Usage: must path one path to a bagfile to load currents from.")

# times and currents both (n_channels x n_timepoints)
# 'tidy' data with columns ['channel', 'time', 'voltage']
df = choice_util.load_voltages(sys.argv[1])

sns.set_style('dark')

# TODO
# -maybe just get regions where there should have been shocks
#   -and why does the signal not seem to match shock duty cycle I set?
# -maybe compare left and right (should only be a fly in one in vast majority of
# cases
# -try to predict whether fly will learn from voltages (even if messy)
# -compare to no fly / no cable trials
# -record w/ voltmeter / scope / DAQ @ cable output?
g = sns.FacetGrid(df, col='channel')
g.map(plt.plot, 'times', 'voltages')
plt.show()

