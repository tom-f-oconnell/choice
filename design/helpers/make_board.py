#!/usr/bin/env python

from __future__ import division
import os
from os.path import split, join, abspath, realpath
import sys
import pcbnew
from pcbnew import PCB_IO as io
import numpy as np
import datetime
# TODO git

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


max_if_floor = 3 + num_chambers
# will be None if ceiling board
# (or this and even lower reference #s will be None if footprints not yet placed)
floor_or_ceiling_indicator = pcb.FindModuleByReference('J{}'.format(max_if_floor))
if floor_or_ceiling_indicator is None:
    in_ceiling_board = True
else:
    in_ceiling_board = False


def nm_to_mm(nm):
    return nm / float(1e6)

def print_placing(name, center):
    # x and y in wxPointMM are still stored in nm
    print 'placing {} centered at ({}, {})'.format(name, \
        nm_to_mm(center.x), nm_to_mm(center.y))

for j, y in enumerate(np.linspace(y0_center, y0_center + num_chambers * \
    y_grid_interval, num=num_chambers, endpoint=False)):

    # not sure how to build connectivity after placing components, so i'll just 
    # load netlist manually, and then move components into place, selecting them
    # with their reference
    #electrode = io().FootprintLoad(footprint_lib_dir, 'electrode')
    # TODO count # connectors & assume all at end? or renumber and assume they
    # are at beginning? maybe take # as a parameter?
    electrode = pcb.FindModuleByReference('J{}'.format(j + \
        (3 if in_ceiling_board else 4)))

    # TODO this clone didn't seem to work, but way to add multiples without reloading?
    #pcb.Add(electrode.clone())

    electrode_center = pcbnew.wxPointMM(x_center, \
        float(kicad_y_for_librecad_y0 - y))

    print_placing('grid', electrode_center)
    electrode.SetPosition(electrode_center)

    #pcb.Add(electrode)


# TODO share w/ electrode_vertices.py break into module? pcbnew func?
def mm_to_nm(mm):
    return int(round(1e6 * mm))

# sets the position of two of the headers, relative to the boundaries of the board
# so that their position is symmetric about the board center
board_edge_x_to_center_mm = 23
board_edge_y_to_center_mm = 7
eda_rect = pcb.GetBoardEdgesBoundingBox()

# value returned should be an integer in nm
center = eda_rect.GetCenter()

# using a 10 pin spring connector on floor since more available
# but not using one of the pins, and want to center the top footprint
offset_x = mm_to_nm(0 if in_ceiling_board else 2.54)

top = eda_rect.GetTop()
top_conn = pcb.FindModuleByReference('J2')
top_center = pcbnew.wxPoint(center + offset_x, top + mm_to_nm(board_edge_y_to_center_mm))
top_conn.SetPosition(top_center)
print_placing('top connector', \
    pcbnew.wxPointMM(nm_to_mm(top_center.x), nm_to_mm(top_center.y)))

bottom = eda_rect.GetBottom()
bottom_conn = pcb.FindModuleByReference('J1')
# TODO is it by center?
bottom_center = pcbnew.wxPoint(center + offset_x, bottom - mm_to_nm(board_edge_y_to_center_mm))
bottom_conn.SetPosition(bottom_center)
print_placing('bottom connector', \
    pcbnew.wxPointMM(nm_to_mm(bottom_center.x), nm_to_mm(bottom_center.y)))


# TODO also place J3 just for completeness? it's basically just the routing left
# after that...
if not in_ceiling_board:
    to_control_conn = pcb.FindModuleByReference('J3')

    # J3 goes on the bottom
    j1_bbox = bottom_conn.GetBoundingBox()
    # origin is at the top
    j3_y = j1_bbox.GetBottom() + to_control_conn.GetBoundingBox().GetHeight() / 2
    
    j3_pos = pcbnew.wxPoint(center + offset_x, j3_y)
    bottom_conn.SetPosition(bottom_center)
    print_placing('offboard connector', \
        pcbnew.wxPointMM(nm_to_mm(bottom_center.x), nm_to_mm(bottom_center.y)))


# TODO include ceiling / floor
print 'setting title block'
# TODO only if a title block isn't set?
tb = pcbnew.TITLE_BLOCK()
tb.SetTitle('{} chamber shock conditioning {} grid'.format(num_chambers, \
        'ceiling' if in_ceiling_board else 'floor'))
tb.SetCompany('Hong Lab @ Caltech')
tb.SetDate(datetime.date.today().strftime('%d-%m-%Y'))
# TODO git
#tb.SetRevision()
# TODO way to set extent of title block to cover whole schematic?
# does title block include the outer border?
# TODO why does this not seem to be displaying?
pcb.SetTitleBlock(tb)
