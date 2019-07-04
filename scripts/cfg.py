#!/usr/bin/env python3


# This script is used for generating cfgs from python code
# Author: Nathan Cairns and Buster Major


# IMPORTS #


from staticfg import CFGBuilder
from iteratortools import *
import os


# GLOBAL VARIABLES #


ERROR_LOG_FILE = os.path.join(ERROR_LOG_PATH, 'cfg.csv')
err_no = 0


# FUNCTIONS #


def process_set():
    if not os.path.exists(get_output_data_path('')):
        os.makedirs(get_output_data_path(''))

    content = get_file_paths()
    print('Generating CFG files:')

    progress_bar = ProgressBar(0, content.__len__(), prefix='Progress:', suffix='Complete')
    progress_bar.print_progress_bar(0)
    for i, f in enumerate(content):
        try:
            build_cfg(f)
        except Exception as e:
            global err_no
            err_no += 1
            handle_exception(ERROR_LOG_FILE, f, 'Error in building cfg file', e)
        finally:
            progress_bar.print_progress_bar(i+1)


def build_cfg(file_path):
    cfg = CFGBuilder().build_from_file(os.path.basename(file_path), os.path.join(DATA_PATH, file_path))
    cfg.build_visual(get_output_data_path(file_path), format='dot', calls=False, show=False)
    os.remove(get_output_data_path(file_path))  # Delete the other weird file created


# MAIN #

if __name__ == '__main__':
    process_set()

    if err_no is not 0:
        print('WARN Data pre-processing was unable to process {} files!'.format(err_no))
        print('WARN Refer to log/dataprocessing/cfg.csv for more details.')
