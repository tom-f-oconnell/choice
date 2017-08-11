#!/usr/bin/env python

from __future__ import division
import rospy

class Stimuli:
    def __init__(self):
        # TODO run old code to generate stimuli / save
        rospy.init_node('stimuli')
        rospy.Service('get_next_stiminfo', StimInfo, self.send_arduino_stiminfo)

        rospy.spin()
        
    def send_arduino_stiminfo(self, req):
        # are <SrvName>Response types created automatically?
        # (there is no TestResponse in rosserial_arduino.srv,
        # see rosserial_arduino examples)
        
        return StimInfoRequest()
        

if __name__ == '__main__':
    s = Shocks()
