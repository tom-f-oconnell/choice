
from __future__ import division
import pcbnew

def nm_to_mm(nm):
    return nm / float(1e6)

def mm_to_nm(mm):
    return int(round(1e6 * mm))

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

