#!/bin/bash

base=`pwd`

for d in */
do
	echo $d
	cd $d
	../uppercase_extensions.py
	
	cd ${base}
	rm ${d%/}.zip
	zip -r ${d%/}.zip $d
	echo ""
done
