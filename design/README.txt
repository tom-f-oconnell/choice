
If any .svg or .fcstd files are newer than files of the same name with a
different extension (should be .eps and .stl, respectively), then you may want
to delete those .eps and .stl files and re-generate them from the newer source
files before cutting / printing the parts.

SVGs are Inkscape SVGs. Generally I would export these as EPS and then load them
on the computer connected to the laser cutter in Coreldraw.  In Coreldraw, I
would convert all lines to "Hairline" , as this was required for any lines you'd
like to cut (<0.0001" should be treated the same, but it is harder to work with
while designing).

.fcstd files should be openable with FreeCAD. The software is getting a lot
better, so it is worth getting the most recent version from the PPA (you can
look up how to do this). I generally used version 0.17. To export STLs you have
to open the FCSTD file, select an object (on the left, the highest level node
that isn't the name of the document), and then go to File->Export and change the
output file type to STL.  I prepared gcode (instruction for the 3D printer) in
Cura, on Windows, because this is what our librarian showed me how to use.

