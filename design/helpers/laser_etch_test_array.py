#!/usr/bin/env python

from __future__ import division
import os
import numpy as np
import solid as s

outfile = '.'.join(os.path.split(__file__)[1].split('.')[:-1]) + '.scad'

radius_mm = 5

n_intensities = 16
min_color = 0
max_color = 1

n_colors = 2

# TODO how to programmatically control both speed and power?
# pick n colors = n speeds and vary power?
# is it even worth manipulating them independently?
# alternatives?

# 0=r, 1=g, 2=b, 3=alpha
varied_dimension = 2

# TODO can solid scad_render a list or what? some kind of list type?


with open(outfile, 'w') as f:
    for i in range(n_colors):
        for j in range(n_intensities):
        f.write(s.color(s.circle(radius_mm)))
