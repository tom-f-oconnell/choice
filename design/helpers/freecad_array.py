
# TODO need to import anything? maybe to run w/ python, rather than freecad?

import FreeCAD
import Draft

# TODO TODO script the install of the dxf export libraries if necessary

doc = 'test_array'
App.newDocument(doc)
App.setActiveDocument(doc)
# necessary for headless editing?
# this might have been expanded from previous line?
App.ActiveDocument = App.getDocument(doc)

# TODO way to set working plane to xy? only benefit in manual editing?
# would be nice to have other commands also only take two arguments in that case?
# maybe not...

# TODO r, x, y, color need to be defined below

# TODO is the following necessary? meaning of 1 in 4th arg?
pl = FreeCAD.Placement()
# TODO does the rotation have a reasonable default? it should...
pl.Rotation.Q = (0.0, 0.0, 0.0, 1.0)
pl.Base = FreeCAD.Vector(x, y, 0.0)

# TODO color?
# TODO how to make radius depend on one variable (in freecad). need to use spreadsheet?
# and how much of array can be made parametric w/in FreeCAD rather than here?
# colors (or other property) via group? clone?
# TODO do properties persist through "offset"? "clone"? is there a clone? how else?

c = Draft.makeCircle(radius=r, placement=pl, face=False, support=None)
# TODO what does this line do? invoke at all? once at end?
#Draft.autogroup(c)

# TODO is label the same thing edited w/ "Rename"?

# TODO is it kosher to use 0.01 / 0.001? gui seemed to not want to accept those?
# are default units mm? why does lowest allowed seem to be 1? can use um or something?
# or just mm / in?
c.LineWidth = 1 # way to specify units here?
# TODO note there can (must?) be a 4th element to color (transparency).
# but not used? implement?
c.LineColor = tuple(color)

# TODO what is deviation property?

# TODO set properties before or after arraying? copy array in y?
# TODO how to vary something along axis of array (doable in freecad?) (the alpha / intensity)
# TODO TODO maybe use Transparency or DiffuseColor properties? test them

# TODO how exactly is array different from makeArray? 
# the latter makes one of the former, it seems, but "parametric"? how diff?


# TODO do i want the freecad file?
# TODO encode same way prefix of u'' does
#App.getDocument(doc).saveAs(freecad_intermediate_output)

