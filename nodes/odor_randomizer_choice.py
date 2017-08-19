#!/usr/bin/env python

from __future__ import print_function

import random
import datetime
import time
import pickle

import rospy
from std_msgs.msg import Header
from stimuli.msg import PulseSeq, Pulse, Transition, State, DefaultState
from stimuli_loader import StimuliLoader

# TODO do i ever want to train the same flies on different pairs of odors sequentially?
# or maybe expose them to some odors / some sequence of odors first (/ after?)?

rospy.init_node('stimuli')

save_stimulus_info = False

# TODO store as effective dilution given flow conditions / mixing ratios?
'''
odor_panel = {'parafin (mock)': (0,),
              '4-methylcyclohexanol': (-2,),
              '3-octanol': (-2,)}
'''
'''
odor_panel = {'4-methylcyclohexanol': (-2,),
              '3-octanol': (-2,)}

# TODO left pins & right pins separately?

# TODO break this into a function?
'''
reinforced_odor_side_order = rospy.get_param('olf/reinforced_odor_side_order')

training_blocks = rospy.get_param('olf/training_blocks')
prestimulus_delay_s = rospy.get_param('olf/prestimulus_delay_s')
test_duration_s = rospy.get_param('olf/test_duration_s')
pretest_to_train_s = rospy.get_param('olf/pretest_to_train_s')
train_duration_s = rospy.get_param('olf/train_duration_s')
inter_train_interval_s = rospy.get_param('olf/inter_train_interval_s')
train_to_posttest_s = rospy.get_param('olf/train_to_posttest_s')
beyond_posttest_s = rospy.get_param('olf/beyond_posttest_s')

left_pins = rospy.get_param('olf/left_pins')
right_pins = rospy.get_param('olf/right_pins')
separate_balances = rospy.get_param('olf/separate_balances')
left_balance = rospy.get_param('olf/left_balance')
right_balance = rospy.get_param('olf/right_balance')
balance_normally_flowing = rospy.get_param('olf/balance_normally_flowing')

shock_ms_on = rospy.get_param('zap/shock_ms_on')
shock_ms_off = rospy.get_param('zap/shock_ms_off')

left_shock = rospy.get_param('zap/left')
right_shock = rospy.get_param('zap/right')

# TODO TODO how to deal w/ symmetry re: sides? (blocks pick a random side to start on?)

# TODO for now, just save sides to a separate file to be loaded by that ROS node

###############################################################################
#odors = list(odor_panel)
mock = ('parafin (mock)', 0)
odors = [('4-methylcyclohexanol', -2), ('3-octanol', -2)]
reinforced, unreinforced = random.sample(odors, 2)
odors.append(mock)

# TODO
# randomly break stimuli into groups fitting into the number of 
# valves we have on the rig
# ***if odors are ever to be mixed, need to be connected simultaneously***

# assign them to random pins / ports
# needs |pins| <= |odors|
# (samples without replacement)
# TODO maybe keep pin -> odor assignments for a few neighboring sets of experiments?
# if the total time a fly is in there will be short...
# TODO republish / set?
left_pins = random.sample(left_pins, len(odors))
right_pins = random.sample(right_pins, len(odors))

for pin, odor_pair in sorted(zip(left_pins, odors), key=lambda x: x[0]):
    print(str(pin) + ' -> ' + str(odor_pair))

for pin, odor_pair in sorted(zip(right_pins, odors), key=lambda x: x[0]):
    print(str(pin) + ' -> ' + str(odor_pair))

# TODO republish / set?
odors2left_pins = dict(zip(odors, left_pins))
odors2right_pins = dict(zip(odors, right_pins))

# TODO pause until person has connected stuff?

###############################################################################

