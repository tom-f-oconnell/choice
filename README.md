
### Installation
1. [Install ROS Kinetic](http://wiki.ros.org/kinetic/Installation) on a supported operating system.  
   - Tested on [Ubuntu 16.04](https://www.ubuntu.com/download/desktop).
   - You can install Ubuntu alongside Windows with minimal effort.
   - Other ROS versions may work, but tested with Kinetic.
   - You only need `ros-kinetic-ros-base`.
      - You do *NOT* need everything in `ros-kinetic-desktop-full`, and it takes more disk space and install time.
  

2. Install the catkin packages.
   See ROS [tutorial on making a catkin workspace](http://wiki.ros.org/catkin/Tutorials/create_a_workspace).

   If you have not already, add a line to your `~/.bashrc` that loads the development setup script (that catkin generates), such as:
   ```
   source <your_catkin_workspace>/devel/setup.bash
   ```

   Then this should install all the packages you need:
   ```
   cd <your_catkin_workspace>/src
   git clone git://github.com/tom-f-oconnell/multi_tracker.git
   git clone git://github.com/tom-f-oconnell/rosserial.git
   git clone git://github.com/tom-f-oconnell/metatools.git
   git clone git://github.com/tom-f-oconnell/stimuli.git
   git clone git://github.com/tom-f-oconnell/choice.git
   cd <your_catkin_workspace>
   catkin_make
   . ~/.bashrc
   ```

   The last line loads `<your_catkin_workspace>/devel/setup.bash` because of the line you added to your `~/.bashrc` in the previous step.

   On all of the computers in the Hong lab, the catkin workspace can be found at `~/catkin`, for whichever user account was used to run the experiments.

   Currently, only installation from source is supported. In the future, I would like to make this installable as a ROS package via apt, but that would likely also require the same of `multi_tracker`, and there are some technical reasons that won't be possible right now with ROS Kinetic.
  

3. Upload the firmware to an Arduino MEGA
   1. Download and unzip Arduino to a path you will remember, or locate it if already installed.
      - Version ~1.5 - 1.8.3 should definitely work. Nearby versions almost certainly also will. You should get error messages when compiling if things do not work, and if this is the case you may need to use a different version of Arduino.
      - Arduino older than or equal to 1.0 will likely not work.
      - I unzipped Arduino to my home directory, which came out as as `~/arduino-1.8.3`, which I will use as an example.
   2. `cd ~/arduino-1.8.3/libraries` (or wherever your Arduino is installed)
   3. `rm -rf ros_lib` (in case some libraries have already been generated)
   4. `rosrun rosserial_arduino make_libraries.py .`
   5. If you Arduino IDE was open, close and re-open it.
      - *Make sure that you are opening the same version of Arduino you installed the libraries for.* It is easier to only have one version of Arduino installed at any given time to avoid these conflicts.
   6. Add your user to the `dialout` group (if on Ubuntu), to be able to upload code.
      - `sudo adduser <username> dialout`
      - Log out and back in for the change to take effect
   7. Connect your Arduino MEGA to the computer.
      - Arduino's with less memory will currently **NOT** work, as there is considerable overhead in the generated ROS libraries.
   8. Upload code
      In the Arduino IDE, under the `Tools` menu:
      - Select appropriate port
         - Usually `/dev/ttyUSBX`, where `X` could vary. `/dev/ttyACMX` may also work. It is never the one like `/dev/ttyS0`.
         - May have the correct board model in parentheses after the port name
      - Select appropriate board (probably `Arduino/Genuino Mega or Mega 2560`)
      - Press the Upload button in the top left of the IDE
         - It looks like a circle with a righward arrow in it.
      - If the TX / RX lights flash on the Arduino, and the Upload seems to finish, you should be good to go.
  

4. *(Optional)* Set an alias for running `roslaunch` with a different `ROS_HOME` environment variable.

To load the configuration files from (and to save the output directory to) the current directory, I prefix the `roslaunch choice choice.launch` command with `ROS_HOME=``pwd```. To make all `roslaunch` invokations behave this way, which works for my purposes, you can make an alias for `roslaunch`.

If you don't already have a ~/.bash_aliases file, you can create one by opening it in a text editor, otherwise just open the file you already have. Add a line that says:
```
alias roslaunch='ROS_HOME=`pwd` roslaunch'
```

Save and close the file, and reload your terminal environment by typing `. ~/.bashrc`, or opening a new terminal. Now you can just type `roslaunch choice choice.launch`, and it will load configuration input from the current directory and save output there as well.


### Manufacture

TODO link to a readme in the design folder / wiki?
  

### Running an experiment

#### Requirements
The current directory has at least the following configuration files:
##### For tracking
- tracker_parameters.yaml
- roi_finder.yaml
- delta_video_parameters.yaml

- If running the tracking in real-time, also:
   - liveviewer_parameters.yaml
   - data_association_parameters.yaml
   - kalman_parameters.py

##### For stimulus
- stimulus_parameters.yaml

Depending on the camera you are using, you may also want to include parameters for your camera node, which you will have to load separately. There are some examples in the `multi_tracker` repository.

To copy templates for each of these configuration files to your current directory:
```
rosrun choice copy_configs.py
```

##### To set the length of the experiment
In the `stimulus_parameters.yaml` file, set the parameters starting at `olf/training_blocks` and ending at `olf/beyond_posttest_s` to appropriate values.

For now, also make sure that `multi_tracker/record_length_hours`, in `tracker_parameters.yaml`, is at least as large as the total length of your stimulus presentation.

#### To run a full experiment with real-time tracking on the same computer.
Requires a computer with adequate memory and processor.
```
roslaunch choice choice.launch
```

##### Errors (red text)
The only error message that is normal during startup is one along the lines of `Parameter stimulus_arduino/debug does not exist`. Another other red text means something is likely not working, and you should not ignore it.

##### Warnings (yellow text)
`Failed to get param: timeout expired` is normal, as long as the program ultimately stops emitting these warnings. You should be aware of the reasons other warnings occur. Contact Tom with any questions.

#### To run an experiment saving a background subtracted video in a ROS bag file, for offline tracking.
Less hardware demands.
```
roslaunch choice choice.launch video_only:=True
```

#### To run the stimulus presentation that would happen during an experiment, but without any recording or tracking.
For measurement / verification / PID purposes.
```
roslaunch choice choice.launch stimuli_only:=True
```

To test the valves (I run this before and after each experiment, to make sure no connections came loose. With more robust electronics this might be less of a concern.)
- The number of the pin to be switched will be printed in the terminal you run the launch file from.
- I attach higher pressure air to all valves and check manually for air flow at each pin that should be switched.
```
roslaunch stimuli test_valves.launch
```

Press `<Ctrl>-C` to stop the `test_valves.launch` file.
  

### Offline tracking

#### Requirements
- The environment variable `DATA_DIR` is set to a path you will keep your data directories beneath.
   - I organize my experiment directories as grandchildren of `DATA_DIR`, grouping them as I see fit with directories (of arbitrary names) just beneath `DATA_DIR`.
   - To test that this is set, you can run `echo $DATA_DIR`, and the path should be printed.
   - To set this:

     Add a line to your `~/.bashrc` file like:

     ```
     export DATA_DIR="<full_path_to_data_directory>"
     ```

     For instance, mine has this line:
     ```
     export DATA_DIR="$HOME/data"
     ```

     Then, either start a new terminal, or run `. ~/.bashrc`, so that the change in the environment variable takes effect.

- `$DATA_DIR/retracked` exists and has all of the configuration files required for tracking (see requirements for running an experiment above)
- All of the installation instructions for at least ROS and the `multi_tracker` package are done.


On any computer satisfying these requirements, run:
```
rosrun multi_tracker retrack_ros <experiment_directory> <decimal_valued_rate>
```

The `<decimal_valued_rate>` can be set as high as does not produce a stream of warning messages that does not improve until the tracking finishes.  If the computer appears to be straining, you may also want to decrease the rate.  If you want to also employ more limited computers for tracking lots of data, you are also able to decrease the rate beneath 1.0 if necessary.

The default rate is currently 0.8, if no rate is provided. Our analysis workstations can track up to a rate of 4.0 - 5.0, with little issue.

The `<experiment_directory>` can be any of:
- ~~a path to a valid directory~~
- ~~a file within a valid directory~~
- the name of a subdirectory beneath `$DATA_DIR`, if the `DATA_DIR` environment variable is set
   - the way this script currently finds the output path, it requires `DATA_DIR`, so you should use this option for now.

A valid directory has:
- at a minimum:
   - a name in the `YYYYMMDD_HHMMSS` format
   - a bag file
   - any background PNGs that were in the same directory
   - a file with the ROIs called `compressor_rois_<experiment_id>.yaml`
- ideally, all files generated during acquisition, including also:
   - a `*_parameters.yaml` file
   - a `*_stimuli.p` file


#### Example
```
rosrun multi_tracker retrack_ros 20170930_164433 2.0
```

In this example, `DATA_DIR` was set with a line in my `~/.bashrc` file as:
```
export DATA_DIR="$HOME/data"
```
and `/home/tom/data/20170920/20170930_164433` was a valid directory. Note that `20170930_164433` was not a direct child directory of `DATA_DIR`. The code may currently expect the `<experiment_directory>` to be a granchild of `DATA_DIR`, if this option is selected.

#### Output
After running the tracking, the valid directory you provided as input will also have:
- An HDF5 file with a the variables the tracker is estimating, over time
   - The `position_x` and `position_y`


#### Copying data from acquisition to tracking / analysis computer

You are of course free to copy the files via other means. This may just end up being convenient.

#### Requirements
- Both computers have internet access
- The computer you are trying to connect TO has an SSH server installed and running
   - Look up how to install OpenSSH server for the operating system you are using if you need to do this.

```
rsync -auvPzr <folder_with_data> user@<server_ip_address>:~/<place_to_put_it>
```

The rsync command with those flags seems not to work if you include a trailing slash after the `<folder_with_data>` name.

#### Example
```
rsync -auvPzr ~/data/. tom@gerty:~/data
```
This example will recursively copy all subdirectories of data, and I keep all my experiment directories nested within here.


#### Known bugs + workarounds
If you notice your computer working harder than it should when the acquisition / tracking should otherwise have terminated, you can run `top` or some other process manager, and check for a handful of processes, owned by the same user that ran the launch file, with names including:
- `play`
- `record`
- `python`
- `<something>launch` ?

And assuming you are OK killing all ROS processes currently running on your computer, you can try running:
- `killall roscore`
- `killall roslaunch`
- `killall play`

Under some circumstances, you may also want to kill all python processes owned by the user that started the ROS processes, with `killall python`.
  

### Analysis
#### Requirements
(To be added )
- `DATA_DIR` is set as in offline tracking instructions.
- `choice` and `multi_tracker` are installed as above (though you don't technically need all of ROS)
- The experiments you want to analyze together have their data folders grouped within an immediate subdirectory of `$DATA_DIR/retracked`.
   - If your tracking output comes from real-time tracking, it does not need to be treated differently, apart from copying it to a subdirectory beneath `$DATA_DIR/retracked`.
- The `ruamel.yaml` package, which you should be able to get via:
   ```
   cd <choice>
   pip install -r requirements.txt
   ```
   Again, if you need root access to install via `pip`, use `sudo` as above.

#### Running
```
rosrun choice choice_analysis <subdirectory>
```

If, across all analysis runs *that have used this folder as input*, you have not already labelled all experiments as either good or needing rejection for some reason, a GUI should open asking you to label the traces appropriately. See the terminal output for which keys correspond to which labels.

The output of this labelling should be saved as `$DATA_DIR/retracked/<subdirectory>/analysis_rejects.yaml`. It is human readable, and you can edit it by hand in a text editor if you want to change something. If you want to start the labelling over, feel free to delete or move / rename `analysis_rejects.yaml`.

Currently, if you want labels to apply across groupings of your data, (across analysis runs with different subdirectories as input) you will need to manually merge the `analysis_rejects.yaml` text files.

#### Output

Within the `$DATA_DIR/retracked/<subdirectory>`, you should find a number of files in a graphics format (svg by default). For each odor, each reject category, and each preference metric (fraction of time spent and "decision bias"), you will find:
- `<metric>.svg`
   - For pooled data of all non-rejects, across all odors.
- `<odor>_<metric>.svg` (or .other_graphic_format, like .png)
   - For pooled data of all non-rejects, within an odor.
- `<reject_category>_<metric>.svg`
   - For data of all rejects of a certain label / category, pooled across odors

There will also be text output, in the terminal in which you ran the analysis, describing the metrics within and across odors, and the fraction of flies in each reject category.
  

### Updating code

If you have made any changes to your local copies of these repositories that you would like to keep, look up `git stash` and proceed with caution, otherwise:

```
roscd multi_tracker
git pull
roscd choice
git pull
```

Then, repeat the instructions for installing catkin packages above, which should look like:
```
cd <catkin_workspace>
catkin_make
. ~/.bashrc
```

This, again, requires that you have a line in your `~/.bashrc` that "sources" (loads) the file `<catkin_ws>/devel/setup.bash`, or else the line `. ~/.bashrc` will not necessarily apply all updates that have been made to the code.

