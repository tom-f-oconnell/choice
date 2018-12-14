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
    def __init__(self, robot, offset, position_correction=True,
            calibration_approach_from=None, verbose=False):
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
        # TODO TODO maybe slightly further down when withdrawing (and move
        # between two heights, to ensure seal?)
        # 11/27/18: 10.4 seemed maybe too low? (phenotype is flies were getting
        # stuck in door)
        # TODO it could be that the opposite vent helps get them out of the
        # doorway initially... for this trial, that was taped to try to assist
        # unloading
        flymanip_working_height = 11

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
            calibration_approach_from=calibration_approach_from)

        # TODO require working height for this effector higher up in class
        # heirarchy? (in ArrayWithDoors, for sure, if i implement that)
        self.z0_working_height = 9.5 # was 9.0
        self.z0_center_travel_height = self.z0_working_height + 6

        self.flymanip_travel_height = self.flymanip_working_height + 6

        # TODO maybe go back to using a fn to define calibration points,
        # b/c now I have to pass flag to superclass constructor indicating we
        # are going to handle checking for correction...
        # or maybe just don't automatically try to fit correction in
        # constructor?
        j = 0
        for i in (0, self.n_cols - 1):
            center = self.anchor_center(i, j, without_correction=True)

            for left in (True, False):
                z0_vx, vy = self.vent_manip_center( (i,j), left, closed=True)
                z2_vx = z0_vx - self.robot.z0_to_z2_dx
                self.calibration_points.append((z2_vx, vy))

                # TODO TODO might want to provide facilities for correcting
                # based on each point, rather than only applying correction to
                # the anchor_center and then assuming rectilinear axes about
                # that
                self.calibration_approach_points.append(center)

                # Will ultimately use the vacuum cup to move these vent doors.
                self.calibration_effectors.append(0)

        # was causing backlash problems
        #self.close_doors_after_unloading = False
        self.close_doors_after_unloading = True

        self.door_vac_connect_delay_ms = 0
        self.door_vac_disconnect_delay_ms = 0
        self.disconnect_air_ms = 80
        # TODO measure whether this actually helps (seemed to by hand, but might
        # not with robot) (and is 2 sufficient?)
        self.repeats_per_door = 1

        # TODO implement
        #self.door_overshoot = 0.5

        # Assume everything is closed at beginning, b/c trying to open a closed
        # door isn't really that harmful (?), and the first operation will need
        # them open.
        self.door_is_open = np.full((self.n_cols, self.n_rows), False)
        # 2 vents per chamber. One on either end.
        self.vent_is_open = np.full((self.n_cols, self.n_rows, 2), False)


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
            zt = self.robot.z2_to_worksurface - self.flymanip_travel_height
            print('Moving fly manipulator to working height {}'.format(zw))
            self.robot.moveZ2(zw)

            self.robot.dwell_ms(2000)
            # TODO need to shut off? (might interfere w/ door operation...)
            self.robot.fly_vac_highflow(False)

            # TODO TODO TODO should i just go to the morgue after each hole?
            # or will it either not generate too much debris by running higher
            # vac against flies or will it not matter?

            # TODO also try blowing thru vents to push fly towards center, if
            # we don't want to / can't suck flies thru vents.
            # TODO randomly pick which to open first?

            # TODO yea... just factor into a fn
            # Left vent
            self.open_vent(ij, True)
            self.robot.fly_vac_highflow(True)
            self.to_vent_port(ij, True)
            self.robot.moveZ2(zw)
            self.robot.dwell_ms(2000)
            self.robot.fly_vac_highflow(False)
            self.close_vent(ij, True)

            # Right vent
            self.open_vent(ij, False)
            self.robot.fly_vac_highflow(True)
            self.to_vent_port(ij, False)
            self.robot.moveZ2(zw)
            self.robot.dwell_ms(2000)
            self.robot.fly_vac_highflow(False)
            self.close_vent(ij, False)

            '''
            self.robot.fly_vac_highflow(False)

            self.robot.dwell_ms(500)
            self.robot.flyManipVac(False)
            self.robot.flyManipAir(True)
            self.robot.dwell_ms(800)
            self.robot.flyManipVac(True)
            self.robot.flyManipAir(False)

            self.robot.dwell_ms(750)
            self.robot.fly_vac_highflow(True)
            self.robot.dwell_ms(5000)

            self.robot.fly_vac_highflow(False)
            '''
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
            self.robot.dwell_ms(1500)
            # TODO leave on while withdrawing a little? if lack of opposite vent
            # is the problem, and that does help with unloading, then may need
            # to play around with this...
            self.robot.flyManipAir(False)

            zt = self.robot.z2_to_worksurface - self.flymanip_travel_height
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

                self.robot.smallPartManipAir(True)
                self.robot.dwell_ms(self.disconnect_air_ms)
                self.robot.smallPartManipAir(False)

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
            # TODO TODO may need to use fn that uses gcode to get pos from
            # smoothie?
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

                self.robot.smallPartManipAir(True)
                self.robot.dwell_ms(self.disconnect_air_ms)
                self.robot.smallPartManipAir(False)

                self.robot.moveZ0(zt)

        self.door_is_open[ij] = False


    def open_vent(self, ij, left):
        """
        """
        i, j = ij
        k = 0 if left else 1

        if self.vent_is_open[i, j, k]:
            print('{} vent {} was already open'.format(
                'Left' if left else 'Right', ij))
            return

        open_vent = self.vent_manip_center(ij, left, closed=False)
        closed_vent = self.vent_manip_center(ij, left, closed=True)

        print('Moving to closed {} vent at {}'.format(
            'left' if left else 'right', closed_vent))
        print('Moving {} vent to open position at {}'.format(
            'left' if left else 'right', open_vent))

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

            self.robot.moveXY(closed_vent)

            zw = self.robot.z0_to_worksurface - self.z0_working_height
            self.robot.moveZ0(zw)
            self.robot.moveXY(open_vent)
            self.robot.moveZ0(zt)

        self.vent_is_open[i, j, k] = True


    def close_vent(self, ij, left):
        """
        """
        i, j = ij
        k = 0 if left else 1

        if not self.vent_is_open[i, j, k]:
            print('{} vent {} was already closed'.format(
                'Left' if left else 'Right', ij))
            return

        open_vent = self.vent_manip_center(ij, left, closed=False)
        closed_vent = self.vent_manip_center(ij, left, closed=True)

        print('Moving to open {} vent at {}'.format(
            'left' if left else 'right', open_vent))
        print('Moving {} vent to closed position at {}'.format(
            'left' if left else 'right', closed_vent))

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

            # So that manipulator isn't right up against the edge it was pushing
            # when it was opening the door.
            backoff = 0.5
            self.robot.moveXY((open_vent[0] + backoff, open_vent[1]))

            zw = self.robot.z0_to_worksurface - self.z0_working_height
            self.robot.moveZ0(zw)

            # Some other effect causing need for this.
            # Maybe it's lasercutter kerf? Maybe friction from effector rubbing
            # on shim layer and bending?
            further = 0.6
            self.robot.moveXY((closed_vent[0] + further, closed_vent[1]))
            self.robot.moveZ0(zt)

        self.vent_is_open[i, j, k] = False


    # TODO similar fn for main fly ports?
    def to_vent_port(self, ij, left, z_axis=2):
        """
        """
        if not (z_axis == 0 or z_axis == 2):
            raise ValueError('only Z0 and Z2 supported')

        # In Z0 coordinates
        vent_port = self.vent_air_center(ij, left)

        # TODO open first?
        
        if self.robot is not None:
            if z_axis == 0:
                zt = self.robot.z0_to_worksurface - self.z0_center_travel_height
                curr_z0 = self.robot.currentPosition[2]

                if curr_z0 <= zt:
                    print('Part manipulator already above minimum travel ' +
                        'height ({} <= {})'.format(curr_z0, zt))
                else:
                    print('Moving part manipulator to local travel height ' +
                        '{}'.format(zt))
                    self.robot.moveZ0(zt)

                self.robot.moveXY(vent_port)

                # TODO maybe allow this to be set indep of height for main port?
                zw = self.robot.z0_to_worksurface - self.z0_working_height
                self.robot.moveZ0(zw)

            elif z_axis == 2:
                zt = self.robot.z2_to_worksurface - self.flymanip_travel_height
                curr_z2 = self.robot.currentPosition[4]

                if curr_z2 <= zt:
                    print('Fly manipulator already above minimum travel height'+
                        ' ({} <= {})'.format(curr_z2, zt))
                else:
                    print('Moving fly manipulator to local travel height ' +
                        '{}'.format(zt))
                    self.robot.moveZ2(zt)

                self.robot.moveXY([vent_port[0] - self.robot.z0_to_z2_dx,
                    vent_port[1]])

                # TODO maybe allow this to be set indep of height for main port?
                zw = self.robot.z2_to_worksurface - self.flymanip_working_height
                self.robot.moveZ2(zw)


    def door_center(self, ij, closed=False):
        """Returns door_center in Z0 coordinates.
        """
        i, j = ij
        assert j == 0, 'This module only has one column.'
        x, y = self.anchor_center(i, j)
        flyport_to_door_dx = -4.89
        
        door_x = x + flyport_to_door_dx + self.robot.z0_to_z2_dx

        dy = 8.252
        if not closed:
            # Real stroke should be 3. Adding 1 for backlash.
            dy += 4.0

        # Which side the door is on alternates, about axis that goes through
        # each anchor (fly loading holes). Reflected in y with workspace
        # orientation.
        if i % 2 == 0:
            door_y = y + dy
        else:
            door_y = y - dy

        return (door_x, door_y)


    def vent_air_center(self, ij, left):
        """Returns center of vent air/vacuum application point.

        Args:
        left (bool): True if you want center of left vent manipulation point,
            viewing chamber in CAD orientation (w/ D-sub at bottom). False
            otherwise.
        """
        i, j = ij
        assert j == 0, 'This module only has one column.'
        x, y = self.anchor_center(i, j)

        vent_air_x = x + 1.268 + self.robot.z0_to_z2_dx

        flyport_to_vent_air_dy = 22.495
        if left:
            vent_air_y = y - flyport_to_vent_air_dy
        else:
            vent_air_y = y + flyport_to_vent_air_dy
        
        return (vent_air_x, vent_air_y)


    def vent_manip_center(self, ij, left, closed=True):
        """Returns center of vent slider manipulation point.

        Args:
        left (bool): True if you want center of left vent manipulation point,
            viewing chamber in CAD orientation (w/ D-sub at bottom). False
            otherwise.
        """
        vent_air_x, vent_air_y = self.vent_air_center(ij, left)

        # May want to set this less, possibly to prevent fly escape, catching,
        # or limit switch problems.
        # 4 did pose some limit switch problems, at least with one calibration.
        vent_stroke = 3.3
        max_vent_stroke = 4
        assert vent_stroke <= max_vent_stroke

        vent_manip_y = vent_air_y
        fudge_factor = -0.4
        vent_manip_dx = -4.75 + fudge_factor

        # These doors open along other axis, so this is the coordinate that
        # changes depending on open / closed status.
        if not closed:
            # TODO TODO maybe backtrack a little, so we aren't right up against
            # the same right edge that we pushed to get the slider in this
            # position
            vent_manip_dx += -vent_stroke

        vent_manip_x = vent_air_x + vent_manip_dx

        return (vent_manip_x, vent_manip_y)


    # TODO maybe effectors_to_travel_height in all of these fns?
    def open_doors(self):
        """
        """
        self.effectors_to_travel_height()

        for ij in self.all_index_pairs():
            self.open_door(ij)

        self.effectors_to_travel_height()


    def close_doors(self):
        """
        """
        self.effectors_to_travel_height()

        for ij in self.all_index_pairs():
            self.close_door(ij)

        self.effectors_to_travel_height()


    # TODO TODO also store state of vents
    def open_vents(self):
        """
        """
        self.effectors_to_travel_height()

        for ij in self.all_index_pairs():
            if self.robot is not None:
                i, j = ij
                # To keep backlash similar to during normal operation
                z2x, z2y = self.anchor_center(i,j)
                self.robot.moveXY([z2x + self.robot.z0_to_z2_dx, z2y])

            # Left
            self.open_vent(ij, True)
            # Right
            self.open_vent(ij, False)

        self.effectors_to_travel_height()


    def close_vents(self):
        """
        """
        self.effectors_to_travel_height()

        for ij in self.all_index_pairs():
            if self.robot is not None:
                i,j = ij
                z2x, z2y = self.anchor_center(i,j)
                self.robot.moveXY([z2x + self.robot.z0_to_z2_dx, z2y])

            # Left
            self.close_vent(ij, True)
            # Right
            self.close_vent(ij, False)

        self.effectors_to_travel_height()


    def visit_all_loading_ports(self):
        """To see whether there would be crashes.

        Result of check will mean more if approaches in use are in same
        direction as here, because of the backlash.
        """
        self.effectors_to_travel_height()

        for i, j in self.all_index_pairs():
            xy = self.anchor_center(i,j)
            self.robot.moveXY(xy)

            zw = self.robot.z2_to_worksurface - self.flymanip_working_height
            print('Moving fly manipulator to working height {}'.format(zw))
            self.robot.moveZ2(zw)
            
            zt = self.robot.z2_to_worksurface - self.flymanip_travel_height
            print('Moving fly manipulator to local travel height {}'.format(zt))
            self.robot.moveZ2(zt)

        self.effectors_to_travel_height()

    
    def visit_all_vent_ports(self, z_axis=2):
        """To see whether there would be crashes.

        Result of check will mean more if approaches in use are in same
        direction as here, because of the backlash.
        """
        assert z_axis == 2 or z_axis == 0

        self.effectors_to_travel_height()
        zt = self.robot.z0_to_worksurface - self.z0_center_travel_height

        for ij in self.all_index_pairs():
            if self.robot is not None:
                i,j = ij
                z2x, z2y = self.anchor_center(i,j)
                self.robot.moveXY([z2x + self.robot.z0_to_z2_dx, z2y])

            self.to_vent_port(ij, True, z_axis=z_axis)

            self.effectors_to_travel_height()
            #print('Moving part manipulator to local travel height {}'.format(
            #    zt))
            #self.robot.moveZ0(zt)

            self.to_vent_port(ij, False, z_axis=z_axis)

            self.effectors_to_travel_height()
            #print('Moving part manipulator to local travel height {}'.format(
            #    zt))
            #self.robot.moveZ0(zt)

        self.effectors_to_travel_height()

    # TODO one function that combines all to check for crashes


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
    z2_reference_point = (310, 110)

    if not dry_run:
        # Silicone seems to just be touching at ~40mm. Silicone extends between
        # metal needle by maybe ~1mm or so.
        #robot.z2_to_worksurface = 43.175
        # This is a point just north of the flyplate.
        '''
        robot.zero_z2_to_reference(xy=z2_reference_point, thickness=3.175,
            speed=1500)
        print('Found worksurface at Z2={:.2f}mm'.format(
            robot.z2_to_worksurface))
        '''
        # Measured as above
        robot.z2_to_worksurface = 44.5125

        # TODO TODO set relative to z2_to_worksurface if not using sensor?
        # Measured 45.5 to top of 1/8" alignment plate + 3.175 thickness of that
        # plate.
        robot.z0_to_worksurface = 48.675 + 14.0 - 3 #48.675

        # TODO use central offset definition (in cfg?)
        # 78 was measured from Z-plate DXF. Need correction?
        # 78 is the difference in X position of the Z0 and Z2 motor mounts.
        robot.z0_to_z2_dx = -(78 - 1)

    # Measured from tom-f-oconnell/MAPLEHardware/Drawings/alignment_plate.dxf,
    # with construction lines added as necessary to measure from origin to top
    # right corner of the bounding box of each module.

    flyplate = maple.module.FlyPlate(robot,
        (321.65 - z2_offset[0], 212.0 - z2_offset[1]),
        calibration_approach_from=z2_reference_point)
    # TODO TODO save these in human editable format like json/yaml, rather than
    # pickle
    flyplate.fit_correction()

    left_arena = ChoiceModule(robot,
        (382.15 - z2_offset[0], 18.2 - z2_offset[1]),
        calibration_approach_from=flyplate.offset[:2] + (flyplate.extent[0], 0))
    if not just_right_arena:
        left_arena.fit_correction()

    right_arena = ChoiceModule(robot,
        (93.65 - z2_offset[0], 18.2 - z2_offset[1]),
        calibration_approach_from=flyplate.offset[:2])
    right_arena.fit_correction()

    morgue = maple.module.Morgue(robot,
        (427.15 - z2_offset[0], 303.8 - z2_offset[1]))

    # TODO maybe factor into some kind of workspace class, with higher level
    # planning fns (could be useful at least for picking appropriate approach
    # points to avoid backlash errors in calibration)
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
    '''
    start_from = platelabels_to_indices('G', 7)

    flyplate.full[:start_from[0], :] = False
    flyplate.full[start_from[0], :start_from[1]] = False
    '''

    # TODO compute and save desired working distances?
    '''
    print('Measuring Z2 working distance for flyplate:')
    flyplate.measure_working_distance()
    print('\nMeasuring Z2 working distance for choice chamber for flyplate:')
    right_arena.measure_working_distance()
    print('')
    '''

    # TODO delete me
    #right_arena.open_doors()
    #right_arena.close_doors()

    ###right_arena.clear_correction()

    #right_arena.visit_all_loading_ports()
    # TODO fix anchors in z2 case. seems to be using z0 anchor.
    #right_arena.visit_all_vent_ports()
    right_arena.open_vents()
    right_arena.close_vents()

    sys.exit()
    #

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
                    # TODO TODO so provide function to return list of tuples of
                    # indices of free wells? (& maybe also full well for
                    # unloading?)
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
                    # TODO maybe just prompt on next run as to whether it should
                    # be deleted? maybe prompt now?
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

        if not dry_run:
            print('Moving effectors out of way.')
            robot.moveZ0(0)
            robot.moveZ2(0)
            stage_right = left_arena.offset[:2] + [left_arena.extent[0] + 50, 0]
            # For return w/o backlash. May want to just home and then move a
            # little to the opposite side of the first well, or visit morgue
            # first.
            robot.moveXY(stage_right)

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
