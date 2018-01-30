#!/usr/bin/env python

"""
Splits the channel_measurement field in the choice/ChannelMeasurementMicros type
into a (6-bit) channel and a (10-bit) measurement type, and republishes.
"""

from __future__ import print_function
from __future__ import division

import rospy
from choice.msg import ChannelMeasurementMicros
from choice.msg import ChannelMeasurementStamped

class ChannelMeasurementSplitter:
    def __init__(self):
        rospy.init_node('channel_measurement_splitter')
        rospy.Subscriber('channel_measurements', ChannelMeasurementMicros, \
            self.cm_callback)
        self.pub = rospy.Publisher('channel_measurements_stamped', \
            ChannelMeasurementStamped)
        # defined in multishock.hpp
        self.measurement_mask = 0x3FF
        self.measurement_bits = 10
        rospy.spin()

    def cm_callback(self, cmm):
        cms = ChannelMeasurementStamped()
        # TODO fix. approximation (will always be after actual time, probably by
        # order hundreds of microseconds to single milliseconds)
        cms.stamp = rospy.Time.now()
        # TODO maybe call c functions defined in multishock.cpp directly
        cms.channel = cmm.channel_measurement >> self.measurement_bits
        cms.measurement = cmm.channel_measurement & self.measurement_mask
        self.pub.publish(cms)


if __name__ == '__main__':
    try:
        ChannelMeasurementSplitter()
    # TODO why was this not in the listener example code? need it?
    except rospy.ROSInterruptException:
        pass
