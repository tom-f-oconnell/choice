#!/usr/bin/env python

from __future__ import division
# TODO dont need manifest do I? service example has it
import rospy

# if this might somehow work outside of ros, maybe try to sort
# out ROS portions from core functions?

# TODO use two instances of same code for shock and odor
# delivery?

class Shocks:
    def __init__(self):
        # TODO run old code to generate stimuli / save
        rospy.init_node('shocks')
        rospy.Service('get_next_stiminfo', StimInfo, self.send_arduino_stiminfo)

        rospy.spin()
        
    def send_arduino_stiminfo(self, req):
        # are <SrvName>Response types created automatically?
        # (there is no TestResponse in rosserial_arduino.srv,
        # see rosserial_arduino examples)
        si = StimInfoRequest()
        # TODO
        si.output = []
        return si
        

if __name__ == '__main__':
    s = Shocks()
