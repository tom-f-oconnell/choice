
import os
import numpy as np
import multi_tracker_analysis as mta

exp_dir = os.environ['EXP_DIR']
# walk to find subdirs
for subdir in os.path.walk(exp_dir):
    # TODO read roi_polygon saved (via parameters?) for this node
    # TODO TODO TODO means i have to save the parameters for each node...
    # maybe put save_parameters in each single_tracking_pipeline as well?
    # way to restrict what is dumped to the namespace of each tracking node?
    # TODO or otherwise just save rois per node?

    # TODO find long axis (+ approx w/ rect?) and rotate


    # TODO modify to work on directories if it does not yet, assuming directory only
    # has one hdf5 file
    pd, config = mta.read_hdf5_file_to_pandas.load_and_preprocess_data(subdir)
   
    # TODO auto join all trajectories for this analysis? considering we should only have 1 fly per...
    
