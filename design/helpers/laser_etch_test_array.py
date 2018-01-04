#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

import os
import ezdxf

dxf = ezdxf.new('R2013')
msp = dxf.modelspace()

###############################################################################
# for concentric squares
inner_width_mm = 2
border_width_mm = 0.6
between_mm = 2

#just_black = True

#n_colors = 3
# none of the drawing programs i use (inkscape / coreldraw) seem to recognize
# the transparency DXF attribute
n_intensities = 16
max_intensity = 255
###############################################################################

# TODO how to programmatically control both speed and power? (looks like i can't)
# resolution?
# pick n colors = n speeds and vary power?
# is it even worth manipulating them independently?
# alternatives?

# length of unit making up one side of concentric square shape
unit_length = border_width_mm + inner_width_mm
def side_rect(top_left, long_vertical=True):
    def off(p, x, y):
        return (p[0] + x, p[1] + y)

    if long_vertical:
        return [top_left, off(top_left, border_width_mm, 0), \
            off(top_left, 0, unit_length), \
            off(top_left, border_width_mm, unit_length)]
    else:
        return [top_left, off(top_left, 0, border_width_mm), \
            off(top_left, unit_length, 0), \
            off(top_left, unit_length, border_width_mm)]

base_coords = [side_rect((0, 0)), side_rect((unit_length, border_width_mm)), \
    side_rect((border_width_mm, 0), long_vertical=False), \
    side_rect((0, unit_length), long_vertical=False)]

# TODO provide option to specify x and y dims of array
for i in range(1):
    x_offset = (inner_width_mm + 2*border_width_mm + between_mm) * i
    for j in range(n_intensities):
        y_offset = (inner_width_mm + 2*border_width_mm + between_mm) * j
        level = int(round(max_intensity * (j + 1) / n_intensities))
        print(level)

        # 1=r,3=g,5=b(,2=y,4=c,6=m)
        autocad_color_index = (2*i) + 1
        
        for shape_coords in base_coords:
            offset_coords = [(c[0] + x_offset, c[1] + y_offset) for c in shape_coords]
            # TODO ok if points is a list of tuples?
            s = msp.add_solid(offset_coords)
            # TODO is color thing working? would it work any better with truecolor?
            # just find a function to convert rgb to autocad color index 
            # and use only r12 features?
            s.rgb = (level, level, level)

prefix = '.'.join(os.path.split(__file__)[1].split('.')[:-1])
dxf.saveas(prefix + '.dxf')

