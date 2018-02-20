

- `olfactory_shock_conditioning_chambers.dxf`
   - Master design file for lasercut layers of two choice behavior chambers.
   - Layers in the same plane have the same prefix number (before the period).
   - Lower prefix numbers are layers higher in the assembly.
   - TODO include materials and sources for all layers

- `floor_pcb_edges.dxf` and `ceiling_pcb_edges.dxf`
   - Generated from one version of `olfactory_shock_conditioning_chambers.dxf`
   - Imported into Kicad to the `Edge.Cuts` layer to form the outline and 
     interior routed / drilled features of the floor and ceiling circuit boards.

- `food_vial_holder_no_slider.svg`
   - A prototype food vial holder, to serve as a source of flies for an automatic
     loader.
   - TODO list related parts in 3D printed folder.
   - This master was created in Inkspace. May not load correctly in other programs,
     as it is a special Inkscape SVG format.

- `shaft_output_doubler.dxf`
   - Mounting plates to mate two of the following 70mm gears .
   - Meant to keep the heads of two fly sorters aligned, so when one is at a 
     valid outlet, so is the other.
   - TODO mention related 3D models
- `generated_70mm_gear.svg`
   - TODO how was this generated again? online utility? inkscape script?
   - TODO has this since been copied to `shaft_output_doubler.dxf`? delete?

- `vacuum_trap_for_engraving_0.3.dxf`
   - Prototype of a modular vacuum trap that would be used in isolation.
   - Based quite directly on designs from Ben de Bivort's lab.
   - TODO include laser cutter instructions / power file
- `modular_vacuum_trap.dxf`
   - Unclear whether this was the master or the above was. Neither is rendering 
     properly for me now.

- `smaller_boardcam_mount.dxf`
   - Acrylic adaptor to attach top-down camera to 1" aluminum rail
   - TODO include link to camera / model of one

  
Other files ending in `.svg` or `.eps` are (potentially outdated) exports 
generated from the `.dxf` of the same name. These are for laser cutting, or use
in other programs. They were generated in Librecad, the same program used to 
draw the master DXFs. These intermediates should load OK in at least Coreldraw.

To get a DXF suitable for import into KiCAD, for use as the outline of the
board:
- Make a copy of the DXF with the edges you want
- In the copy (at least relevant to LibreCAD):
  - delete all layers / features other than the edges
  - select any blocks in your design and `Tools->Modify->Explode` them
  - delete all blocks
- (temporarily) change page settings in KiCAD PCB Layout Editor view of either
  the ceiling or the floor board, whichever you want to import new edges to.
  - `File->Page Settings->Orientation->Landscape`
- `File->Import->DXF`
- Change page settings back to portrait, so boards fit on page for printing.

TODO put this in a README in PCB directories somewhere
To generate negative of copper layer for etchant mask:
- (in KiCAD) `File->Plot`
- Select `SVG` from dropdown
- Check `Mirrored plot` and `Negative plot`
- Change any other settings you want, including perhaps what to do with edges.
- Plot
- Print the SVG output in some program that maintains scale (Inkscape works)

The existing negative is in `design/pcb/gerber/ceiling/<...>.svg`.

#### TODO
- maybe delete all of either the SVGs or the EPS
- maybe generate all of one or both for all files
- maybe store generated files separate from the masters (whether Inkscape SVG or DXF)
