#!/usr/bin/env python

from __future__ import division
import numpy as np
import pandas as pd
# TODO figure out what the hold up is on importing this, with the prints
import multi_tracker_analysis as mta
import glob
from os.path import join
import re
import pickle
from stimuli.srv import LoadSequenceRequest
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
# TODO maybe remove this dependency if it means it cant be run easily on windows?
import rosparam

import ipdb

make_plots = False

# was it set_style?
sns.set()

# TODO have these parameters save correctly
left_shock = 6
right_shock = 5

def load_metadata(d):
    files = glob.glob(join(d, '*_stimuli.p'))
    if len(files) > 1:
        raise IOError('too many stimulus files in ' + d)
    elif len(files) < 1:
        raise IOError('found no stimulus files in ' + d)
    filename = files[0]
    with open(filename, 'rb') as f:
        # TODO it seems like pins2odors would really be more useful?
        odors2left_pins, odors2right_pins, _, trial_structure = pickle.load(f)
    odors2pins = dict()
    odors2pins.update(odors2left_pins)
    odors2pins.update(odors2right_pins)
    times = dict()
    # TODO convert to double here?
    # TODO also display period before?
    # TODO is this to seconds from epoch?
    times['start'] = trial_structure[0].to_sec()
    times['end'] = trial_structure[-1].to_sec()
    stimuli = filter(lambda x: type(x) is LoadSequenceRequest, trial_structure)
    times['pretest_start'] = stimuli[0].seq.start.to_sec()
    times['posttest_start'] = stimuli[-1].seq.start.to_sec()
    times['test_duration'] = stimuli[0].seq.end.to_sec() - stimuli[0].seq.start.to_sec()
    # TODO fix parameter saving so stimulus parameters are also recorded (e.g. which pins are left)
    left_pins = [56, 57, 59]
    right_pins = [54, 55, 61]
    pretest_left_pin = [p for p in stimuli[0].seq.pins if p in left_pins][0]
    pretest_left_odor = [o for o, p in odors2pins.items() if p == pretest_left_pin]
    posttest_left_pin = [p for p in stimuli[-1].seq.pins if p in left_pins][0]
    posttest_left_odor = [o for o, p in odors2pins.items() if p == posttest_left_pin]
    # TODO check that all blocks would yield the same answer
    for block in stimuli[1:-1]:
        odors = []
        if left_shock in block.seq.pins:
            odors += [o for o, p in odors2pins.items() if p in left_pins and p in block.seq.pins]
        if right_shock in block.seq.pins:
            odors += [o for o, p in odors2pins.items() if p in right_pins and p in block.seq.pins]
        if len(odors) > 0:
            assert len(odors) == 1
            reinforced_odor = odors[0]
            break
    # TODO associate with negative / positive on appropriate x / y axis
    #side2odor = dict()
    #side2odor_index['down'] = 
    #return times, trial_structure
    metadata = dict()
    metadata['times'] = times
    # TODO maybe don't need these?
    metadata['pretest_left_odor'] = pretest_left_odor
    metadata['posttest_left_odor'] = posttest_left_odor
    metadata['reinforced_odor'] = reinforced_odor
    metadata['stimuli'] = list(stimuli)
    left_pins2odors = dict((v, k) for k, v in odors2left_pins.items())
    right_pins2odors = dict((v, k) for k, v in odors2right_pins.items())

    assert len(left_pins2odors) == len(odors2left_pins), 'some odors map to multiple left pins'
    assert len(right_pins2odors) == len(odors2right_pins), 'some odors map to multiple right pins'

    for p in left_pins2odors.keys():
        assert not p in right_pins2odors.keys(), 'pin ' + str(p) + \
            ' was listed as both left and right'
    for p in right_pins2odors.keys():
        assert not p in left_pins2odors.keys(), 'pin ' + str(p) + \
            ' was listed as both left and right'

    metadata['left_pins2odors'] = left_pins2odors
    metadata['right_pins2odors'] = right_pins2odors
    metadata['odors'] = set(odors2pins.keys())
    return metadata

# TODO include list of known good trials to use. derive from inspecting tracking.

fps = 30.0

