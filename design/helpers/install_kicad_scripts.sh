#!/bin/bash

# TODO fix

KICAD_PLUGIN_DIR='~/.kicad_plugins'
if [ ! -d $KICAD_PLUGIN_DIR ]; then
	mkdir $KICAD_PLUGIN_DIR
fi

ln -s `realpath make_board.py` ~/.kicad_plugins/.
