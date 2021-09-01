"""
This script is strictly for debugging the functions in
'reformat_exp_data.py' and is __not__ meant to be included
in tkinter bundles/the app itself (see README file for info on that).
"""
import reformat_exp_data

test_input_dir = (
    'debug_data'
)
test_output_dir = (
    'debug_data/debug_data_output'
)

reformat_exp_data.reformat_data(test_input_dir, test_output_dir)
