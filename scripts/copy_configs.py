#!/usr/bin/env python

import sys
import rospkg
from os.path import split, join, isfile, exists
from os import getcwd
from shutil import copy2
import subprocess

# TODO TODO refactor so this can reuse multi_tracker copy_config (which we are calling anyway?)
# with just a few arguments, maybe?

# this runs code with side effects of copying the multi_tracker
# config files
command = ['rosrun', 'multi_tracker', 'copy_configs.py']

# TODO check works whether run with rosrun / roslaunch or not
# may not
if len(sys.argv) > 1:
    command += sys.argv[1:]
    print 'appending {} to args for multi_tracker copy_configs.py'.format(sys.argv[1:])

else:
    print 'not appending any arguments to multi_tracker copy_configs.py call'

sp = subprocess.Popen(command)
# TODO can i just import this from the correct directory to call it?
# TODO package into function to avoid this hack

if len(sys.argv) == 1:
    dst_dir = getcwd()

elif len(sys.argv) > 2:
    dst_dir = sys.argv[1]

else:
    raise ValueError('Usage: rosrun multi_tracker copy_configs.py <destination_path>. Omit path to use current directory.')

# TODO will have to first find source directory unless i put the default configuration files in the
# install targets of cmake (which i may want to do to package this)

# TODO will need to change if i ever want this to be installable via apt / ROS build farm (install target, I assume)
only_in_source = True

if only_in_source:
    n_src_dirs = 0
    for d in rospkg.get_ros_paths():
        # TODO how to find if there are multiple catkin workspaces?
        # probably need to call get_path on RosPack initialized on both, and handle empty output
        if 'src' in split(d):
            source_dir = d
            if n_src_dirs > 0:
                raise IOError('found multiple directories with package sources. only searching first found. this script not currently equipped for this case.')
            n_src_dirs += 1

    if source_dir is None:
        raise IOError('No source directories found! Must configure yamls as part of catkin install target to have those in non-source version.')

    rospack = rospkg.RosPack([source_dir])

else:
    rospack = rospkg.RosPack()

# TODO will defaults be in same relative place once installed? can / should they be?
# (might be non-compliant w/ install standard)

# TODO rename either multi_tracker/example_config or choice/example, for consistency?
path = join(rospack.get_path('choice'), 'example')
src = join(path, 'stimulus_parameters.yaml')

f = split(src)[-1]
dst = join(dst_dir, f)

if exists(dst):
    raise IOError('file ' + dst + ' exists! delete it or run this script elsewhere')

if not exists(src):
    raise IOError('file ' + f + ' not found')

if isfile(src):
    copy2(src, dst)

else:
    raise ValueError('found non-file in source directory, but only equipped to copy regular files. delete the non-file or change the code')

