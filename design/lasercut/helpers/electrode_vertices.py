#!/usr/bin/env python

from __future__ import division
import numpy as np
import os

def electrode_vertices():
    # the electrode with one trace down the center of the arena
    mirror = True

    # not the exact same as the electrode with a bus down the center
    # there are two disconnected electrodes like these per chamber
    # but only one common high voltage electrode
    include_other_electrode = True
    rightmost_tooth_from_top = False

    # all units in mm unless otherwise noted
    center_x = 125.0
    center_y = 38.7450
    # maybe a little less?
    min_half_length = 25
    min_width = 6.5
    between_electrodes = 1
    electrode_width = 1

    connections_between_grids = False
    y_between_grid_centers = 22.50

    # only does something if connections_between_grids is False
    # otherwise there is a bus going down the whole center anyway
    extra_y_center_tooth = 3

    # derived quantities
    tooth_length = min_width + between_electrodes
    width_between_backbones = min_width + (2.0 * between_electrodes)
    y_backbone = center_y - (width_between_backbones / 2.0)
    y_tooth_tip = center_y + (width_between_backbones / 2.0) - between_electrodes
    x_between_backbone_vertices = electrode_width + (2.0 * between_electrodes)
    #y_grid_total_extent = width_between_backbones + (2.0 * electrode_width)

    if include_other_electrode:
        opposing_backbone =  y_backbone + width_between_backbones
        opposing_tooth_tip = y_backbone + between_electrodes

    # we will start with points that intersect center traces
    origin_x = center_x - (electrode_width / 2.0)
    curr_x = origin_x
    points = []

    # top left, at intersection with bottom edge of grid unit above
    if connections_between_grids:
        points.append([curr_x, y_backbone + (y_between_grid_centers - electrode_width)])
        curr_x += electrode_width
        points.append([curr_x, y_backbone + (y_between_grid_centers - electrode_width)])

    else:
        points.append([curr_x, y_tooth_tip + extra_y_center_tooth])
        curr_x += electrode_width
        points.append([curr_x, y_tooth_tip + extra_y_center_tooth])

    if include_other_electrode:
        # origin for this will be topleft-most vertex
        other_electrode_points = [[curr_x + between_electrodes, \
            opposing_backbone + electrode_width]]

    # TODO maybe take into account that interleaved comb will add one electrode tooth
    # one one end?
    while curr_x < (center_x + min_half_length):
        if include_other_electrode:
            opp_x = curr_x + between_electrodes
            other_electrode_points.append([opp_x, opposing_tooth_tip])
            opp_x += electrode_width
            other_electrode_points.append([opp_x, opposing_tooth_tip])
            other_electrode_points.append([opp_x, opposing_backbone])
            opp_x += x_between_backbone_vertices 
            other_electrode_points.append([opp_x, opposing_backbone])

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

    # TODO not sure how i want to finish off opposing electrode yet
    # give it another tooth, or not?
    if include_other_electrode:
        if rightmost_tooth_from_top:
            other_electrode_points.append([opp_x, opposing_tooth_tip])
            opp_x += electrode_width
            other_electrode_points.append([opp_x, opposing_tooth_tip])

        other_electrode_points.append([opp_x, opposing_backbone + electrode_width])
        other_electrode_points.append(other_electrode_points[0])

    # finish up the central electrode
    if not mirror:
        # loop will be closed at point high point to the left of center_x
        initial_point = points[0]

    else: 
        mirrored_points = []
        # excluding the first and last points, which would be redundant
        for p in reversed(points[1:-1]):
            # mirror over x=center_x
            mirrored_points.append([2*center_x - p[0], p[1]])

        for p in mirrored_points:
            points.append(p)

        # loop will be closed at first vertex listed
        # that is the the right of center_y
        initial_point = points[1]

    # initial point again to close the loop
    points.append(initial_point)
    
    polylines = [points]
    if include_other_electrode:
        polylines.append(other_electrode_points)

        if mirror:
            mirrored_other_points = []
            for p in other_electrode_points:
                mirrored_other_points.append([2*center_x - p[0], p[1]])
            polylines.append(mirrored_other_points)

    return polylines

