# =======================================
# PACKAGE IMPORTS
# =======================================
# python built-in packages
import bisect
import os

# 3rd party packages
import h5py
import numpy as np
import pandas as pd

# local
from custom_errors import (
    MissingFilesException, 
    CorruptHDF5Exception,
    MissingColumnException,
)

# =======================================
# DEFINE HELPER FUNCTIONS
# =======================================
# function that goes through an **already sorted** array-like 
# data structure and finds the index of the element that 
# is closest to a passed numeric value
def find_closest_index(sorted_arr, search_val):
    # use the built-in library bisect's binary search function
    # to find the index where the input value would be inserted
    # in order to keep the array sorted
    insert_index = bisect.bisect(sorted_arr, search_val)
    # if the search value is greater than the highest value
    # in the array, return the highest index of the array
    if len(sorted_arr) == insert_index:
        return insert_index - 1
    # if the search value is less than the least value
    # in the array, return index 0
    if insert_index == 0:
        return 0
    # check which value is the closest to 'search_val' out of the value
    # right before the 'insertion index slot', or right after
    # it. if there is a tie, return the lower of the two indexes.
    before_dist = abs(sorted_arr[insert_index-1] - search_val)
    after_dist = abs(sorted_arr[insert_index] - search_val)
    if after_dist < before_dist:
        return insert_index
    else:
        return insert_index-1



