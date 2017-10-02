#!/usr/bin/env bash

DATA_DIR=$HOME/data

while true;
do
	echo "waiting for file write in $DATA_DIR"
	# TODO why does cp -r not trigger this?
	INCOMING_DATA_DIR=$(inotifywait -r -q --format '%w' -e close_write -- $DATA_DIR)
	# TODO maybe make this robust to transfers that finish before we have time to check rsync?
	if ! lsof +D $INCOMING_DATA_DIR 2>/dev/null | grep -q rsync
	then
		# TODO shouldn't i still process it if new directory magically appeared
		# and it hasn't been tracked? test for that directly? (presence of hdf5)
		echo "rsync did not appear to have files open in this directory. restarting."
		continue
	fi
	echo "waiting for rsync writing to this directory to finish."
	while true;
	do
		if ! lsof +D $INCOMING_DATA_DIR 2>/dev/null | grep -q rsync
		then
			echo "rsync writing to this directory finished."
			break
		fi
	done
	echo "waiting for ROS to shutdown"
	# wait until ROS is no longer running, checking every 10s
	while true;
	do
		rostopic list 2&>1 >/dev/null || break
		sleep 10
	done
	# TODO also run on any directories created after first incoming detected?
	# run tracking on the video, as recreated from the bag file
	echo "running \"rosrun multi_tracker retrack ${INCOMING_DATA_DIR}\""
	rosrun multi_tracker retrack ${INCOMING_DATA_DIR} &&

	# -> run analysis pipeline
	# TODO have that upload all from each experiment to their own evernote thing?
	# see stackoverflow.com/questions/786376/how-do-i-run-a-program-with-a-
	# different-working-directory-from-current-from-lin
	(cd $DATA_DIR && exec rosrun choice choice_analysis)
	# else error?
done
