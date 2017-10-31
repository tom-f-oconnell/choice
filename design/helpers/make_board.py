#!/usr/bin/env python

from __future__ import division
import os
from os.path import split, join, abspath, realpath
import sys
import pcbnew
from pcbnew import PCB_IO as io
import numpy as np

# TODO why did this seem to behave differently just upon re-running this?
# (all from within KiCAD pcbnew scripting window, via "import make_board")

if __file__[-1] == 'c':
    this_py_file = __file__[:-1]
else:
    this_py_file = __file__

pcb_base_dir = abspath(join(split(split(realpath(this_py_file))[0])[0], 'pcb'))
print pcb_base_dir

# TODO maybe have a pcb file with everything but the copper grids layed out?
# and then that can be loaded, populated with the grids, and resaved under
# a different filename?

'''
# TODO what is the proper file extension for LoadBoard / SaveBoard?
# .kicad_pcb or .pro? other?
pcb_filename = os.path.join(pcb_base_dir, 'shock_floor.kicad_pcb')
if os.path.exists(pcb_filename):
    print '{} exists! Delete or rename it before running this ' + \
        'script.'.format(pcb_filename)
    sys.exit()
'''

#footprint_lib_dir = os.path.join(pcb_base_dir, 'footprints.pretty')

# TODO how does GetBoard behave if kicad isn't running?
#pcb = pcbnew.BOARD()
pcb = pcbnew.GetBoard()

# mm
x_center = 125.0
y0_center = 16.250
num_chambers = 8
y_grid_interval = 22.4806



# (in KiCAD)
# top of imported librecad dxf seems to be at |minimum y_coord in librecad|
# increasing y coordinates are down
# TODO make it so i don't make to manually calculate this...
kicad_y_for_librecad_y0 = 216.500 - 6.5

for j, y in enumerate(np.linspace(y0_center, y0_center + num_chambers * \
    y_grid_interval, num=num_chambers, endpoint=False)):

    # not sure how to build connectivity after placing components, so i'll just 
    # load netlist manually, and then move components into place, selecting them
    # with their reference
    #electrode = io().FootprintLoad(footprint_lib_dir, 'electrode')
    electrode = pcb.FindModuleByReference('J{}'.format(j+4))

    # TODO this clone didn't seem to work, but way to add multiples without reloading?
    #pcb.Add(electrode.clone())

    print 'placing grid centered at ({}, {})'.format(x_center, float(y))
    electrode.SetPosition(pcbnew.wxPointMM(x_center, \
        float(kicad_y_for_librecad_y0 - y)))

    #pcb.Add(electrode)