# TODO allow script to be run in directory w/ data
path = '/home/tom/data/retracked'
# TODO just walk from path in future?
# or glob on date here and glob separately below?
dirs = ['20170913_104724', '20170913_105853', '20170913_112951']

curr_fly = 0
fly2data = dict()
fly2meta = dict()
all_odors = set()

for d in map(lambda x: join(path, x), dirs):
    # TODO check trial structure times against those in log
    common_metadata = load_metadata(d)
    for o in common_metadata['odors']:
        all_odors.add(o)

    # TODO can join take a variable # of args?
    for f in glob.glob(join(d, '*.hdf5')):
        metadata = dict(common_metadata)
        # TODO make it so this generates the (optional) config? notify if doing so
        # TODO TODO exclude trajectories that don't cover enough ground
        data, _ = mta.read_hdf5_file_to_pandas.load_and_preprocess_data(f)
        print 'position_x range', data['position_x'].min(), data['position_x'].max()
        print 'position_y range', data['position_y'].min(), data['position_y'].max()
        fly2data[curr_fly] = data
        metadata['dir'] = d
        match = re.search('_N([0-9])_', f)
        # TODO why is it more than what is in the parens?
        #print 'MATCH', match
        metadata['n'] = int(match.group(0)[2:-1])
        roi_points = rosparam.load_file(join(d, 'roi_N' + str(metadata['n']) + \
            '.yaml'))[0][0]['roi_points']
        metadata['roi_points'] = roi_points
        fly2meta[curr_fly] = metadata
        curr_fly += 1

# how to use this if not a cmap?
#cmap = sns.color_palette('husl', len(all_odors), l=0.3, s=0.8, as_cmap=True)
# TODO have fallback in case as_cmap isn't available
cmap = sns.color_palette('husl', len(all_odors))
#sns.hls_palette(len(all_odors), l=0.3, s=0.8)

odor2color = dict()
for o, c in zip(all_odors, cmap):
    odor2color[o] = c

# TODO don't necessarily average across trials (because arena is repositioned wrt camera)
# TODO just load rois and take middle of that? (assumes you click evenly far away on both sides...)
y_max = max([data['position_y'].max() for data in fly2data.values()])
y_min = min([data['position_y'][data['position_y'] > 1].min() for data in fly2data.values() \
    if np.sum(data['position_y'] > 1) > 0])
print 'overall y_max', y_max
print 'overall y_min', y_min

# TODO divide into mch and oct? make a dataframe including all variables (like side, etc)?
percent_reinforced_pre = []
percent_reinforced_post = []

crop_to_seconds = 1100

# TODO TODO line up images of ROIs, with drawn midline, to check for those errors
# TODO one y value range for all plots