class StimuliGenerator:
    def __init__(self):
        self.current_t0 = rospy.Time.now()

        # only do this for 'alternating' mode?
        self.current_side_is_left = random.choice([True, False])

    # currently just on all the time. maybe i want something else?
    def odor_transitions(self):
        """
        TODO
        """
        # TODO need to deep copy these?
        # setting ms_on to 1 to emphasize duration is determined by end time set in PulseSeq
        # and the pin will only go low if that is the DefaultState for the pin
        high = State(ms_on=1, ms_off=0)
        # don't need explicit low transition because default state is low
        # but end time in PulseSeq messsage must be set correctly
        transition = [Transition(self.current_t0, high)]

        pulse_seq = []
        if separate_balances:
            balance_pins = [left_balance, right_balance]

            if balance_normally_flowing:
                balance_transition = transition
            else:
                low = State(ms_on=0, ms_off=1)
                balance_transition = [Transition(self.current_t0, low)]

            for p in balance_pins:
                pulse_seq.append(Pulse(p, balance_transition))

        if self.current_side_is_left:
            pins = [odors2left_pins[reinforced], odors2right_pins[unreinforced]]
        else:
            pins = [odors2left_pins[unreinforced], odors2right_pins[reinforced]]

        for p in pins:
            pulse_seq.append(Pulse(p, transition))

        return pulse_seq


    # TODO how to handle shocking + presenting reinforced odor on both sides?
    def shock_transitions(self):
        """
        TODO
        """
        square_wave = State(ms_on=shock_ms_on, ms_off=shock_ms_off)
        transition = [Transition(self.current_t0, square_wave)]

        # TODO 'left' / r / 'both'?
        if self.current_side_is_left:
            return [Pulse(left_shock, transition)]
        else:
            return [Pulse(right_shock, transition)]


    def test(self):
        # TODO will need to add header.stamp before sending
        header = Header()

        start = self.current_t0
        end = start + rospy.Duration(test_duration_s)
        self.current_t0 = end

        pulse_seq = self.odor_transitions()
        if reinforced_odor_side_order == 'alternating':
            self.current_side_is_left = not self.current_side_is_left 

        elif reinforced_odor_side_order == 'random':
            self.current_side_is_left = random.choice([True, False])

        # TODO add shock and balance pins
        pins_to_signal = []
        return PulseSeq(header, start, end, pulse_seq, pins_to_signal)


    def train(self):
        # TODO will need to add header.stamp before sending
        header = Header()

        start = self.current_t0
        end = start + rospy.Duration(train_duration_s)

        pulse_seq = self.odor_transitions() + self.shock_transitions()
        if reinforced_odor_side_order == 'alternating':
            self.current_side_is_left = not self.current_side_is_left 

        elif reinforced_odor_side_order == 'random':
            self.current_side_is_left = random.choice([True, False])

        self.current_t0 = end

        # TODO add shock and balance pins
        pins_to_signal = []
        return PulseSeq(header, start, end, pulse_seq, pins_to_signal)


    def delay(self, delay_s):
        ros_delay = rospy.Duration(delay_s)
        self.current_t0 = self.current_t0 + ros_delay
        # do we have a copy constructor?
        return rospy.Time.from_sec(self.current_t0.to_sec())

flatten = lambda l: [item for sublist in l for item in sublist]

# TODO fix train + delay line
gen = StimuliGenerator()
trial_structure = [gen.delay(prestimulus_delay_s), \
                   gen.test(), \
                   gen.delay(pretest_to_train_s)] + \
                  flatten([[f(), gen.delay(inter_train_interval_s)] for f in [gen.train] * training_blocks]) + \
                  [gen.delay(train_to_posttest_s), \
                   gen.test(), \
                   gen.delay(beyond_posttest_s)]

#print(trial_structure)

low_pins = left_pins + right_pins + [left_shock, right_shock]
if separate_balances:
    if balance_normally_flowing:
        low_pins += [left_balance, right_balance]
        high_pins = []
    else:
        high_pins = [left_balance, right_balance]

default_states = [DefaultState(p, True) for p in high_pins] + \
                 [DefaultState(p, False) for p in low_pins]

# TODO make sure this node stays alive until the current_t0 after the trial structure has been
# evaluated

###############################################################################

# print trial structure?

# can i do this from outside of a node?
rospy.loginfo('Stimuli should finish at ' + datetime.datetime.fromtimestamp(gen.current_t0.to_sec()\
        ).strftime('%Y-%m-%d %H:%M:%S'))

# TODO compare w/ decoding saved all_stimuli_in_order
# and then possibly skip decoding

# TODO make if not there. warn if cant.
output_dir = '.'

if save_stimulus_info:
    # TODO get rid of multi_tracker prefix
    experiment_basename = rospy.get_param('multi_tracker/experiment_basename', None)
    if experiment_basename is None:
        experiment_basename = time.strftime("%Y%m%d_%H%M%S_N1", time.localtime())
        rospy.set_param('multi_tracker/experiment_basename', experiment_basename)

    filename = output_dir + experiment_basename + '_stimuli.p'
    rospy.loginfo('Trying to save save stimulus info to ' + filename)

    # TODO check / test success
    with open(filename, 'wb') as f:
        # TODO test trial_structure is recoverable from pickle / serializable
        pickle.dump((odors2left_pins, odors2right_pins, default_states, trial_structure), f)
else:
    rospy.logwarn('Not saving generated trial structure / pin to odor mappings!')

stimuli_loader = StimuliLoader(default_states, trial_structure)

