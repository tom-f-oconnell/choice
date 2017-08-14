#!/usr/bin/env python

from __future__ import division
import rospy
# necessary?
from std_msgs.msg import Header
from stimuli.msg import PulseSeq, Pulse, Transition, State, DefaultState
from stimuli.srv import LoadDefaultStates, LoadPulseSeq

class StimuliLoader:
    def __init__(self, default_states, trial_structure):
        # TODO run old code to generate stimuli / save
        rospy.init_node('stimuli')
        rospy.wait_for_service('load_defaults')
        rospy.wait_for_service('load_next_sequence')
        load_defaults = rospy.ServiceProxy('load_defaults', LoadDefaultStates)
        load_next_sequence = rospy.ServiceProxy('load_next_sequence', LoadPulseSeq)

        try:
            h = Header()
            h.stamp = rospy.Time.now()
            resp = load_defaults(h, default_states)
        except rospy.ServiceException as exc:
            print("Service load_defaults failed: " + str(exc))
        
        for block in trial_structure:
            if type(block) is PulseSeq:
                try:
                    block.header.stamp = rospy.Time.now()
                    resp = load_next_sequence(block)

                except rospy.ServiceException as exc:
                    print("Service load_next_sequence failed: " + str(exc))

            # TODO test
            elif type(block) is rospy.Time:
                # sleep until 2 secs before next block we need to communicate
                rospy.sleep(block - rospy.Duration(2))

            else:
                raise ValueError('unexpected type ' + str(type(block)) + ' in trial structure')

        rospy.spin()
        
# fix
if __name__ == '__main__':
    s = StimuliLoader()
