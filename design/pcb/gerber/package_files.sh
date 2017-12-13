#!/bin/bash

pass_gerbers_through_gerbv=true
pass_drill_through_gerbv=true

if [ "$pass_gerbers_through_gerbv" = true ] || \
    [ "$pass_drill_through_gerbv" = true ]; then

    # bash returns an exit code of 127 if (among perhaps some other reasons)
    # a command is not found, but because there are other reasons and it is
    # unclear is other shells behave that way, we will do it this way
    if ! dpkg-query -W -f='${Status}' gerbv | grep -q '^install ok installed$'; then
        sudo apt update
        sudo apt install -y gerbv
    fi
    # TODO check version is sufficient to have export settings?
fi

base=`pwd`

echo "removing any existing gerbv exports"
# prune is so find doesn't complain about missing directories
# after deleting them with exec, it would otherwise try to traverse them later
find . -iname '*_gerbv_export*' -prune -exec rm -rf {} \;

for d in */
do
    echo $d
    cd $d
    ../uppercase_extensions.py

    cd ${base}

    if [ "$pass_gerbers_through_gerbv" = true ] || \
        [ "$pass_drill_through_gerbv" = true ]; then

        gerbv_export_dir="${d%/}_gerbv_export"
        mkdir ${gerbv_export_dir}

        # currently assuming all drill files end in DRL
        # and that everything else is a gerber
        # TODO consider extensions / cases i might have missed
        if [ "$pass_gerbers_through_gerbv" = false ]; then
            # TODO escaped parens needed for negation or was it just because
            # stuff was ORed inside them in the example?
            find ${d} -type f ! \( -iname '*drl' \) -exec cp {} ${gerbv_export_dir} \;

        elif [ "$pass_drill_through_gerbv" = false ]; then
            # could also probably use symlinks
            find ${d} -type f -iname '*drl' -exec cp {} ${gerbv_export_dir} \;
        fi
    fi

    if [ "$pass_gerbers_through_gerbv" = true ]; then
        # TODO check output is the same
        # TODO make sure to handle if gerbv actually crashes
        find ${d} -type f ! \( -iname '*drl' \) -printf "%f\n" | \
            xargs -I{} gerbv ${d}{} --export=rs274x -o ${gerbv_export_dir}/{} \
            2> gerbv_gerber_errors.txt
    fi
    if [ "$pass_drill_through_gerbv" = true ]; then
        find ${d} -type f -iname '*drl' -printf "%f\0" | \
            xargs -0 -I{} gerbv ${d}{} --export=drill -o ${gerbv_export_dir}/{} \
            2> gerbv_drill_errors.txt
    fi
done

# should just delete the error files if there is nothing in them
if [ ! -s gerbv_gerber_errors.txt ]; then
    rm gerbv_gerber_errors.txt
else
    echo "It seems you might be exporting gerbers from Kicad with extented features checked,"
    echo "because gerbv output errors while processing one or more of the gerber files."
    echo "gerbv and Advanced Circuits both generally seem to have problems with these, so "
    echo "please re-plot the files in Kicad with those boxes unchecked."
fi
if [ ! -s gerbv_drill_errors.txt ]; then
    rm gerbv_drill_errors.txt
else
    echo "There were errors converting drill files from Kicad output with gerbv."
fi

# TODO don't zip empty directories. actually just don't make above
# since some directories could have been created, for gerbv export, in last loop
for d in */
do
    if [ -f ${d%/}.zip ]; then
        rm ${d%/}.zip
    fi
    zip -r ${d%/}.zip $d
    echo ""
done

# TODO store suffix  once and reuse that?
ls *_gerbv_export/
