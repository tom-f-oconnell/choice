
from __future__ import print_function

import random
import datetime
import pickle

import odors
import trial_server

# TODO put in place all randomizers can use
def set_product(s1, s2):
    """
    Returns unordered "Cartesian product".
    """
    s = set()
    for e1 in s1:
        for e2 in s2:
            s.add(frozenset({e1, e2}))
    return s


def key2tupleset(dictionary, key):
    """
    Assumes dictionary values are iterables.
    """
    val = dictionary[key]
    return set(zip(len(val) * [key], val))


def nice_timestamp():
    return str(datetime.datetime.now())[:-7].replace(' ', '_').replace(':', '')


def print_nestedset(s):
    """
    Because lots of frozensets as elements of something doesn't print well.
    """
    print('{', end='')
    for fs in s:
        # convert the frozensets to sets for printing
        print(set(fs))
    print('}')

###############################################################################

# TODO do i ever want to train the same flies on different pairs of odors sequentially?
# or maybe expose them to some odors / some sequence of odors first (/ after?)?

save_mappings = True
communicate_to_arduino = False

'''
odor_panel = {'2-butanone': (-4, -6, -8),
              'trans-2-hexenal': (-5, -6, -8, -10),
              'pentyl acetate': (-3,),
              'pentanoic acid': (-2, -3, -4),
              'parafin (mock)': (0,)}
'''
# TODO store as effective dilution given flow conditions / mixing ratios?
odor_panel = {'parafin (mock)': (0,),
              '4-methylcyclohexanol': (-2,),
              '3-octanol': (-2,)}

# TODO left pins & right pins separately?

# 5 through 11 inclusive
available_pins = tuple(range(5,12))

# TODO break this into a function?
mock = ('parafin (mock)', 0)

# TODO TODO consolidate these kind of parameters and move off arduino
# for each odor combination we will test
repeats = 5 # 5
# TODO check that it was / still is 45
secs_per_repeat = 45  # seconds

all_mappings = []
odors2pins = []
all_stimuli_in_order = []

# TODO TODO how to deal w/ symmetry re: sides? (blocks pick a random side to start on?)

# TODO for now, just save sides to a separate file to be loaded by that ROS node

###############################################################################
# TODO
odors = list(odors_panel)
random.shuffle(odors)

# TODO
# randomly break stimuli into groups fitting into the number of 
# valves we have on the rig
# ***if odors are ever to be mixed, need to be connected simultaneously***

# assign them to random pins / ports
# needs |pins| <= |odors|
# (samples without replacement)
# TODO maybe keep pin -> odor assignments for a few neighboring sets of experiments?
# if the total time a fly is in there will be short...
pins = random.sample(available_pins, len(odors))

for pin, odor_pair in sorted(zip(pins, odors), key=lambda x: x[0]):
    odor = odors.pair2str(odor_pair)
    print(str(pin) + ' -> ' + odor)

odors2pins.append(dict(zip(odors, pins)))
# TODO delete me? replace w/ odors2pins where necessary.
all_mappings.append(list(zip(pins, odors)))

# now determine order in which to present combinations of the connected
# odors
to_present = list(odors)
random.shuffle(to_present)
expanded = []
for e in to_present:
    expanded += [e] * repeats
expanded = [set(e) for e in expanded]

all_stimuli_in_order.append(expanded)
###############################################################################

total_secs = sum(map(lambda x: len(x), all_stimuli_in_order)) * secs_per_repeat
m, s = divmod(total_secs, 60)
h, m = divmod(m, 60)
print(h, 'hours', m, 'minutes', s, 'seconds')

# TODO compare w/ decoding saved all_stimuli_in_order
# and then possibly skip decoding

# TODO make if not there. warn if cant.
output_dir = '.'

if save_mappings:
    filename = output_dir + nice_timestamp() + '.p'
    print(filename)
    with open(filename, 'wb') as f:
        pickle.dump((all_mappings, all_stimuli_in_order), f)
else:
    print('NOT SAVING MAPPINGS!!!')
    
required_pins_in_order = []
for block in range(len(all_stimuli_in_order)):
    order = []
    for mixture in all_stimuli_in_order[block]:
        order.append({odors2pins[block][o] for o in mixture})
    required_pins_in_order.append(order)
    
# so that i can break the communication out into another script if i want to
with open('.pinorder.tmp.p', 'wb') as f:
    pickle.dump((required_pins_in_order, all_mappings), f)
    
###############################################################

with open('.pinorder.tmp.p', 'rb') as f:
    required_pins_in_order, all_mappings = pickle.load(f)
    
# TODO detect where arduino is 
# (and which, based on whatever hardware ID info is available)
# maybe upload some handshaking / id code
if communicate_to_arduino:
    # TODO set timing (and other) params in ROS eventually
    trial_server.start(required_pins_in_order, port='COM14', mappings=all_mappings)

