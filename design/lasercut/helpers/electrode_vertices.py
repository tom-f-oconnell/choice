#!/usr/bin/env python

from __future__ import division
import numpy as np

# all units in mm unless otherwise noted
center_x = 125.0
center_y = 38.7450
# maybe a little less?
min_half_length = 25
min_width = 6.5
between_electrodes = 1
electrode_width = 1
y_between_grid_centers = 22.50

# derived quantities
tooth_length = min_width + between_electrodes
width_between_backbones = min_width + (2.0 * between_electrodes)
y_backbone = center_y - (width_between_backbones / 2.0)
y_tooth_tip = center_y + (width_between_backbones / 2.0) - between_electrodes
x_between_backbone_vertices = electrode_width + (2.0 * between_electrodes)
#y_grid_total_extent = width_between_backbones + (2.0 * electrode_width)

# we will start with points that intersect center traces
origin_x = center_x + (between_electrodes / 2.0)
curr_x = origin_x
points = []

# top left, at intersection with bottom edge of grid unit above
initial_point = [curr_x, y_backbone + (y_between_grid_centers - electrode_width)]
points.append(initial_point)
curr_x += electrode_width
points.append([curr_x, y_backbone + (y_between_grid_centers - electrode_width)])

# TODO maybe take into account that interleaved comb will add one electrode tooth
# one one end?
while curr_x < (center_x + min_half_length):
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

# initial point again to close a loop
points.append(initial_point)

# command to generate this polyline in librecad
# you may want to manually connect the end to some other feature
print 'Copy the output below this line, look for the command window in LibreCAD,' + \
    ' and find the "Paste Multiple Commands" option in the dropdown. Then press <Esc> ' + \
    'to finish drawing the polyline.'

print 'polyline'
for p in points:
    print '{}, {}'.format(*p)

# TODO also print commands for rotation of half of one half grid to create both
# electrodes for a half grid
# and commands to mirror that to create a full grid unit

# current way blocks were generated:
# this code -> polyline that goes in one_electrode
# this was rotated 180 degrees and moved to have two opposing electrodes
# -> new block called half_chamber_grid
# that was mirrored about line down center of arena -> chamber_grid
# chamber_grid was copied to each of 8 positions

