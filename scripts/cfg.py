#!/usr/bin/env python3


# This script is used for generating cfgs from python code
# Author: Nathan Cairns and Buster Major


# IMPORTS #


from staticfg import CFGBuilder
from iteratortools import *
import os
import datetime

# GLOBAL VARIABLES #


err_no = 0


# FUNCTIONS #


# TODO: convert dataset to python 3?  maybe execute in batches to stop the large slowdown, also output stderr on the subproc.
# TODO: add graphviz step in readme and add to envir vars


def process_set():
    if not os.path.exists(ERROR_LOG_PATH):
        os.makedirs(ERROR_LOG_PATH)
    if not os.path.exists(OUTPUT_DATA_PATH):
        os.makedirs(OUTPUT_DATA_PATH)

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
            handle_exception(f, 'Error in building cfg file', e)
        finally:
            progress_bar.print_progress_bar(i+1)


def build_cfg(file_path):
    cfg = CFGBuilder().build_from_file(os.path.basename(file_path), os.path.join(DATA_PATH, file_path))
    cfg.build_visual(os.path.join(OUTPUT_DATA_PATH, file_path), format='dot', calls=False, show=False)
    os.remove(os.path.join(OUTPUT_DATA_PATH, file_path))  # Delete the other weird file created


def handle_exception(file_path, message, stacktrace):
    with open(ERROR_LOG_FILE, 'w+', encoding='utf8') as f:
        f.write('\r{},{},{},{}\n'.format(str(datetime.datetime.now()), message, file_path, stacktrace))


# MAIN #

if __name__ == '__main__':
    process_set()

    if err_no is not 0:
        print('WARN Data pre-processing was unable to process {} files!'.format(err_no))
        print('WARN Refer to log/dataprocessing/errorlog.csv for more details.')
