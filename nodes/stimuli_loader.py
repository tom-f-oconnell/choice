#!/usr/bin/env python

from __future__ import division
import rospy
import time
import datetime
# necessary?
from std_msgs.msg import Header
from stimuli.msg import PulseSeq, Pulse, Transition, State, DefaultState
from stimuli.srv import LoadDefaultStates, LoadPulseSeq

class StimuliLoader:
    def __init__(self, default_states, trial_structure):
        rospy.loginfo('stimuli_loader waiting for services')
        defaults_service_name = 'load_defaults'
        sequence_service_name = 'load_next_sequence'
        rospy.wait_for_service(defaults_service_name)
        rospy.wait_for_service(sequence_service_name)
        load_defaults = rospy.ServiceProxy(defaults_service_name, LoadDefaultStates)
        load_next_sequence = rospy.ServiceProxy(sequence_service_name, LoadPulseSeq)

        rospy.loginfo('stimuli_loader sending default states')
        try:
            h = Header()
            h.stamp = rospy.Time.now()
            resp = load_defaults(h, default_states)
        except rospy.ServiceException as exc:
            rospy.logerr("Service load_defaults failed: " + str(exc))
        rospy.loginfo('stimuli_loader finished sending default states')
        
        for block in trial_structure:
            if type(block) is PulseSeq:
                rospy.loginfo('stimuli_loader sending block info')
                try:
                    #print(block)
                    #print(block.pulse_seq)
                    block.header.stamp = rospy.Time.now()
                    resp = load_next_sequence(block)
                    rospy.logwarn('sent block info!')

                except rospy.ServiceException as exc:
                    rospy.logerr("Service load_next_sequence failed: " + str(exc))
                rospy.loginfo('stimuli_loader finished sending')

            # TODO test
            elif type(block) is rospy.Time:
                intertrial_interval_end = block
                wake_at = intertrial_interval_end - rospy.Duration(2)
                rospy.loginfo('stimuli_loader sleeping until ' + \
                    datetime.datetime.fromtimestamp(wake_at.to_sec()).strftime('%Y-%m-%d %H:%M:%S'))

                # sleep until 2 secs before next block we need to communicate
                until_wake = wake_at - rospy.Time.now()
                rospy.sleep(until_wake)

            else:
                # TODO was this error getting supressed? logerr?
                # seems a list was in here
                raise ValueError('unexpected type ' + str(type(block)) + ' in trial structure')

        rospy.spin()
        
# fix
if __name__ == '__main__':
    s = StimuliLoader()
