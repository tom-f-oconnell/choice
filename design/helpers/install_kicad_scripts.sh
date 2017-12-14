#!/bin/bash

# TODO fix (what was broken?)

KICAD_PLUGIN_DIR='~/.kicad_plugins'
if [ ! -d $KICAD_PLUGIN_DIR ]; then
	mkdir $KICAD_PLUGIN_DIR
fi

ln -s `realpath make_board.py` ~/.kicad_plugins/.

# TODO maybe dont assume reltive paths (make_board and below)
./kicad_holes/install.sh
