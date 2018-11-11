#!/usr/bin/env python3

"""
A script to control the MAPLE robot to load and unload flies from the behavior
chambers, running experiments in between.
"""

from __future__ import print_function
from __future__ import division

import random

import maple
# TODO also use this api in other places i call roslaunch w/ subprocess
# (roi_finder might be the only other place I do that?)
import roslaunch


class ChoiceModule(maple.module.Array):
    """
    """
    def __init__(self, robot, offset):
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


    def get(self, xy, ij):
        """
        """
        self.robot.flyManipVac(True)
        self.robot.flyManipAir(False)
        # TODO add support for larger valve? (just rewire into old vac?)

        self.open_door(ij)

        # Anchors are defined as centers of fly loading ports here.
        self.robot.moveXY(xy)
        # TODO TODO lower to working height

        self.robot.dwell(5)
        # TODO TODO move back up to travel height

        self.close_door(ij)

        # TODO move back up to travel height


    def put(self, xy, ij):
        """
        Assumes flyManipVac is on and flyManipAir is off, otherwise fly could
        have been able to escape.
        """
        # how much time will i have before flies start to escape? test
        self.open_door(ij)

        self.robot.moveXY(xy)
        # TODO TODO lower to working height

        self.robot.flyManipVac(False)
        self.robot.flyManipAir(True)
        self.robot.dwell(3)
        self.robot.flyManipAir(False)

        # again, test escape rate
        self.close_door(ij)


    # TODO would doors like these be a common enough motif to include their
    # positions (optionally?) in Array constructor, and move these fns up there?
    # maybe an ArrayWithDoors class?
    def open_door(self, ij):
        """
        Assumes smallPartManipAir is off.
        """
        self.robot.smallPartManipVac(True)
        # TODO require working height for this effector higher up in class
        # heirarchy? (in ArrayWithDoors, for sure, if i implement that)

        # TODO move to working height
        self.robot.move self.z0_working_height

        self.robot.moveXY(self.door_center(ij, closed=True))
        self.robot.dwell(1)
        # TODO move back to travel height
        self.robot.moveXY(self.door_center(ij, closed=False))
        self.robot.dwell(1)
        self.robot.smallPartManipVac(False)
        # TODO move back to travel height


    def close_door(self, ij):
        """
        Assumes smallPartManipAir is off.
        """
        self.robot.smallPartManipVac(True)
        self.robot.moveXY(self.door_center(ij, closed=False))
        # TODO move to working height

        self.robot.dwell(1)
        # TODO move back to travel height

        self.robot.moveXY(self.door_center(ij, closed=True))
        self.robot.dwell(1)
        self.robot.smallPartManipVac(False)
        # TODO move back to travel height


    def door_center(self, ij, closed=False):
        """
        """
        i, j = ij
        # should i stick to (row, col)? might be more natural?
        assert i == 1, 'This module only has one column.'
        # TODO check using right index
        x, y = self.anchor_center(i, j)

        # Which side the door is on alternates, about axis that goes through
        # each anchor (fly loading holes). Reflected in y with workspace
        # orientation.
        door_x = x - 4.89

        dy = 10.0 if closed else 14.0
        if j % 2 == 0:
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
    random_order = True

    ###########################################################################
    # TODO get config from right place first
    # not sure i want to need to change MAPLE.cfg in experiment dependent manner
    # TODO implement contructor that can also take components of workspace?
    robot = maple.MAPLE()  

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

    # Measured from tom-f-oconnell/MAPLEHardware/Drawings/alignment_plate.dxf,
    # with construction lines added as necessary to measure from origin to top
    # right corner of the bounding box of each module.
    left_arena = ChoiceModule(robot, (382.15, 18.2))
    right_arena = ChoiceModule(robot, (93.65, 18.2))
    flyplate = maple.module.FlyPlate(robot, (321.65, 212.0))
    morgue = maple.module.Morgue(robot, (427.15, 303.8))

    ###########################################################################
    # Load flies
    ###########################################################################
    # TODO maybe factor into function outside of main, s.t. after the plate is
    # out of flies, the user can just be prompted to reload it before the main
    # loop continues
    while flyplate.has_flies():

        while (not left_arena.is_full()) or (not right_arena.is_full()):
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
                arena_to_load = random.choice([x for x in
                    [left_arena, right_arena] if not x.is_full()])

                dest_arena = arena_to_load.__name__
                # Deposits the fly currently in the manipulator into a random
                # well in the behavior arena.
                dest_pos = arena_to_load.put_random()

            else:
                raise NotImplementedError

            if flyplate.is_empty():
                break

        ########################################################################
        # Run the experiment
        ########################################################################
        # TODO maybe don't image both chambers if one is empty?

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
                morgue.put()

            else:
                raise NotImplementedError


if __name__ == '__main__':
    main()
