#!/usr/bin/env python

from __future__ import division
from collections import defaultdict
import ezdxf
import solid as s
import os


# TODO include flag for whether or not to also render PCB outlines

name2material = defaultdict(lambda: 'acrylic_3.175mm')
exceptions = {'slider_compression': 'clamp_delrin_1.5875mm',
              'yellow_manifold_layer': 'plastic_shimstock_0.3969mm',
              'delrin_chambers_and_manifold': 'delrin_0.7938mm',
              'pcb_side_spacers': 'viton_1.5875mm',
              'bottom_pcb': 'bottom_pcb'}

# colors will be [r,g,b,alpha], all on [0,1]
material2color = {'acrylic_3.175mm': [1,1,1,0.2],
                  'delrin_0.7938mm': [1,1,1,0.9],
                  'clamp_delrin_1.5875mm': [1,1,1, 0.9],
                  'plastic_shimstock_0.3969mm': [1,1,0,0.95],
                  'viton_1.5875mm': [0,0,0,1],
                  'bottom_pcb': [40/255, 239/255, 179/255, 0.9]}

# TODO load from a BOM or something?
# 1/8 inch = 3.175 mm
# delrin is 1/32" and 1/16"
# yellow shimstock is 1/64"
material2thickness = {'acrylic_3.175mm': 3.175,
                      'delrin_0.7938mm': 0.7938,
                      'clamp_delrin_1.5875mm': 1.5875,
                      'plastic_shimstock_0.3969mm': 0.3969,
                      'viton_1.5875mm': 1.5875,
                      'bottom_pcb': 1.5875}


dxf_filename = '../olfactory_shock_conditioning_chambers.dxf'
dxf = ezdxf.readfile(dxf_filename)
nonconstruction_color = 1
# If using 3D pcb models generated from Kicad, don't need this.
include_regardless = {'bottom_pcb_edges_and_routing', 'top_pcb_edges_and_routing'}
exclude = {'egress_slider'}
layers = []

# get layers for processing later
for layer in dxf.layers:
    name = layer.dxf.name
    '''
    # can't seem to find out how to figure out which layers librecad
    # considers "construction" layers. using color for now.
    print dir(layer)
    #print dir(layer.DXFATTRIBS)
    #print layer.DXFATTRIBS.keys()
    print layer.DXFATTRIBS[u'flags']
    #print layer.has_xdata()
    #print layer.has_app_data()
    print layer.valid_dxf_attrib_names()
    '''
    print name
    print layer.get_color()
    print ''

    use_layer = False
    if layer.get_color() == nonconstruction_color:
        use_layer = True

    else:
        for i in include_regardless:
            if i in name:
                use_layer = True

    if use_layer:
        for e in exclude:
            if e in name:
                use_layer = False
                break

    if use_layer:
        for e in exceptions:
            if e in name:
                name2material[name] = exceptions[e]

        layers.append(name)

print name2material

# TODO how to close w/ ezdxf? context manager?

# TODO assert all have numbers in name for sorting?
# TODO optional sets of layers? (or mutually exclusive sets)

# TODO way to just enforce that everything just stacks enough to not overlap?
# TODO are there ever cases where two layers starting from the same plane are 
# a different height? (would prevent just using prefix as level sets for offset)

sorted_layers = sorted(layers, reverse=True)

def get_prefix(name):
    if '.' in name:
        left = name.split('.')[0]
    else:
        left = name.split('_')[0]
    return int(left)

curr_prefix = get_prefix(sorted_layers[0])
curr_z0 = 0.0
last_height = None

outfile = os.path.split(dxf_filename)[1].split('.')[0] + '.scad'
print 'writing to {}'.format(outfile)

with open(outfile, 'w') as f:
    f.write('// Generated with make_3d.py from master DXF, {}'.format(dxf_filename))
    f.write('\n// Uses ezdxf and solidpython')
    # not sure if OpenSCAD supports all DXF features we would need...
    # way to automatically simplify?
    # what are all the "hatches" it was complaining about? the splines?
    f.write('\n// It seems solidpython needs to be updated to use import and ' + \
        'linear extrude, \n// rather than dxf_linear_extrude.\n')

    for layer in sorted_layers:
        prefix = get_prefix(layer)
        if curr_prefix > prefix:
            curr_prefix = prefix
            curr_z0 += last_height

        material = name2material[layer]
        height = material2thickness[material]
        color = material2color[material]
        # TODO shouldn't layer be quoted? add quotes manually?
        # TODO are all extrusions still in DXF coordinate frame?
        # TODO need to explicitly set center to false?
        e = s.dxf_linear_extrude(dxf_filename, \
            layer=str(layer), height=height)

        if curr_z0 != 0.0:
            e = s.translate([0, 0, curr_z0])(e)
        last_height = height

        # TODO fix color support? (let it take any string?)
        ce = s.color(color)(e)
        f.write(s.scad_render(ce))

