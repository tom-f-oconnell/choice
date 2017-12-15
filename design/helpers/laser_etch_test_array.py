#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

import os
import solid as s
from subprocess import Popen

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


# generate the solidpython representation of the array we want
circles = []
for i in range(n_colors):
    c = [0, 0, 0]
    c[i] = 1
    x_offset = (2*radius_mm + between_circles_mm) * i

    # TODO should i change the intensity w/ alpha or color level?
    for j in range(n_intensities):
        y_offset = (2*radius_mm + between_circles_mm) * j

        # color argument: 0=r, 1=g, 2=b, 3=alpha
        circles.append(s.color(c + [(j + 1) / n_intensities])(\
            s.translate([x_offset, y_offset, 0])(s.circle(radius_mm))))


# convert this to OpenSCAD format
prefix = '.'.join(os.path.split(__file__)[1].split('.')[:-1])
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

# postprocessing to improve chances it cuts reasonably? (doesn't jump around, etc)

