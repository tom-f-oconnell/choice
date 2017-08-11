#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

mkdir -p ~/catkin/src
cd ~/catkin/src
git clone https://github.com/bosch-ros-pkg/usb_cam.git
cd ..
catkin_make
source ~/catkin/devel/setup.bash

# TODO need? need root?
rosdep install camera_calibration

# should include v4l2-ctl and get rid of a usb_cam warning
# not sure what it fixes / if it fixes anything
apt install v4l-utils

touch $DIR.usb_cam_installed
