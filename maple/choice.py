#!/usr/bin/env python2
# TODO change back to python3 after upgrading maple code

"""
A script to control the MAPLE robot to load and unload flies from the behavior
chambers, running experiments in between.
"""

from __future__ import print_function
from __future__ import division

import sys
import os
import random

import numpy as np

import maple
import maple.errs
import maple.module
import maple.robotutil
# TODO also use this api in other places i call roslaunch w/ subprocess
# (roi_finder might be the only other place I do that?)
#import roslaunch


class ChoiceModule(maple.module.Array):
    """
    """
    def __init__(self, robot, offset, position_correction=True, verbose=False):
        # Oriented rotated 90 degrees clockwise from LibreCAD schematics.
        # "length" and "height" in FreeCAD params reflect LibreCAD rotation.
        # All units mm.
        chamber_height = 203
        chamber_length = 279.4
        v1_nub_height = 25
        v1_nub_length = 80

        # This includes side heights plus screw heads.
        # TODO might need to either include extent of horz dsub or tubes going
        # into two Luer locks, or prevent paths from going near them.
        # TODO could also make this a little shorter if all paths over chamber
        # stayed over ceiling PCB...
        # TODO just include more detailed map of heights and let some path
        # planning work?
        max_z_extent = 19.5

        # TODO if extent is only going to be what is flush with floor, s.t. it
        # can be used to generate layout w/ 1/8" sheet, maybe also include
        # extents beyond these dimensions that would still need to be considered
        # to bounds check...
        extent = (chamber_height + v1_nub_height,
                  chamber_length,
                  max_z_extent)

        # TODO experiment with this
        # Defined from z=0 being the bottom of this module.
        # 10.8 seemed to verge on not deep enough to reliably make a good seal
        # (though may need to revisit after playing with how billows sits)
        # 9.8 seemed possibly too low to allow fly to get shot past door,
        # leading to some escapes and door deaths (though possible it is also
        # because wider loading holes on this ceiling I cut)
        flymanip_working_height = 10.4

        n_cols = 8
        n_rows = 1
        # Measured from upper left corner of bottom layer, to the center of the
        # closest hole in the ceiling layer, as if the corner were not filleted,
        # with the dimensions swapped.
        to_first_anchor = (19.738 + v1_nub_height, 139.701)
        anchor_spacing = 22.5

        super(ChoiceModule, self).__init__(robot, offset, extent,
            flymanip_working_height, n_cols, n_rows,
            to_first_anchor, anchor_spacing,
            position_correction=position_correction)

        # TODO require working height for this effector higher up in class
        # heirarchy? (in ArrayWithDoors, for sure, if i implement that)
        self.z0_working_height = 9.5 # was 9.0
        self.z0_center_travel_height = self.z0_working_height + 6

        # TODO was this causing backlash problems?
        # TODO TODO (seems likely) can still skip closing doors, just approach
        # as it opening on next load
        #self.close_doors_after_unloading = False
        self.close_doors_after_unloading = True

        self.door_vac_connect_delay_ms = 0
        self.door_vac_disconnect_delay_ms = 0
        # TODO measure whether this actually helps (seemed to by hand, but might
        # not with robot) (and is 2 sufficient?)
        self.repeats_per_door = 2

        # TODO implement
        #self.door_overshoot = 0.5

        # Assume everything is closed at beginning, b/c trying to open a closed
        # door isn't really that harmful (?), and the first operation will need
        # them open.
        self.door_is_open = np.full((self.n_cols, self.n_rows), False)


    def get(self, xy, ij):
        """
        """
        if self.robot is not None:
            self.robot.flyManipVac(True)
            self.robot.flyManipAir(False)
            # TODO add support for larger valve? (just rewire into old vac?)

        self.open_door(ij)

        if self.robot is not None:
            # Anchors are defined as centers of fly loading ports here.
            self.robot.moveXY(xy)

            self.robot.fly_vac_highflow(True)

            zw = self.robot.z2_to_worksurface - self.flymanip_working_height
            print('Moving fly manipulator to working height {}'.format(zw))
            self.robot.moveZ2(zw)

            self.robot.dwell_ms(2000)
            self.robot.fly_vac_highflow(False)

            self.robot.dwell_ms(1000)
            self.robot.fly_vac_highflow(True)
            self.robot.dwell_ms(5000)

            self.robot.fly_vac_highflow(False)

            zt = self.robot.z2_to_worksurface - self.flymanip_working_height - 6
            print('Moving fly manipulator to local travel height {}'.format(zt))
            self.robot.moveZ2(zt)

        #else:
        print('Getting fly from behavior chamber {} ({})'.format(ij, xy))

        if self.close_doors_after_unloading:
            self.close_door(ij)


    def put(self, xy, ij):
        """
        Assumes flyManipVac is on and flyManipAir is off, otherwise fly could
        have been able to escape.
        """
        # how much time will i have before flies start to escape? test
        self.open_door(ij)

        if self.robot is not None:
            self.robot.moveXY(xy)

            zw = self.robot.z2_to_worksurface - self.flymanip_working_height
            print('Moving fly manipulator to working height {}'.format(zw))
            self.robot.moveZ2(zw)

            self.robot.flyManipVac(False)
            self.robot.flyManipAir(True)
            self.robot.dwell_ms(1200)
            self.robot.flyManipAir(False)

            zt = self.robot.z2_to_worksurface - self.flymanip_working_height - 6
            print('Moving fly manipulator to local travel height {}'.format(zt))
            self.robot.moveZ2(zt)

        print('Depositing fly in behavior chamber {} ({})'.format(ij, xy))

        # again, test escape rate
        self.close_door(ij)


    # TODO would doors like these be a common enough motif to include their
    # positions (optionally?) in Array constructor, and move these fns up there?
    # maybe an ArrayWithDoors class?
    def open_door(self, ij):
        """
        Assumes smallPartManipAir is off.
        """
        # TODO TODO TODO check that vac isn't pulling doors up (increasing
        # friction, risking escape, etc) at the working height (decrease working
        # height if so)
        if self.door_is_open[ij]:
            print('Door {} was already open'.format(ij))
            return

        closed_door = self.door_center(ij, closed=True)
        open_door = self.door_center(ij, closed=False)

        #if self.robot is None:
        print('Moving to closed door at {}'.format(closed_door))
        print('Moving door to open position at {}'.format(open_door))

        if self.robot is not None:
            zt = self.robot.z0_to_worksurface - self.z0_center_travel_height
            curr_z0 = self.robot.currentPosition[2]

            if curr_z0 <= zt:
                print('Part manipulator already above minimum travel height' +
                    ' ({} <= {})'.format(curr_z0, zt))
            else:
                print('Moving part manipulator to local travel height ' +
                    '{}'.format(zt))
                self.robot.moveZ0(zt)

            # TODO maybe jitter starting position of other attempts optionally?
            for _ in range(self.repeats_per_door):
                self.robot.smallPartManipVac(True)

                self.robot.moveXY(self.door_center(ij, closed=True))

                zw = self.robot.z0_to_worksurface - self.z0_working_height
                self.robot.moveZ0(zw)

                self.robot.dwell_ms(self.door_vac_connect_delay_ms)
                self.robot.moveXY(self.door_center(ij, closed=False))
                self.robot.dwell_ms(self.door_vac_disconnect_delay_ms)
                self.robot.smallPartManipVac(False)

                self.robot.moveZ0(zt)

        self.door_is_open[ij] = True


    def close_door(self, ij):
        """
        Assumes smallPartManipAir is off.
        """
        if not self.door_is_open[ij]:
            print('Door {} was already closed'.format(ij))
            return

        open_door = self.door_center(ij, closed=False)
        closed_door = self.door_center(ij, closed=True)

        #if self.robot is None:
        print('Moving to open door at {}'.format(open_door))
        print('Moving door to closed position at {}'.format(closed_door))
        #    return

        if self.robot is not None:
            zt = self.robot.z0_to_worksurface - self.z0_center_travel_height
            curr_z0 = self.robot.currentPosition[2]

            if curr_z0 <= zt:
                print('Part manipulator already above minimum travel height' +
                    ' ({} <= {})'.format(curr_z0, zt))
            else:
                print('Moving part manipulator to local travel height ' +
                    '{}'.format(zt))
                self.robot.moveZ0(zt)

            for _ in range(self.repeats_per_door):
                self.robot.smallPartManipVac(True)
                self.robot.moveXY(open_door)
                zw = self.robot.z0_to_worksurface - self.z0_working_height
                self.robot.moveZ0(zw)

                self.robot.dwell_ms(self.door_vac_connect_delay_ms)
                self.robot.moveXY(closed_door)
                self.robot.dwell_ms(self.door_vac_disconnect_delay_ms)
                self.robot.smallPartManipVac(False)

                self.robot.moveZ0(zt)

        self.door_is_open[ij] = False


    def door_center(self, ij, closed=False):
        """
        """
        i, j = ij
        assert j == 0, 'This module only has one column.'
        # TODO check using right index
        x, y = self.anchor_center(i, j)

        # TODO use central offset definition (in cfg?)
        # 78 was measured from Z-plate DXF. Need correction?
        door_x = x - 4.89 - 78

        # Which side the door is on alternates, about axis that goes through
        # each anchor (fly loading holes). Reflected in y with workspace
        # orientation.

        dy = 10.0 if closed else 14.0
        if i % 2 == 0:
            door_y = y + dy
        else:
            door_y = y - dy

        return (door_x, door_y)

    # TODO TODO function to test opening and closing of doors
    # to optimize working height + overshoot (if any)


