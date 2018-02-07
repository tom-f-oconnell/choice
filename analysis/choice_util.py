#!/usr/bin/env python

"""
Functions to load, analyze, and plot data from experiments run with other code
in this repository.
"""

import rosbag
import numpy as np
import pandas as pd

def load_voltages(bagfile_path):
    """
    Returns a 'tidy' pandas.DataFrame with columns ('channel', 'time',
    'voltage').

    Ranges:
    -channel: 0-15
    -voltage: raw 10-bit ADC readings from Arduino. May be limited to <5v by
     amplifier and overvoltage protection circuitry.
    -time: starts at 0. TODO may want to keep Unix time to better compare to
     events in trial...
    """
    bag = rosbag.Bag(bagfile_path)
    channels = dict()
    n_msgs = 0

    for topic, msg, t in \
        bag.read_messages(topics=['channel_measurements_stamped']):

        if not msg.channel in channels:
            channels[msg.channel] = dict()
            channels[msg.channel]['times'] = []
            channels[msg.channel]['voltages'] = []
            
        else:
            channels[msg.channel]['times'].append(msg.stamp.to_sec())
            channels[msg.channel]['voltages'].append(msg.measurement)

        # TODO why is length of first axis of concatenated result less than
        # # of messages processed by some small amount?
        n_msgs += 1
    print('Processed {} messages.'.format(n_msgs))

    channel_dfs = []
    # TODO i wonder what the idiomatic way to build a df like this would be...
    for c in channels:
        channels[c]['times'] = np.array(channels[c]['times'])
        channels[c]['voltages'] = np.array(channels[c]['voltages'])
        channels[c]['channel'] = np.ones(len(channels[c]['times'])) * c

        channel_df = pd.DataFrame(channels[c])
        channel_dfs.append(channel_df)

        # TODO del from dict to save memory
    df = pd.concat(channel_dfs)
    return df
