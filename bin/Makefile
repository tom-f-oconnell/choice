
EXEC = .all_installed

# TODO need full path to shell scripts?

$(EXEC): .ros_installed .usb_cam_installed
	touch .installed

.ros_installed:
	install_ros.sh

.usb_cam_installed:
	install_usb_cam.sh