def measure_offset(array_modules, current_offset=None):
    """
    """
    points = []
    errors = []
    for array_module in array_modules:
        ps, errs = array_module.measure_errors()
        points.extend(ps)
        errors.extend(errs)

    print('Errors:')
    for p, e in zip(points, errors):
        print(p, e)

    mean_errors = np.mean(errors, 0)
    print('Mean errors ({0[0]}, {0[1]})'.format(mean_errors))
    if current_offset is not None:
        print('Change Z2 offset to ({0[0]}, {0[1]})'.format(
            current_offset + mean_errors))

    return points, errors


def main():
    ###########################################################################
    # Flags
    ###########################################################################
    #random_order = True
    random_order = False
    dry_run = False
    just_right_arena = True

    # TODO TODO include mode to load the flies back into flyplate after
    # experiment, for testing purposes (cycle back and forth and measure loss)

    if just_right_arena and random_order:
        raise ValueError('set random_order to False to use just_right_arena')

    ###########################################################################
    # TODO implement contructor that can also take components of workspace?
    if dry_run:
        robot = None
    else:
        # TODO allow calling constructor w/ no arguments for default config
        robot = maple.robotutil.MAPLE(os.path.join(maple.__path__[0],
            'MAPLE.cfg'))
        ###    'MAPLE.cfg'), home=False)

    # Distance from zero defined in alignment_plate.dxf (inside corner of
    # vertical support in top right corner) to z2 (fly) effector, when the robot
    # is at what it considers to be (0,0)
    z2_offset = (46.89, 94.8)

    # Silicone seems to just be touching at ~40mm. Silicone extends between
    # metal needle by maybe ~1mm or so.
    #robot.z2_to_worksurface = 43.175
    # This is a point just north of the flyplate.
    # TODO maybe save and only do this every so often (or if errors seem to
    # happen)
    # TODO TODO have this fail / re-home if it basically times out
    # now, it just uses the position it thinks it got to as the reference
    robot.zero_z2_to_reference(xy=(310, 110), thickness=3.175, speed=1500)

    # TODO TODO set relative to z2_to_worksurface if not using sensor?
    # Measured 45.5 to top of 1/8" alignment plate + 3.175 thickness of that
    # plate.
    robot.z0_to_worksurface = 48.675

    # Measured from tom-f-oconnell/MAPLEHardware/Drawings/alignment_plate.dxf,
    # with construction lines added as necessary to measure from origin to top
    # right corner of the bounding box of each module.

    # Turning off position_correction on left_arena, so that isn't done in the
    # constructor, since I'm not using the left_arena just while testing.
    left_arena = ChoiceModule(robot,
        (382.15 - z2_offset[0], 18.2 - z2_offset[1]), position_correction=False)
    right_arena = ChoiceModule(robot,
        (93.65 - z2_offset[0], 18.2 - z2_offset[1]))

    flyplate = maple.module.FlyPlate(robot,
        (321.65 - z2_offset[0], 212.0 - z2_offset[1]))

    morgue = maple.module.Morgue(robot,
        (427.15 - z2_offset[0], 303.8 - z2_offset[1]))

    modules = {
        'left_arena': left_arena,
        'right_arena': right_arena,
        'flyplate': flyplate,
        'morgue': morgue
    }

    def indices_to_platelabels(ij):
        cols = [chr(x + ord('A')) for x in range(8)][::-1]
        rows = [x for x in range(1, 13)][::-1]
        return cols[i], rows[j]

    def platelabels_to_indices(letter, num):
        i = ord('H') - ord(letter)
        j = 12 - num
        return (i, j)

    # TODO how to have it just to the next well, rather than starting from (0,0)
    # set all preceding to full?
    # TODO cache automatically if crash, etc
    # TODO TODO also save position while clearing arrays
    # (need to store another bit to say whether you are loading or unloading?)
    # or just load if have flies and some are still empty?
    start_from = platelabels_to_indices('G', 7)

    flyplate.full[:start_from[0], :] = False
    flyplate.full[start_from[0], :start_from[1]] = False

    # TODO compute and save desired working distances?
    '''
    print('Measuring Z2 working distance for flyplate:')
    flyplate.measure_working_distance()
    print('\nMeasuring Z2 working distance for choice chamber for flyplate:')
    right_arena.measure_working_distance()
    print('')
    '''

    # TODO TODO build in ability to start where it left off
    # (like if there was an error or the program needed to be stopped)

    # TODO TODO how come a keyboardinterrupt during homing doesn't have the
    # robot stop right after the home? shouldnt sendSyncCmd still be waiting to
    # finish, and then that be what gets interrupted? fix if possible

    ###########################################################################
    # Load flies
    ###########################################################################
    # TODO maybe factor into function outside of main, s.t. after the plate is
    # out of flies, the user can just be prompted to reload it before the main
    # loop continues

    experiment_num = 1
    while flyplate.has_flies():

        # TODO TODO handle this better...
        try:
            while (not left_arena.is_full()) or (not right_arena.is_full()):

                if just_right_arena and right_arena.is_full():
                    break

                if random_order:
                    # TODO TODO TODO load multi_tracker rois, map those to
                    # index coordinates in the module, and implement some simple
                    # machine vision to check whether a fly has been loaded in a
                    # given chamber. skip chambers that have a fly in them.
                    # TODO AND AVOID TRACKING THEM
                    # TODO and warn once the # of such chambers reaches a
                    # certain threshold value

                    # Takes a fly from the flyplate. It will be held in the fly
                    # manipulator effector with vacuum until it is deposited.
                    # TODO TODO manage metadata about the fly. probably easiest
                    # to take data from a GUI to annotate flies in the wells?
                    source_pos = flyplate.get_random()

                    # TODO maybe randomly select from all available wells, s.t.
                    # there isn't more probability (per well) on wells in more
                    # full chambers?
                    # TODO just weight choice by # wells free? (would need new
                    # func?)
                    # TODO fix hack. use dict of modules addressed by name or
                    # something.
                    arena_to_load = random.choice([x for x in [('left_arena',
                        left_arena), ('right_arena', right_arena)]
                        if not x[1].is_full()])

                    print('Trying to load {}'.format(arena_to_load[0]))
                    #dest_arena = arena_to_load.__name__

                    # Deposits the fly currently in the manipulator into a
                    # random well in the behavior arena.
                    dest_pos = arena_to_load[1].put_random()

                else:
                    source_pos = flyplate.get_next()

                    if not right_arena.is_full():
                        arena_to_load = right_arena
                        arena_name = 'right_arena'

                    elif not left_arena.is_full():
                        arena_to_load = left_arena
                        arena_name = 'left_arena'

                    else:
                        # TODO invalid state error
                        assert False

                    print('Trying to load {}'.format(arena_name))
                    dest_pos = arena_to_load.put_next()
                    

                if flyplate.is_empty():
                    break

        except maple.errs.FlyManipulatorCrashError:
            # TODO factor this all into a fn or use only one except block

            # TODO TODO TODO save state and also clear calibration of module we
            # crashed over
            # TODO TODO get current position and use it to check which module we
            # are over
            pos = robot.getCurrentPosition()
            # TODO log position of crash, including Z

            # TODO TODO probably need to skip to the next fly, considering we
            # will likely have lost the fly in the crash, when the vacuum
            # switched off

            for name, m in modules.items():
                # (Ignoring calibration for now)
                if m.contains(pos[:2]):
                    print('\n\nCrashed over module {}!!!!!\n\n'.format(name))
                    print('You will need to recalibrate this module.')
                    m.clear_correction()
                    break

            # TODO could jitter position and retry?

            # TODO factor into robot util function just short of release
            robot.smoothie.sendCmd('M999\n')

            robot.light(False)
            robot.flyManipVac(False)
            robot.smallPartManipVac(False)
            robot.flyManipAir(False)
            robot.smallPartManipAir(False)
            robot.fly_vac_highflow(False)
            #

            robot.home()

        # TODO TODO load rois saved w/ choice ROS acquisition scripts, so that
        # we can build backgrounds for each of those regions, and check for
        # flies getting loaded / cleared successfully (may need to adjust for
        # rectangular ROIs, if I allow those to be applied simultaneously)
        # (may also need to move gantry out of way to check)

        ########################################################################
        # Run the experiment
        ########################################################################
        # TODO maybe don't image both chambers if one is empty?

        #if dry_run:
        print('\n\nRunning experiment {}\n'.format(experiment_num))

        '''
        else:
            # TODO in example, they make a node first. necessary?
            uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
            roslaunch.configure_logging(uuid)
            # TODO just make cli args I want here the default for use in <lunar
            # would need to upgrade to lunar if I wanted to pass cli args
            # TODO find launch file w/ ros api tools? assume catkin ws location
            # relative to home?
            launch = roslaunch.parent.ROSLaunchParent(uuid,
                ['/home/tom/catkin/src/choice/launch/choice.launch'])

            # TODO does this return when the launch file finishes?
            launch.start()
        '''
        experiment_num += 1

        # TODO also transfer data, start tracking, and (if labelling is
        # automated) do analysis (build that sequence here, or elsewhere and
        # wrap?)

        # TODO need to clear namespace or anything? (test)


        ########################################################################
        # Unload the flies
        ########################################################################
        try:
            while left_arena.has_flies() or right_arena.has_flies():
                if random_order:
                    arena_to_clear = random.choice([x for x in
                        [left_arena, right_arena] if x.has_flies()])
                    source_pos = arena_to_clear.get_random()

                else:
                    if right_arena.has_flies():
                        arena_to_clear = right_arena
                        arena_name = 'right_arena'

                    elif left_arena.has_flies():
                        arena_to_clear = left_arena
                        arena_name = 'left_arena'

                    else:
                        # TODO invalid state error
                        assert False

                    source_pos = arena_to_clear.get_next()

                morgue.put()
                #if dry_run:
                print('')

        except maple.errs.FlyManipulatorCrashError:
            pos = robot.getCurrentPosition()
            for name, m in modules.items():
                if m.contains(pos[:2]):
                    print('\n\nCrashed over module {}!!!!!\n\n'.format(name))
                    print('You will need to recalibrate this module.')
                    m.clear_correction()
                    break

            robot.smoothie.sendCmd('M999\n')
            robot.light(False)
            robot.flyManipVac(False)
            robot.smallPartManipVac(False)
            robot.flyManipAir(False)
            robot.smallPartManipAir(False)
            robot.fly_vac_highflow(False)

            robot.home()

        # TODO alternative strategies to maintain better repeatability?
        # just go slower? diff motor current? tension? move cables so they don't
        # touch edge?
        # TODO or search surface to find holes w/ Z2? vision?

        # To try to re-establish some positional accuracy.
        # Assumes error across homings are smaller than error that has
        # accumulated since last home.
        #robot.home()


# TODO TODO command line arg to force recalibration
if __name__ == '__main__':
    main()
