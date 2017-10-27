#!/usr/bin/env python

from __future__ import division
import os
import sys
import pcbnew
from pcbnew import PCB_IO as io


pcb_base_dir = os.path.abspath('../pcb')

# TODO maybe have a pcb file with everything but the copper grids layed out?
# and then that can be loaded, populated with the grids, and resaved under
# a different filename?

# TODO what is the proper file extension for LoadBoard / SaveBoard?
# .kicad_pcb or .pro? other?
pcb_filename = os.path.join(pcb_base_dir, 'shock_floor.kicad_pcb')
if os.path.exists(pcb_filename):
    print '{} exists! Delete or rename it before running this ' + \
        'script.'.format(pcb_filename)
    sys.exit()

footprint_lib_dir = os.path.join(pcb_base_dir, 'choice.pretty')
electrode = io().FootprintLoad(footprint_lib_dir, 'electrode')

# TODO how does GetBoard behave if kicad isn't running?
pcb = pcbnew.BOARD()

#pcb.Add(electrode.clone())
pcb.Add(electrode)

print dir(pcb)

