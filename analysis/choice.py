#!/usr/bin/env python

from __future__ import division
import numpy as np
import pandas as pd
# TODO figure out what the hold up is on importing this, with the prints
import multi_tracker_analysis as mta
import glob
from os.path import join, split
import re
import pickle
from stimuli.srv import LoadSequenceRequest
# TODO maybe remove this dependency if it means it cant be run easily on windows?
import rosparam

make_plots = True

# TODO will this work?
if make_plots:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import seaborn as sns
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

'''
also check:
20170913_105853
    -end of roi 1 (does first shock kill the fly?)
    -roi 5. ever a fly in there?
    -3. i assume artifact? (basically a flat line)
    -6. also only looks like a fly part of the time. investigate flat regions.
        -also more flat towards end
    -4. looks like a step function. real?
    -2 WHY DOES THIS ALSO GET FLAT TOWARDS END?
    -7 SAME THING

really not excluding from this one?
20170913_104724
    -(WHICH) why so jumpy?
    -5, whats up during flat region starting at last training session?

really only 2/6 this day were good? what happened to other 2 flies?
20170913_112951
    -1, really ugly. i assume there was no fly?
    -3, pretty jumpy
    -4, if there is a fly at all, very erratic. investigate.

'''

bad = {'20170913_104724': set(),
       '20170913_105853': {3,4,5},
       '20170913_112951': {1,2,4,5}}

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
        '''
        print 'position_x range', data['position_x'].min(), data['position_x'].max()
        print 'position_y range', data['position_y'].min(), data['position_y'].max()
        '''
        match = re.search('_N([0-9])_', f)
        # TODO why is it more than what is in the parens?
        #print 'MATCH', match
        metadata['n'] = int(match.group(0)[2:-1])

        stamp = split(d)[-1]
        if metadata['n'] in bad[stamp]:
            print 'skipping fly', metadata['n'], 'from experiment', stamp, 'because listed as bad'
            continue

        fly2data[curr_fly] = data
        metadata['dir'] = d
        roi_points = rosparam.load_file(join(d, 'roi_N' + str(metadata['n']) + \
            '.yaml'))[0][0]['roi_points']
        metadata['roi_points'] = roi_points
        fly2meta[curr_fly] = metadata
        curr_fly += 1

if make_plots:
    cmap = sns.color_palette('husl', len(all_odors))
    odor2color = dict()
    for o, c in zip(all_odors, cmap):
        odor2color[o] = c

y_maxes_above_mid = []
y_mins_below_mid = []

# TODO assert that we are analyzing with dimension that corresponds to long axis of roi

for m in fly2meta.values():
    y_vals = map(lambda p: p[1], m['roi_points'])
    curr_mid = np.mean(y_vals)
    centered_y_vals = map(lambda y: y - curr_mid, y_vals)
    y_maxes_above_mid.append(max(centered_y_vals))
    y_mins_below_mid.append(min(centered_y_vals))

y_max_above_mid = max(y_maxes_above_mid)
y_min_below_mid = min(y_mins_below_mid)

print 'y_min_below_mid', y_min_below_mid, 'y_max_above_mid', y_max_above_mid

# TODO divide into mch and oct? make a dataframe including all variables (like side, etc)?
percent_reinforced_pre = []
percent_reinforced_post = []

# TODO why did 1100 not work? isn't sequence 1000 long?
crop_to_seconds = 1300

# TODO TODO line up images of ROIs, with drawn midline, to check for those errors
# TODO label / group by the reinforced odor?

plotting_y_max = None
plotting_y_min = None
plotting_x_max = None
plotting_x_min = None

axes_to_set_limits = []

y_shock_to_odor = 4
y_beyond_arena = 10
small_height = 6
odor_patch_alpha = 0.4
shock_patch_alpha = 1
shock_color = 'red'

