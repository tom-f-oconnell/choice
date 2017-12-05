#!/usr/bin/env python

from __future__ import division
import numpy as np
import os

# TODO convert in to kicad footprint wizard
def electrode_vertices():
    # the electrode with one trace down the center of the arena
    mirror = True

    # not the exact same as the electrode with a bus down the center
    # there are two disconnected electrodes like these per chamber
    # but only one common high voltage electrode
    include_other_electrode = True
    rightmost_tooth_from_top = False

    # all units in mm unless otherwise noted
    center_x = 0
    center_y = 0
    '''
    # this was the center of one of the grids in the librecad document
    center_x = 125.0
    center_y = 38.7450
    '''

    # maybe a little less?
    min_half_length = 25
    min_width = 6.5
    # changed from 1mm of original to 0.6, which is IPC
    # minimum for up to 150V for uncoated external connectors not at elevation
    between_electrodes = 0.6
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


def as_kicad_mod(polylines, filename='../pcb/footprints.pretty/electrodes_clearance0.6mm.kicad_mod'):
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

    def get_layer_id_by_name(name):
        # TODO how to programmatically get max # of layers?
        ret = None
        for i in range(49):
            n = pcbnew.BOARD_GetStandardLayerName(i)
            if n == name:
                ret = i
        if ret is None:
            raise ValueError('layer with name {} not found'.format(name))
        return ret

    def mm_to_nm(mm):
        return int(round(1e6 * mm))

    def remove_neighboring_duplicates(point_list):
        new_list = list()
        last = None
        for p in point_list:
            if last != p:
                new_list.append(p)
            last = p
        return new_list

    def remove_redundant_ends(point_list):
        def point_set(pl):
            return set(map(lambda x: tuple(x), pl))

        len_redundant_tail = 0
        for i in range(1, len(point_list) // 2):
            # TODO cases where this might fail?
            if point_set(point_list[:i]) == point_set(point_list[-i:]):
                len_redundant_tail = i

        if len_redundant_tail == 0:
            return point_list
        else:
            return point_list[:-len_redundant_tail]

    all_xs = []
    all_ys = []
    for i, pl in enumerate(polylines):
        pad = pcbnew.D_PAD(footprint)
        # work for polygon?
        pad.SetShape(pcbnew.PAD_SHAPE_CUSTOM)
        pv = pcbnew.wxPoint_Vector()

        # kicad considers polygons to be self intersecting any points are repeated
        # including having the point list start and end be the same
        # so we will just exclude the end here
        pl = remove_neighboring_duplicates(pl)
        pl = remove_redundant_ends(pl)

        xs = []
        ys = []
        for p in pl:
            x, y = map(mm_to_nm, p)
            xs.append(x)
            # custom pads on F.Cu (top / front copper) seem flipped along y (?)
            ys.append(-y)

        clearance_nm = mm_to_nm(0.5)
        # left
        if max(xs) < 0:
            pad_x = min(xs) + clearance_nm
            sorted_ys = sorted(list(set(ys)))
            pad_y = (sorted_ys[0] + sorted_ys[1]) / 2.0

        # right
        elif min(xs) > 0:
            pad_x = max(xs) - clearance_nm
            sorted_ys = sorted(list(set(ys)))
            pad_y = (sorted_ys[0] + sorted_ys[1]) / 2.0

        # center
        else:
            pad_x = 0.0
            pad_y = max(ys) - clearance_nm

        # will set position later to compensate for offset
        # apparently anchor will necessarily be at (0,0)
        for p in pl:
            x, y = map(mm_to_nm, p)
            # TODO sign correct?
            pv.append(pcbnew.wxPoint(x - pad_x, (-y) - pad_y))

        # TODO what all does the smd pad specifier mean? reasons i wouldn't want it?
        # TODO remove mask layer?

        # TODO remove solder paste layer?

        # TODO actually setting thickness to zero seemed to expose a bug?
        # even though pad dialog in footprint editor seems to indicate zero is the default?
        thickness = 1
        # TODO why is the thickness of this primitive listed as 0.15mm in the GUI
        # though i don't see it mentioned in the pads in the s-expr output
        # (at least not for the pad, for the reference and stuff i do)
        pad.AddPrimitive(pv, thickness)

        # size needs to be nonzero?
        pad.SetSize(pcbnew.wxSize(1.0, 1.0))

        # i think there are supposed to correspond to pin numbers actually?
        if i == 0:
            pad.SetName('0')
        elif i == 1:
            pad.SetName('1')
        elif i == 2:
            pad.SetName('2')

        # TODO document to set anchor positions for pads

        # TODO how to remove front silkscreen "electrode" label?
        # or move to cmnts layer?

        layer_set = pcbnew.LSET()
        fcu_layer_id = get_layer_id_by_name('F.Cu')
        layer_set.addLayer(fcu_layer_id)
        pad.SetLayerSet(layer_set)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)

        # pad editing in GUI fails if this is not true
        assert pad.MergePrimitivesAsPolygon(), 'pad could not be merged. would be invalid in GUI.'

        # TODO sign correct?
        pad.SetPosition(pcbnew.wxPoint(pad_x, pad_y))

        footprint.Add(pad)

        all_xs.extend(xs)
        all_ys.extend(ys)

    # TODO name according to input parameters
    # (would require this function to have knowledge of generating parameters)
    module_id = os.path.split(filename)[-1][:(-1)*len('.kicad_mod')]
    # what is reference used for exactly?
    footprint.SetReference(module_id)

    # TODO not clear on why both setpos0 and setposition are called
    # in FootprintWizardBase.py
    footprint.Reference().SetPosition(pcbnew.wxPoint(int(round(0.6 * min(all_xs))), \
        int(round(1.1 * min(all_ys)))))
    footprint.Value().SetPosition(pcbnew.wxPoint(int(round(0.6 * max(all_xs))), \
        int(round(1.1 * min(all_ys)))))

    # aiming for a visible layer that does not translate into manufacture
    comment_layer_id = get_layer_id_by_name('Cmts.User')
    footprint.Reference().SetLayer(comment_layer_id)
    footprint.Value().SetLayer(comment_layer_id)

    fpid = pcbnew.LIB_ID(module_id)
    footprint.SetFPID(fpid)

    io().FootprintSave(footprint_lib_dir, footprint)
    

if __name__ == '__main__':
    to_output_format = as_kicad_mod
    to_output_format(electrode_vertices())

