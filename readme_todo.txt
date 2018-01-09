
installation

1.
- TODO include script to automate all of this (except maybe Arduino upload)
- TODO test sufficiency of ros-kinetic-ros-base. May need `ros-kinetic-ros-desktop`, or at least a few more packages.

2.
- TODO ROS install file?

manufacture

See bill of materials [TODO]()
actually describe manufacture...

running an experiment
requirements
TODO include portion (maybe wiki?) on setting parameters for ROS launch files.

TODO clarify which camera parameters are read by launch files / give options / instructions for other cameras

TODO example usb camera parameter file? do i use one now?

offline tracking
definition of valid directory:
- TODO is compressor_rois* actually required, or can it be recovered from other files? which?

TODO test file + directory options still work in retrack_ros script (was using env var / id most recently)

TODO check expectation relative to DATA_DIR
TODO move it before directory arg? set in a computer specific config

TODO name multi_tracker/retrack_ros something to clarify which type of experiment it is to be used for, or give it an argument to indicate when this type of tracking should be used

copying data...

TODO include instructions on how to setup dedicated SSH keys for rsync, to automate the transfer
TODO include instructions on how to automatically start analysis / tracking after transfer, once polished

analysis
move most of this to a readme within the analysis dir and link there? wiki?

known bugs / workarounds

TODO identify / fix root cause / confirm it is no longer an issue
wasn't there a different command i used to kill all python for some reason? subprocesses?

move explanations of warnings / errors to another section? re-order?
kind of breaks up flow, as is.
