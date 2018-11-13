#!/usr/bin/env python2
# TODO change back to python3 after upgrading maple code

"""
A script to control the MAPLE robot to load and unload flies from the behavior
chambers, running experiments in between.
"""

from __future__ import print_function
from __future__ import division

import os
import random

import maple
import maple.module
import maple.robotutil
# TODO also use this api in other places i call roslaunch w/ subprocess
# (roi_finder might be the only other place I do that?)
#import roslaunch


class ChoiceModule(maple.module.Array):
    """
    """
    def __init__(self, robot, offset, verbose=False):
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
        flymanip_working_height = 12

        n_cols = 8
        n_rows = 1
        # Measured from upper left corner of bottom layer, to the center of the
        # closest hole in the ceiling layer, as if the corner were not filleted,
        # with the dimensions swapped.
        to_first_anchor = (20.238 + v1_nub_height, 139.701)
        anchor_spacing = 22.5

        super(ChoiceModule, self).__init__(robot, offset, extent,
            flymanip_working_height, n_cols, n_rows,
            to_first_anchor, anchor_spacing)

        self.z0_working_height = 9
        self.z0_center_travel_height = self.z0_working_height + 4


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

            zw = self.robot.z2_to_worksurface - self.flymanip_working_height
            print('Moving fly manipulator to working height {}'.format(zw))
            self.robot.moveZ2(zw)

            self.robot.dwell_ms(5000)

            zt = self.robot.z2_to_worksurface - self.flymanip_working_height - 6
            print('Moving fly manipulator to local travel height {}'.format(zt))
            self.robot.moveZ2(zt)

        #else:
        print('Getting fly from behavior chamber {} ({})'.format(ij, xy))

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
            self.robot.dwell_ms(3000)
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

            self.robot.smallPartManipVac(True)
            # TODO require working height for this effector higher up in class
            # heirarchy? (in ArrayWithDoors, for sure, if i implement that)

            self.robot.moveXY(self.door_center(ij, closed=True))

            zw = self.robot.z0_to_worksurface - self.z0_working_height
            self.robot.moveZ0(zw)

            self.robot.dwell_ms(1000)
            self.robot.moveXY(self.door_center(ij, closed=False))
            self.robot.dwell_ms(1000)
            self.robot.smallPartManipVac(False)

            self.robot.moveZ0(zt)


    def close_door(self, ij):
        """
        Assumes smallPartManipAir is off.
        """
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

            self.robot.smallPartManipVac(True)
            self.robot.moveXY(open_door)
            zw = self.robot.z0_to_worksurface - self.z0_working_height
            self.robot.moveZ0(zw)

            self.robot.dwell_ms(1000)

            self.robot.moveXY(closed_door)
            self.robot.dwell_ms(1000)
            self.robot.smallPartManipVac(False)

            self.robot.moveZ0(zt)


    def door_center(self, ij, closed=False):
        """
        """
        i, j = ij
        assert j == 0, 'This module only has one column.'
        # TODO check using right index
        x, y = self.anchor_center(i, j)

        # TODO calculate better + use central offset definition (in cfg?)
        door_x = x - 4.89 - 80

        # Which side the door is on alternates, about axis that goes through
        # each anchor (fly loading holes). Reflected in y with workspace
        # orientation.

        dy = 10.0 if closed else 14.0
        if i % 2 == 0:
            door_y = y + dy
        else:
            door_y = y - dy

        return (door_x, door_y)


'''
# TODO or will i want / need to namespace it maple.workspace.Workspace?
class ChoiceWorkspace(maple.Workspace):
    """
    """
    pass
'''


def main():
    ###########################################################################
    # Flags
    ###########################################################################
    #random_order = True
    random_order = False
    dry_run = False
    just_right_arena = True

    if just_right_arena and random_order:
        raise ValueError('set random_order to False to use just_right_arena')

    ###########################################################################
    # TODO get config from right place first
    # not sure i want to need to change MAPLE.cfg in experiment dependent manner
    # TODO implement contructor that can also take components of workspace?
    if dry_run:
        robot = None
    else:
        # TODO allow calling constructor w/ no arguments for default config
        robot = maple.robotutil.MAPLE(os.path.join(maple.__path__[0],
            'MAPLE.cfg'))

    '''
    choice_workspace = {
        'left_arena': ChoiceModule(robot, (,)),
        'right_arena': ChoiceModule(robot, (,)),
        'flyplate': maple.module.FlyPlate(robot, (,)),
        'morgue': maple.module.Morgue(robot, (,))
    }
    '''
    # TODO make sure offsets defined from top right of (original) alignment
    # plate work to find the right positions (probably need some offset relative
    # to endstops)

    # Distance from zero defined in alignment_plate.dxf (inside corner of
    # vertical support in top right corner) to z2 (fly) effector, when the robot
    # is at what it considers to be (0,0)
    # TODO calculate? this was eyeballed
    z2_offset = (48.0, 97.5)

    # Measured 45.5 to top of 1/8" alignment plate + 3.175 thickness of that
    # plate.
    robot.z0_to_worksurface = 48.675

    # Silicone seems to just be touching at ~40mm. Silicone extends between
    # metal needle by maybe ~1mm or so.
    robot.z2_to_worksurface = 43.175

    # Measured from tom-f-oconnell/MAPLEHardware/Drawings/alignment_plate.dxf,
    # with construction lines added as necessary to measure from origin to top
    # right corner of the bounding box of each module.
    left_arena = ChoiceModule(robot,
        (382.15 - z2_offset[0], 18.2 - z2_offset[1]))
    right_arena = ChoiceModule(robot,
        (93.65 - z2_offset[0], 18.2 - z2_offset[1]))

    flyplate = maple.module.FlyPlate(robot,
        (321.65 - z2_offset[0], 212.0 - z2_offset[1]))

    morgue = maple.module.Morgue(robot,
        (427.15 - z2_offset[0], 303.8 - z2_offset[1]))

    ###########################################################################
    # Load flies
    ###########################################################################
    # TODO maybe factor into function outside of main, s.t. after the plate is
    # out of flies, the user can just be prompted to reload it before the main
    # loop continues
    while flyplate.has_flies():

        while (not left_arena.is_full()) or (not right_arena.is_full()):

            if just_right_arena and right_arena.is_full():
                break

            if random_order:
                # Takes a fly from the flyplate. It will be held in the fly
                # manipulator effector with vacuum until it is deposited.
                # TODO TODO manage metadata about the fly. probably easiest to
                # take data from a GUI to annotate flies in the wells?
                source_pos = flyplate.get_random()

                # TODO maybe randomly select from all available wells, s.t.
                # there isn't more probability (per well) on wells in more full
                # chambers?
                # TODO just weight choice by # wells free? (would need new
                # func?)
                # TODO fix hack. use dict of modules addressed by name or
                # something.
                arena_to_load = random.choice([x for x in
                    [('left_arena', left_arena), ('right_arena', right_arena)]
                    if not x[1].is_full()])

                print('Trying to load {}'.format(arena_to_load[0]))
                #dest_arena = arena_to_load.__name__

                # Deposits the fly currently in the manipulator into a random
                # well in the behavior arena.
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

        ########################################################################
        # Run the experiment
        ########################################################################
        # TODO maybe don't image both chambers if one is empty?

        #if dry_run:
        print('\nRunning experiment\n')

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

        # TODO also transfer data, start tracking, and (if labelling is
        # automated) do analysis (build that sequence here, or elsewhere and
        # wrap?)

        # TODO need to clear namespace or anything? (test)


        ########################################################################
        # Unload the flies
        ########################################################################
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


if __name__ == '__main__':
    main()
