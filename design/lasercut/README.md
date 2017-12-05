

- `olfactory_shock_conditioning_chambers.dxf`
   - Master design file for lasercut layers of two choice behavior chambers.
   - Layers in the same plane have the same prefix number (before the period).
   - Lower prefix numbers are layers higher in the assembly.
   - TODO include materials and sources for all layers

- `pcb_outline.dxf`
   - Generated from one version of `olfactory_shock_conditioning_chambers.dxf`
   - Imported into Kicad to the `Edge.Cuts` layer to form the outline and 
     interior routed / drilled features of the floor circuit board.

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

#### TODO
- maybe delete all of either the SVGs or the EPS
- maybe generate all of one or both for all files
- maybe store generated files separate from the masters (whether Inkscape SVG or DXF)