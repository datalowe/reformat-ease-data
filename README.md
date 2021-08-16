# Reformat PsychoPy experiment/eyetracker data
## Overview
This is an app built with Python, using pyinstaller, numpy, pandas, tkinter and h5py, for a project at Karolinska Institutet. __It is likely to be of little interest to others__, the exception being if you can find inspiration in the code for building something yourself. Once built, the app is used to reformat PsychoPy output CSV and HDF5 files into single CSV files which include both eyetracker data and 'core PsychoPy' output such as stimuli onset/offset times.

## Building the app
1. `cd` to the project's root directory
2. Create a Python 3.8 virtual environment, with eg `python3.8 -m venv .venv`
3. Activate the virtual environment (eg `. ./venv/bin/activate`).
4. Build the application with using `pyinstaller tkinter_application.py`., 

Note that building produces an __OS-specific__ runnable. Please see the offical docs for pyinstaller and the other packages mentioned above for more information.

## Caveats
The app assumes that the input/experiment data are of a highly specific character, with CSV files including column names that have been hardcoded into 'reformat_exp_data.py'. Furthermore, the app assumes that the experiment has used the PsychoPy `iohub` module for collecting eyetracker data, and that each participant's data are stored in a separate HDF5 file. The code is also far from optimized or cleaned up.