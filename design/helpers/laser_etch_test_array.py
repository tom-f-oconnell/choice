#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

import os
from subprocess import Popen

# TODO fix
# options are 'openscad' or 'freecad', but 'openscad' can't do most of the work
# 'ezdxf'
# because it doesn't seem to be able to export lines with color (solid uses scad)
intermediate = 'ezdxf'

if intermediate == 'openscad':
    import solid as s

elif intermediate == 'ezdxf':
    import ezdxf
    dxf = ezdxf.new('R2013')
    msp = dxf.modelspace()

###############################################################################
radius_mm = 1.25

# might want to make sure this is large enough
# thoug we would want to etch at this pitch or finer
between_circles_mm = 1

n_colors = 3
n_intensities = 16

segments_per_circle = 32
###############################################################################

assert n_colors <= 3, 'only export of 3 colors supported for now (RGB)'

# TODO how to programmatically control both speed and power?
# pick n colors = n speeds and vary power?
# is it even worth manipulating them independently?
# alternatives?
# TODO can solid scad_render a list or what? some kind of list type?

if intermediate == 'openscad':
    # generate the solidpython representation of the array we want
    circles = []

for i in range(n_colors):
    c = [0, 0, 0]
    c[i] = 1
    x_offset = (2*radius_mm + between_circles_mm) * i

    # TODO should i change the intensity w/ alpha or color level?
    for j in range(n_intensities):
        y_offset = (2*radius_mm + between_circles_mm) * j
        alpha = (j + 1) / n_intensities

        # color argument: 0=r, 1=g, 2=b, 3=alpha
        if intermediate == 'openscad':
            # TODO move shared calculations out of if
            circles.append(s.color(c + [alpha])(\
                s.translate([x_offset, y_offset, 0])(s.circle(radius_mm))))

        elif intermediate == 'ezdxf':
            # 1=r,3=g,5=b(,2=y,4=c,6=m)
            autocad_color_index = (2*i) + 1
            msp.add_circle(center=(x_offset, y_offset), radius=radius_mm, \
                dxfattribs={'color': autocad_color_index, \
                'transparency': int(round(alpha * 255))})


prefix = '.'.join(os.path.split(__file__)[1].split('.')[:-1])


if intermediate == 'openscad':
    # convert this to OpenSCAD format
    outfile = prefix + '.scad'
    with open(outfile, 'w') as f:
        for i, c in enumerate(circles):
            # TODO would it make sense to add iterable rendering for solidpython?
            # (i.e. does it make sense to have a set of top level 
            #  objects(?) in openscad?)
            if i == 0:
                scad = s.scad_render(c, \
                    file_header='$fn = {};'.format(segments_per_circle))
            else:
                scad = s.scad_render(c)
            f.write(scad)

    # TODO need to specify units somewhere?

    # call openscad to turn the .scad file into a dxf
    # TODO maybe just insert the special variable(s) here? (e.g. $fn)
    # TODO don't hang open
    Popen(['openscad', '-o', prefix + '.dxf', outfile])

elif intermediate == 'ezdxf':
    dxf.saveas(prefix + '.dxf')