# TODO legends for odors and shock patch. label / group by the reinforced odor?
for fly, data in fly2data.items():
    if make_plots:
        plt.figure()
        plt.title(fly2meta[fly]['dir'] + ' ' + str(fly2meta[fly]['n']))
        plt.xlabel('Seconds')
    # TODO what happens to missing data?
    # plotted as zero? not plotted?
    curr_times = (data['time_epoch_secs'] + data['time_epoch_nsecs'] / 1e9).as_matrix()
    # TODO so does floris initialize something to 5000? blocks written in that size?
    #print(curr_times.shape)
    nonzero_times = curr_times.nonzero()[0]
    if nonzero_times.size == 0:
        print 'SKIPPING FLY ', fly2meta[fly]['n'], 'FROM', fly2meta[fly]['dir']
        continue
    start = curr_times[nonzero_times].min()
    print 'START TIME =', start
    #ipdb.set_trace()

    # because for some of these, the tracking ran much longer than the stimulus presentation
    cropped_indices = (curr_times - start) <= crop_to_seconds
    cropped_times = curr_times[cropped_indices]
    # relative to start of experiment
    cropped_rel_times = cropped_times - start
    if make_plots:
        plt.plot(cropped_rel_times , data['position_y'][cropped_indices])

    # calculate percent time in each odor region
    # TODO make one variable at top which controls which dimension to use as long axis
    # and have this (and elsewhere) depend on that
    mid = np.mean(map(lambda x: x[1], fly2meta[fly]['roi_points']))
    print 'using y midline', mid
    left = data['position_y'][cropped_indices] > mid
    pretest_indices = np.logical_and(cropped_times > fly2meta[fly]['times']['pretest_start'], \
        cropped_times < (fly2meta[fly]['times']['pretest_start'] + \
        fly2meta[fly]['times']['test_duration']))

    posttest_indices = np.logical_and(cropped_times > fly2meta[fly]['times']['posttest_start'], \
        cropped_times < (fly2meta[fly]['times']['posttest_start'] + \
        fly2meta[fly]['times']['test_duration']))
    # patch in those indices, also representing which odor is on each side
    # first argument is lower left corner of rectangle

    y_bord = 10
    y_shock_to_odor = 10
    large_height = (y_max - y_min) / 2 + y_bord
    small_height = 20
    odor_patch_alpha = 0.4
    shock_patch_alpha = 1
    shock_color = 'red'
    # TODO TODO center all plots about mid point. set origin for all to midpoint?

    meta = fly2meta[fly]
    for s in meta['stimuli']:
        width = (s.seq.end - s.seq.start).to_sec()
        for p in s.seq.pins:
            # TODO fix fact that some x values for patches (and maybe other things?)
            # are way off (i.e. still in unix epoch time)
            if p is left_shock:
                color = shock_color
                height = small_height
                y0 = y_min - y_bord - (y_shock_to_odor + small_height)
                alpha = shock_patch_alpha

            elif p is right_shock:
                color = shock_color
                height = small_height
                y0 = y_max + y_bord + y_shock_to_odor
                alpha = shock_patch_alpha

            # TODO TODO dont use y_min and y_max from across all flies / placements here
            elif p in meta['left_pins2odors']:
                print 'left odor', meta['left_pins2odors'][p]
                color = odor2color[meta['left_pins2odors'][p]]
                # TODO check
                y0 = y_min - y_bord
                height = large_height
                alpha = odor_patch_alpha

            elif p in meta['right_pins2odors']:
                print 'right odor', meta['right_pins2odors'][p]
                color = odor2color[meta['right_pins2odors'][p]]
                # TODO check
                y0 = mid
                height = large_height
                alpha = odor_patch_alpha

            else:
                print 'skipping pin', p
                continue

            # TODO maybe subdivide for shocks? (to reflect actual pulse cycle ~2.5s on/off)
            x0 = s.seq.start.to_sec() - start
            assert x0 > 0, 'times we want to disply should not be negative. was ' + str(x0)
            assert x0 + width < crop_to_seconds, 'last time index of patched region should fall ' + \
                'within limits of cropped experiment. was ' + str(x0)
            print 'patching pin', p, 'from', (x0, y0), 'with w=', width, 'and h=', height
            if make_plots:
                p = patches.Rectangle((x0, y0), width, height, alpha=alpha, \
                    facecolor=color, edgecolor=color)
                ax = plt.gca()
                ax.add_patch(p)
    
    # patch indications of which sides are shocked, and when

    # TODO include a buffer region that is called in neither direction to make this more robust to 
    # misspecifying the middle of the arena?
    percent_left_pre = np.sum(left[pretest_indices]) / pretest_indices.size
    if meta['reinforced_odor'] == meta['pretest_left_odor']:
        percent_reinforced_pre.append(percent_left_pre)
    else:
        percent_reinforced_pre.append(1 - percent_left_pre)

    percent_left_post = np.sum(left[posttest_indices]) / posttest_indices.size
    if meta['reinforced_odor'] == meta['posttest_left_odor']:
        percent_reinforced_post.append(percent_left_post)
    else:
        percent_reinforced_post.append(1 - percent_left_post)

if make_plots:
    plt.figure()
    plt.title('Percent on side w/ reinforced odor')
    axes = plt.gca()
    axes.set_xlim([-.2, 1.2])
    axes.set_ylim([0, 1])

    x = [0, 1]
    for pre, post in zip(percent_reinforced_pre, percent_reinforced_post):
        plt.plot(x, [pre, post])
    # TODO boxplot on top of this?

    plt.show()