for fly, data in fly2data.items():
    meta = fly2meta[fly]
    # TODO what happens to missing data?
    # plotted as zero? not plotted?
    curr_times = (data['time_epoch_secs'] + data['time_epoch_nsecs'] / 1e9).as_matrix()
    # TODO so does floris initialize something to 5000? blocks written in that size?
    #print(curr_times.shape)
    nonzero_times = curr_times.nonzero()[0]
    if nonzero_times.size == 0:
        print 'SKIPPING FLY', meta['n'], 'FROM', meta['dir']
        continue
    start = curr_times[nonzero_times].min()

    if make_plots:
        label_set = set()
        labels = []
        handles = []

        plt.figure()
        plt.title(meta['dir'] + ', ROI ' + str(meta['n']))
        plt.xlabel('Seconds')
        # TODO no other unit conversion is happening, right?
        # TODO convert
        plt.ylabel('Pixels relative to midline')
    #print 'START TIME =', start
    #print '# of zero entries', curr_times.size - nonzero_times.size

    # because for some of these, the tracking ran much longer than the stimulus presentation
    cropped_indices = (curr_times - start) <= crop_to_seconds
    cropped_times = curr_times[cropped_indices]
    # relative to start of experiment
    cropped_rel_times = cropped_times - start

    # calculate percent time in each odor region
    # TODO make one variable at top which controls which dimension to use as long axis
    # and have this (and elsewhere) depend on that
    y_mid = np.mean(map(lambda x: x[1], meta['roi_points']))
    if make_plots:
        # TODO TODO keep in mind this is probably inverted from image display, since pixels count from top
        plt.plot(cropped_rel_times , data['position_y'][cropped_indices] - y_mid)

    y_max = max(map(lambda x: x[1], meta['roi_points']))
    y_min = min(map(lambda x: x[1], meta['roi_points']))
    print 'y_max', y_max, 'y_min', y_min, 'using y midline', y_mid
    left = data['position_y'][cropped_indices] > y_mid
    pretest_indices = np.logical_and(cropped_times > meta['times']['pretest_start'], \
        cropped_times < (meta['times']['pretest_start'] + \
        meta['times']['test_duration']))

    posttest_indices = np.logical_and(cropped_times > meta['times']['posttest_start'], \
        cropped_times < (meta['times']['posttest_start'] + \
        meta['times']['test_duration']))

    # TODO TODO filter out trajectories that don't move much. just use floris' config file thing?

    large_height = (y_max_above_mid - y_min_below_mid) / 2 + y_beyond_arena
    
    for i, s in enumerate(meta['stimuli']):
        width = (s.seq.end - s.seq.start).to_sec()
        for p in s.seq.pins:
            color = 'b'
            label = None
            if p is left_shock:
                label = 'shock'
                color = shock_color
                height = small_height
                y0 = y_min_below_mid - y_beyond_arena - (y_shock_to_odor + small_height)
                alpha = shock_patch_alpha

            elif p is right_shock:
                label = 'shock'
                color = shock_color
                height = small_height
                y0 = y_max_above_mid + y_beyond_arena + y_shock_to_odor
                alpha = shock_patch_alpha

            elif p in meta['left_pins2odors']:
                #print 'left odor', meta['left_pins2odors'][p]
                if make_plots:
                    label = meta['left_pins2odors'][p]
                    color = odor2color[label]
                y0 = y_min_below_mid - y_beyond_arena
                height = large_height
                alpha = odor_patch_alpha

            elif p in meta['right_pins2odors']:
                #print 'right odor', meta['right_pins2odors'][p]
                if make_plots:
                    label = meta['right_pins2odors'][p]
                    color = odor2color[label]
                # because we define the middle as the new origin
                y0 = 0
                height = large_height
                alpha = odor_patch_alpha

            else:
                #print 'skipping pin', p
                continue

            # TODO maybe subdivide for shocks? (to reflect actual pulse cycle ~2.5s on/off)
            x0 = s.seq.start.to_sec() - start
            #print 'seq.start.to_sec()', s.seq.start.to_sec(), 'x0', x0, 'width', width
            if i == 0:
                # define acceptable mismatch here?
                if x0 <= 0.0:
                    print 'WARNING! seems no video was recorded for first ' + \
                        str(-x0) + ' seconds of first block (pre-training test)'

            else:
                assert x0 > 0, 'times we want to disply should not be negative. was ' + str(x0)

            assert x0 + width < crop_to_seconds, 'last time index of patched region should fall ' + \
                'within limits of cropped experiment. was ' + str(x0 + width) + ' end=' + \
                str(crop_to_seconds)
            #print 'patching pin', p, 'from', (x0, y0), 'with w=', width, 'and h=', height

            if make_plots:
                p = patches.Rectangle((x0, y0), width, height, alpha=alpha, \
                    facecolor=color, edgecolor=color)
                ax = plt.gca()
                ax.add_patch(p)

                if (not label is None)  and (not label in label_set):
                    label_set.add(label)
                    labels.append(label)
                    handles.append(p)

                axes_to_set_limits.append(ax)

                # TODO flipped?
                curr_y_max = y0 + height
                if plotting_y_max is None or plotting_y_max < curr_y_max:
                    plotting_y_max = curr_y_max

                curr_y_min = y0
                if plotting_y_min is None or plotting_y_min > curr_y_min:
                    plotting_y_min = curr_y_min

                curr_x_max = x0 + width
                if plotting_x_max is None or plotting_x_max < curr_x_max:
                    plotting_x_max = curr_x_max

                curr_x_min = x0
                if plotting_x_min is None or plotting_x_min > curr_x_min:
                    plotting_x_min = curr_x_min

    # patch indications of which sides are shocked, and when

    # TODO TODO check! (is sign effectively switched b/c pixel y origin being on top? plots at least 
    # may still be shown backwards)
    # TODO include a buffer region that is called in neither direction to make this more robust to 
    # misspecifying the middle of the arena?
    # TODO TODO check uniform sampling rate?
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
        plt.legend(handles=handles, labels=labels)

print 'plotting ranges: x', (plotting_x_min, plotting_x_max), 'y', (plotting_y_min, plotting_y_max)

# relative
y_bord = 0.05
x_bord = 0.05
x_range = plotting_x_max - plotting_y_min
y_range = plotting_y_max - plotting_y_min
plotting_x_min = plotting_x_min - x_range * x_bord
plotting_x_max = plotting_x_max + x_range * x_bord
plotting_y_min = plotting_y_min - y_range * y_bord
plotting_y_max = plotting_y_max + y_range * y_bord

for ax in axes_to_set_limits:
    ax.set_xlim([plotting_x_min, plotting_x_max])
    ax.set_ylim([plotting_y_min, plotting_y_max])

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

