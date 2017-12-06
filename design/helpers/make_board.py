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

dry_run = False
if dry_run:
    print 'dry run. should not make any modifications.'

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

# in kicad's coordinate system, lower y are higher.
# i would need to change for J<N> with lower N to be higher up (bottom now)
# TODO redo s.t. lower N start on top in future board versions

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

    if not dry_run:
        print_placing('grid', electrode_center)
        electrode.SetPosition(electrode_center)
        #pcb.Add(electrode)


# TODO share w/ electrode_vertices.py break into module? pcbnew func?
def mm_to_nm(mm):
    return int(round(1e6 * mm))

# sets the position of two of the headers, relative to the boundaries of the board
# so that their position is symmetric about the board center
# TODO TODO delete everything defined relative to board edge, and replace w/ nearest
# connector. allows connectors on top and bottom to be aligned despite different edges
# TODO except maybe J3 on bottom?


# should yield a symmetric board
# assuming grid footprint is symmetric about its origin
nearest_grid_center_to_conn_center_mm = 12.6

# TODO TODO print distances from center of nearest grids to center of j1/2 for ceiling
# given that it was layed out w/ 6mm from board edges, then use those values for floor

eda_rect = pcb.GetBoardEdgesBoundingBox()
# still useful for centering with board in x
# although a constant should also do
center = eda_rect.GetCenter()

# using a 10 pin spring connector on floor since more available
# but not using one of the pins, and want to center the top footprint
# TODO make sure this goes in right direction to leave rightmost pin (10) disconnected
offset_x = mm_to_nm(0 if in_ceiling_board else 2.54)

# not clear on why this is necessary, but it is to get the HV pads to line up with
extra_c10_offset_x = mm_to_nm(-1.22)

top_conn = pcb.FindModuleByReference('J2')
bottom_conn = pcb.FindModuleByReference('J1')


# TODO delete me
# was for switching from board edge reference to nearest grid reference
# yielded ~12.6-12.7 -> going with 12.6mm
'''
if in_ceiling_board:
    print 'top conn y pos:', nm_to_mm(top_conn.GetPosition().y)
    print 'top grid center:', kicad_y_for_librecad_y0 - \
        (y0_center + (num_chambers - 1) * y_grid_interval)
    print 'top conn y pos to top grid center:', \
        (kicad_y_for_librecad_y0 - (y0_center + (num_chambers - 1) * \
        y_grid_interval)) - nm_to_mm(top_conn.GetPosition().y)

    print 'bottom conn y pos:', nm_to_mm(bottom_conn.GetPosition().y)
    print 'bottom grid center:', kicad_y_for_librecad_y0 - y0_center
    print 'bottom conn y pos to bottom grid center:', \
        nm_to_mm(bottom_conn.GetPosition().y) - \
        (kicad_y_for_librecad_y0 - y0_center)
'''

# place the top 10 pin connector (between floor and ceiling grids)
top_grid_center_y = kicad_y_for_librecad_y0 - \
    (y0_center + (num_chambers - 1) * y_grid_interval)
#if dry_run:
#    print 'top grid center:', top_grid_center_y

top_center = pcbnew.wxPoint(center.x + offset_x + extra_c10_offset_x, \
    mm_to_nm(top_grid_center_y - nearest_grid_center_to_conn_center_mm))

print_placing('top connector', \
    pcbnew.wxPointMM(nm_to_mm(top_center.x), nm_to_mm(top_center.y)))
if not dry_run:
    top_conn.SetPosition(top_center)


# place the bottom 10 pin connector (between floor and ceiling grids)
bottom_grid_center_y = kicad_y_for_librecad_y0 - y0_center
#if dry_run:
#    print 'bottom grid center:', bottom_grid_center_y

bottom_center = pcbnew.wxPoint(center.x + offset_x + extra_c10_offset_x, \
    mm_to_nm(bottom_grid_center_y + nearest_grid_center_to_conn_center_mm))

print_placing('bottom connector', \
    pcbnew.wxPointMM(nm_to_mm(bottom_center.x), nm_to_mm(bottom_center.y)))
if not dry_run:
    bottom_conn.SetPosition(bottom_center)


# place the 25 pin DSUB connector (to the control / measurement board)
# beneath (and relative to) the lower 10 pin connector
if not in_ceiling_board:
    j3 = pcb.FindModuleByReference('J3')

    # TODO maybe don't use bounding box...
    # (it could be offset a little and overestimate w.r.t. pads)

    # the origin of the DSUB25 footprint I'm using is its pin 1
    # so I need to compensate to set the position of the center of the pads

    # measured as x difference between pin 1 and 7
    dsub_x_offset = 16.6200
    # measured as half y difference between pin 1 and pin beneath it
    dsub_y_offset = 1.4200

    # offsets that are necessary for alignment, but that I didn't take the time
    # to understand
    extra_x_offset = mm_to_nm(-1.27)
    extra_y_offset = mm_to_nm(-3.6)
    
    # J3 goes on the bottom
    j1_bbox = bottom_conn.GetBoundingBox()
    # origin is at the top
    j3_y = j1_bbox.GetBottom() + (j3.GetPosition().y - \
        j3.GetBoundingBox().GetTop()) + mm_to_nm(dsub_y_offset)

    j3_pos = pcbnew.wxPoint(bottom_conn.GetPosition().x + \
        mm_to_nm(dsub_x_offset) + extra_x_offset, j3_y + extra_y_offset)

    #print 'bottom of J1 bounding box:', j1_bbox.GetBottom()

    if not dry_run:
        j3.SetPosition(j3_pos)
        print_placing('offboard connector', \
            pcbnew.wxPointMM(nm_to_mm(j3_pos.x), nm_to_mm(j3_pos.y)))


# TODO only if a title block isn't set?
tb = pcbnew.TITLE_BLOCK()

if not dry_run:
    print 'setting title block'
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