# TODO also include / copy over other features of the pcb dxf to use as exclude
# regions for footprint?
# break those layers into own dxf? (would want to keep it in sync with master dxf though...)

def as_librecad_commands(polylines):
    # command to generate this polyline in librecad
    # you may want to manually connect the end to some other feature
    print 'Copy the output below this line, look for the command window in LibreCAD,' + \
        ' and find the "Paste Multiple Commands" option in the dropdown. Then press <Esc> ' + \
        'to finish drawing the polyline.'

    for polyline in polylines:
        print '\npolyline'
        for p in polyline:
            print '{}, {}'.format(*p)


def as_dxf(polylines, filename=''):
    raise NotImplementedError


def as_eagle_footprint(polylines, filename=''):
    raise NotImplementedError


def as_kicad_mod(polylines, filename='../../pcb/choice.pretty/electrode.kicad_mod'):
    import pcbnew
    from pcbnew import PCB_IO as io
    # TODO check for library through some pcbnew api call? / catch creation error?
    footprint_lib_dir = os.path.split(os.path.abspath(filename))[0]
    if not os.path.exists(footprint_lib_dir):
        # TODO any properties i want to pass?
        io().FootprintLibCreate(footprint_lib_dir)

    # seems to only take a module or board argument,
    # but don't think i want either of those
    # TODO is this None thing going to cause problems later?
    footprint = pcbnew.MODULE(None)
    footprint.SetDescription('Electrodes for shocking either side of one ' + \
        'behavior chamber, for conditioning Drosophila to avoid odors ' + \
        'paired with the shock.')

    # TODO which layers are top and bottom copper?
    layer_num = 0
    assert pcbnew.IsCopperLayer(layer_num) and pcbnew.IsValidLayer(layer_num) \
        and pcbnew.IsFrontLayer(layer_num)

    def mm_to_nm(mm):
        return int(round(1e6 * mm))

    for pl in polylines:
        # TODO advantages to using any one of zone_container / d_pad / track?
        # i assume it should be one of these (or include at least one) as they are
        # board_connected_item(s), and i would want this to count as connected
        # TODO can't seem to put zones in modules, based on apparent BOARD requirement
        # to construct one? and can't pass None, is there a const for no parent?
        #track = pcbnew.TRACK(footprint)
        pad = pcbnew.D_PAD(footprint)
        # work for polygon?
        pad.SetShape(pcbnew.PAD_SHAPE_CUSTOM)
        #poly = pcbnew.SHAPE_POLY_SET()
        #poly.NewOutline()

        last_x = None
        last_y = None
        for ic, p in enumerate(pl):
            x, y = map(mm_to_nm, p)
            #poly.Append(x, y)

            if not last_x is None:
                pad.AddPrimitive(pcbnew.wxPoint(last_x, last_y), \
                    pcbnew.wxPoint(x, y), 0)

            last_x = x
            last_y = y

        # TODO reasons not to set the size based on the GetBoundingBox?
        # TODO what does thru_hole specifier mean?
        # TODO remove mask layer?
        # TODO how to fill the outline?

        '''
        thickness = 0
        pad.AddPrimitive(poly, thickness)
        '''
        #pad.BuildPadShapePoylgon(poly, 0, 0, 0)

        #assert cpl.GetClosed()
        #cpl.Hatch()
        # how to set to F.Cu?
        #cpl.SetLayer(0)

        # (?) merge didn't have an effect out output, used this way
        #pad.MergePrimitivesAsPolygon()
        #footprint.Add(track)
        footprint.Add(pad)

    fpid = pcbnew.LIB_ID(os.path.split(filename)[-1][:(-1)*len('.kicad_mod')])
    footprint.SetFPID(fpid)

    # TODO how to set name of kicad_mod file? named parameter in third arg (list?)?
    io().FootprintSave(footprint_lib_dir, footprint)
    

if __name__ == '__main__':
    to_output_format = as_kicad_mod
    to_output_format(electrode_vertices())

