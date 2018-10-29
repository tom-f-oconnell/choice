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
    left_arena = ChoiceModule(robot, (,)),
    right_arena = ChoiceModule(robot, (,)),
    flyplate = maple.module.FlyPlate(robot, (,)),
    morgue = maple.module.Morgue(robot, (,))

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
