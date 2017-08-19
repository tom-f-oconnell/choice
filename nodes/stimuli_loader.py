#!/usr/bin/env python

from __future__ import division
from __future__ import print_function
import rospy
import time
import datetime
# necessary?
from std_msgs.msg import Header
from stimuli.msg import PulseSeq, Pulse, Transition, State, DefaultState
from stimuli.srv import LoadDefaultStates, LoadPulseSeq

def readable_rostime(ros_time):
    return datetime.datetime.fromtimestamp(ros_time.to_sec()).strftime('%Y-%m-%d %H:%M:%S')

class StimuliLoader:
    # TODO TODO assert that time to sleep before is less than all intertrial intervals
    def __init__(self, default_states, trial_structure):
        self.pin2name = dict(zip(range(54, 70), ['A' + str(i) for i in range(16)]))
        rospy.loginfo('stimuli_loader waiting for services')
        defaults_service_name = 'load_defaults'
        sequence_service_name = 'load_seq'
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
                    # TODO any way to print in here whether it is a test / train and side, etc?
                    block.header.stamp = rospy.Time.now()
                    resp = load_next_sequence(block)
                    rospy.logwarn('sent block info!')
                    
                    rospy.loginfo('current time is ' + readable_rostime(rospy.Time.now()))
                    rospy.loginfo('should start at ' + readable_rostime(block.start))
                    rospy.loginfo('should end at ' + readable_rostime(block.end))
                    rospy.loginfo('duration of sequence ' + str((block.end - block.start).to_sec()))
                    rospy.loginfo('using pins: ' + str([self.pin2name[pulse.pin] if pulse.pin in self.pin2name else pulse.pin for pulse in block.pulse_seq]))

                except rospy.ServiceException as exc:
                    rospy.logerr("Service load_next_sequence failed: " + str(exc))

            # TODO test
            elif type(block) is rospy.Time:
                intertrial_interval_end = block
                # TODO how to not write when arduino is in a busy state / rewrite if necessary
                # should i just switch the arduino to a client?
                wake_at = intertrial_interval_end - rospy.Duration(10)
                rospy.loginfo('stimuli_loader sleeping until ' + readable_rostime(wake_at))

                # sleep until N secs before next block we need to communicate
                until_wake = (wake_at - rospy.Time.now()).to_sec()
                rospy.sleep(max(0.0, until_wake))

            else:
                # TODO was this error getting supressed? logerr?
                # seems a list was in here
                raise ValueError('unexpected type ' + str(type(block)) + ' in trial structure')

        rospy.spin()
        
# fix
if __name__ == '__main__':
    s = StimuliLoader()