def reformat_data(exp_data_dir, output_dir):
    """
    Reformats PsychoPy data output, where each experiment run
    produces one CSV file and one HDF5 file, named according to
    the same logic, eg 'foobar_myexp_2021_Aug_09_1904.csv'
    and 'foobar_myexp_2021_Aug_09_1904_hdf5.hdf5'.
    :param exp_data_dir: Full path to raw experiment output directory.
    :param output_dir: Full path to directory to output reformatted
    data to.
    """
    # =======================================
    # FIND ALL DATA FILES
    # =======================================
    # list all files & directories in data input directory,
    # excluding hidden files
    input_fnames = os.listdir(exp_data_dir)

    # find names of all CSV and HDF5 files in the 
    # data input directory
    csv_fnames = [fname for fname in input_fnames if fname.endswith('csv')]
    hdf5_fnames = [fname for fname in input_fnames if fname.endswith('hdf5')]

    # if no CSV files, or no HDF5 files, were found
    # (ie at least one of the lists is empty, 
    # producing False values below), 
    # then raise an error
    if not (csv_fnames and hdf5_fnames):
        raise MissingFilesException(
            "The data directory doesn't contain both CSV and HDF5 files. "
            "Please check to make sure that you've selected the correct "
            "data directory."
        )

    # if there aren't as many CSV files as there are HDF5 files,
    # raise an error (since this means that for some experiment run
    # there are only 'core PsychoPy' data, or only 'eyetracker data')
    if len(csv_fnames) != len(hdf5_fnames):
        raise MissingFilesException(
            "The selected data directory contains an unequal number of "
            f"CSV files ({len(csv_fnames)}) and HDF5 files ({len(hdf5_fnames)}). "
            "This means that for at least one experiment, there is only "
            "'core PsychoPy' experiment output, or there is only eyetracker "
            "recording output.\n\n"
            "The most likely reason for this problem is that an experiment was "
            "aborted/closed down before it could finish, meaning no HDF5 file was saved. "
            "Please make sure that the data directory only includes complete "
            "experiment data sets (ie where there is an HDF5 file and CSV file "
            "corresponding to an experiment run), by moving incomplete data to "
            "a separate folder.\n" 
            "When you're done, click the reformat button again."
        )

    # =======================================
    # SORT DATA FILES BY NAMES
    # =======================================
    csv_fnames.sort()
    hdf5_fnames.sort()

    # =======================================
    # DEFINE RELEVANT 'CORE PSYCHOPY' COLUMNS
    # =======================================
    # define list of 'core PsychoPy' experiment output data columns 
    # that are of interest for combining with/inserting into the
    # eyetracker data frame (see below)
    core_interesting_colnames = [
        'att_grab_start_time_intended',
        'gaze_to_audio_delay_intended',
        'audio_to_visual_delay_intended',
        'visual_duration_intended',
        'end_blank_duration_intended',
        'att_grab_start_time_actual',
        'gaze_captured_time',
        'audio_onset_time',
        'visual_onset_time',
        'visual_offset_time',
        'trial_end_time',
        'attention_sounds_played',
        'visual_stimuli_duration_nframes',
        'visual_social_prop',
        'visual_geometric_prop',
        'visual_manmade_prop',
        'visual_natural_prop',
        'visual_social_filepath',
        'visual_social_pos_x',
        'visual_social_pos_y',
        'visual_geometric_filepath',
        'visual_geometric_pos_x',
        'visual_geometric_pos_y',
        'visual_manmade_filepath',
        'visual_manmade_pos_x',
        'visual_manmade_pos_y',
        'visual_natural_filepath',
        'visual_natural_pos_x',
        'visual_natural_pos_y',
        'audio_filepath',
        'audio_volume',
    ]

    # =======================================
    # START LOOPING THROUGH FILES
    # =======================================
    # loop through all of the CSV/HDF5 files and slightly correct
    # and combine their data, then export results to one CSV
    # file per set of experiment data
    for csv_fname, et_hdf5_fname in zip(csv_fnames, hdf5_fnames):
        et_hdf5_path = os.path.join(exp_data_dir, et_hdf5_fname)
        csv_path = os.path.join(exp_data_dir, csv_fname)

        # =======================================
        # EXTRACT EYETRACKER DATA WITH H5PY
        # =======================================
        try:
            h5f = h5py.File(et_hdf5_path)
        except OSError as e:
            raise CorruptHDF5Exception(
                f"HDF5 file '{et_hdf5_path}' appears to be corrupt and cannot "
                'be processed.'
                f'(original exception: {e})'
            )

        h5f_events = h5f['data_collection']['events']
        # traverse hierarchical data structure to get at eye tracking data.
        # check if 'mock' (using the mouse to simulate eyetracker gaze recording) 
        # data are used (in which case 'monocular' events
        # have been registered), or if actual data are used 
        # (in which case 'BinocularEyeSampleEvent' have been registered,
        # usually)
        if 'BinocularEyeSampleEvent' in h5f_events['eyetracker'].keys():
            eye_dataset = h5f_events['eyetracker']['BinocularEyeSampleEvent']
        elif 'MonocularEyeSampleEvent' in h5f_events['eyetracker'].keys():
            eye_dataset = h5f_events['eyetracker']['MonocularEyeSampleEvent']
        else:
            raise CorruptHDF5Exception(
                f'HDF5 file {et_hdf5_path} appears to be corrupt and cannot '
                'be processed.'
            )
        # traverse hierarchical data structure to get at data describing messages
        # 'sent from PsychoPy', eg 'trial start' messages
        message_dataset = h5f_events['experiment']['MessageEvent']

        # convert eyetracker/message data to numpy arrays
        eye_data_arr = np.array(eye_dataset)
        message_data_arr = np.array(message_dataset)

        # convert the eyetracker data numpy array to a pandas data frame
        et_df = pd.DataFrame(eye_data_arr)
        # convert 'messages' data numpy array to pandas data frame
        msg_df = pd.DataFrame(message_data_arr)

        # convert the 'messages' data frame's messages from 'byte' dtype
        # to string literal dtype
        msg_df['text'] = msg_df.text.str.decode('utf-8')

        # add a 'message' column to the eyetracker data frame
        et_df['message'] = np.nan

        # for each recorded message, find the row in the 'et_df' which matches 
        # most closely with regard to time of recording, and 
        # insert the message into 'et_df'
        for _, row in msg_df.iterrows():
            closest_i = find_closest_index(et_df.time, row.time)
            et_df.loc[closest_i, 'message'] = row.text

        # close the connection to the hdf5 file
        h5f.close()
        
        # =======================================
        # LOAD 'CORE PSYCHOPY' EXPERIMENT DATA
        # =======================================
        # import psychopy experiment output data
        # (stimuli onset times/file names/positions et c.)
        psyp_df = pd.read_csv(csv_path)

        # check if all of the necessary data columns are
        # in the CSV file, and otherwise raise an error
        for coln in (core_interesting_colnames + ['trial_global_start_time']):
            if coln not in psyp_df.columns:
                raise MissingColumnException((
                    f"Missing column in CSV file '{csv_path}':\n"
                    f"Could not find required column '{coln}'. "
                    "Please double-check the data. "
                    "If it's not possible to correct the CSV file, "
                    "please move it, and its corresponding HDF5 file, "
                    "to another directory and rerun the reformatting."
                ))

        # =======================================
        # ADJUST EYETRACKER DATA TIMES
        # =======================================
        # find all correctly registered trial start times from CSV file
        psyp_stime_mask = psyp_df.trial_global_start_time.notna()
        psyp_first_trial_start_times = psyp_df.trial_global_start_time[psyp_stime_mask]
        # find all correctly registered trial start times from eyetracker/HDF5 file
        # (these are indicated by 'trial <trial_number> start' messages sent from PsychoPy to the
        # submodule handling the eyetracker)
        et_stime_mask = et_df.message.notna() & et_df.message.str.match('exp1 trial \d+ start')
        et_first_trial_start_times = et_df.time[et_stime_mask]
        # find the average offset between: 
        # * trial start times as recorded by the PsychoPy 'core', 
        #   and stored in the CSV file 
        # * trial start times as recorded by iohub (the PsychoPy submodule which 
        #   handles the eyetracker) by means of messages sent by the PsychoPy 'core',
        #   and stored in the HDF5 file
        et_avg_offset = et_first_trial_start_times.mean() - psyp_first_trial_start_times.mean()
        # shift the iohub/eyetracker data times by the average offset
        et_df.time = et_df.time - et_avg_offset

        # =======================================
        # INSERT 'CORE PSYCHOPY' DATA INTO 
        # EYETRACKER DATA FRAME
        # =======================================
        # form an empty column in eyetracker data frame 
        # for each 'interesting' one in the 'core PsychoPy' data
        for coln in core_interesting_colnames:
            et_df[coln] = np.nan

        # get a list of indices for 'trial start' rows in et_df
        et_tstart_indices = list(et_stime_mask[et_stime_mask].index)

        trial_counter = 0

        # for each trial, extract the trial's 'core PsychoPy' (CSV)
        # output data and insert it into the eyetracker data frame
        # at the row for 'trial start'. note that in the CSV/psyp_df,
        # each full row corresponds to one trial
        for _, row in psyp_df[psyp_stime_mask].iterrows():
            et_i = et_tstart_indices[trial_counter]
            for coln in core_interesting_colnames:
                et_df.loc[et_i, coln] = row[coln]
            trial_counter += 1
        
        # =======================================
        # EXPORT COMBINED DATA TO CSV FILE
        # =======================================
        # form combined data file's name by replacing '.csv' with
        # 'combined.csv' in input CSV filename
        output_fname = csv_fname.replace('.csv', '_combined.csv')
        output_fpath = os.path.join(output_dir, output_fname)
        et_df.to_csv(output_fpath, index=False)
