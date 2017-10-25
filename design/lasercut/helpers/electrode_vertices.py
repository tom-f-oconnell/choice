#!/usr/bin/env python

from __future__ import division
import numpy as np

# the electrode with one trace down the center of the arena
mirror = True

# not the exact same as the electrode with a bus down the center
# there are two disconnected electrodes like these per chamber
# but only one common high voltage electrode
include_other_electrode = True
rightmost_tooth_from_top = False

# all units in mm unless otherwise noted
center_x = 125.0
center_y = 38.7450
# maybe a little less?
min_half_length = 25
min_width = 6.5
between_electrodes = 1
electrode_width = 1

connections_between_grids = False
y_between_grid_centers = 22.50

# only does something if connections_between_grids is False
# otherwise there is a bus going down the whole center anyway
extra_y_center_tooth = 3

# derived quantities
tooth_length = min_width + between_electrodes
width_between_backbones = min_width + (2.0 * between_electrodes)
y_backbone = center_y - (width_between_backbones / 2.0)
y_tooth_tip = center_y + (width_between_backbones / 2.0) - between_electrodes
x_between_backbone_vertices = electrode_width + (2.0 * between_electrodes)
#y_grid_total_extent = width_between_backbones + (2.0 * electrode_width)

if include_other_electrode:
    opposing_backbone =  y_backbone + width_between_backbones
    opposing_tooth_tip = y_backbone + between_electrodes

# we will start with points that intersect center traces
origin_x = center_x - (electrode_width / 2.0)
curr_x = origin_x
points = []

# top left, at intersection with bottom edge of grid unit above
if connections_between_grids:
    points.append([curr_x, y_backbone + (y_between_grid_centers - electrode_width)])
    curr_x += electrode_width
    points.append([curr_x, y_backbone + (y_between_grid_centers - electrode_width)])

else:
    points.append([curr_x, y_tooth_tip + extra_y_center_tooth])
    curr_x += electrode_width
    points.append([curr_x, y_tooth_tip + extra_y_center_tooth])

if include_other_electrode:
    # origin for this will be topleft-most vertex
    other_electrode_points = [[curr_x + between_electrodes, \
        opposing_backbone + electrode_width]]

# TODO maybe take into account that interleaved comb will add one electrode tooth
# one one end?
while curr_x < (center_x + min_half_length):
    if include_other_electrode:
        opp_x = curr_x + between_electrodes
        other_electrode_points.append([opp_x, opposing_tooth_tip])
        opp_x += electrode_width
        other_electrode_points.append([opp_x, opposing_tooth_tip])
        other_electrode_points.append([opp_x, opposing_backbone])
        opp_x += x_between_backbone_vertices 
        other_electrode_points.append([opp_x, opposing_backbone])

    # two points along backbone
    points.append([curr_x, y_backbone])
    curr_x += x_between_backbone_vertices 
    points.append([curr_x, y_backbone])

    # two at top edge of tooth
    points.append([curr_x, y_tooth_tip])
    curr_x += electrode_width
    points.append([curr_x, y_tooth_tip])
    
# should finish with two at top of tooth, and then add 
# the two vertices along the opposite edge of the backbone
y_backbone_bottom = y_backbone - electrode_width
points.append([curr_x, y_backbone_bottom])

# making two points here for easier manual modification / joining
points.append([origin_x + electrode_width, y_backbone_bottom])
points.append([origin_x, y_backbone_bottom])

# TODO not sure how i want to finish off opposing electrode yet
# give it another tooth, or not?
if include_other_electrode:
    if rightmost_tooth_from_top:
        other_electrode_points.append([opp_x, opposing_tooth_tip])
        opp_x += electrode_width
        other_electrode_points.append([opp_x, opposing_tooth_tip])

    other_electrode_points.append([opp_x, opposing_backbone + electrode_width])
    other_electrode_points.append(other_electrode_points[0])

# finish up the central electrode
if not mirror:
    # loop will be closed at point high point to the left of center_x
    initial_point = points[0]

else: 
    mirrored_points = []
    # excluding the first and last points, which would be redundant
    for p in reversed(points[1:-1]):
        # mirror over x=center_x
        mirrored_points.append([2*center_x - p[0], p[1]])

    for p in mirrored_points:
        points.append(p)

    # loop will be closed at first vertex listed
    # that is the the right of center_y
    initial_point = points[1]

# initial point again to close the loop
points.append(initial_point)

# TODO also include / copy over other features of the pcb dxf to use as exclude
# regions for footprint?
# break those layers into own dxf? (would want to keep it in sync with master dxf though...)

# command to generate this polyline in librecad
# you may want to manually connect the end to some other feature
print 'Copy the output below this line, look for the command window in LibreCAD,' + \
    ' and find the "Paste Multiple Commands" option in the dropdown. Then press <Esc> ' + \
    'to finish drawing the polyline.'

print 'polyline'
for p in points:
    print '{}, {}'.format(*p)

if include_other_electrode:
    print '\npolyline'
    for p in other_electrode_points:
        print '{}, {}'.format(*p)

    if mirror:
        print '\npolyline'
        for p in other_electrode_points:
            print '{}, {}'.format(2*center_x - p[0], p[1])

# TODO also print commands for rotation of half of one half grid to create both
# electrodes for a half grid
# and commands to mirror that to create a full grid unit

# current way blocks were generated:
# this code -> polyline that goes in one_electrode
# this was rotated 180 degrees and moved to have two opposing electrodes
# -> new block called half_chamber_grid
# that was mirrored about line down center of arena -> chamber_grid
# chamber_grid was copied to each of 8 positions

