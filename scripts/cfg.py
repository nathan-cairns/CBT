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
    # content = content[int(content.__len__() * 13 / 100):]
    print('Generating CFG files:')

    iterate(build_cfg, ERROR_LOG_FILE, content)


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
