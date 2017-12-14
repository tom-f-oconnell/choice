#!/usr/bin/env python

# TODO what was this for again? document

from __future__ import division

# as usual, all units in mm

# facts
holes_center_x = 125
bottom_hole_center_y = 9.7274
top_hole_center_y = 180.2620

# goals
width = 56
length_beyond_hole_center = 12

left_edge = holes_center_x - width / 2
bottom_edge = bottom_hole_center_y - length_beyond_hole_center 
print 'bottom left corner at {}, {}'.format(left_edge, bottom_edge)

right_edge = holes_center_x + width / 2
top_edge = top_hole_center_y + length_beyond_hole_center 
print 'top right corner at {}, {}'.format(right_edge, top_edge)

