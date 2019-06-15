#!/usr/bin/env python3


# This script is used for converting existing python program from python version 2 to python version 3.
# Author: Buster Major


# IMPORTS #


from subprocess import call
from iteratortools import *
import os


# FUNCTIONS #


def process_set():
    if not os.path.exists(ERROR_LOG_PATH):
        os.makedirs(ERROR_LOG_PATH)

    content = get_file_paths()

    progress_bar = ProgressBar(0, content.__len__(), prefix='Progress:', suffix='Complete')
    progress_bar.print_progress_bar(0)
    for i, f in enumerate(content):
        try:
            with open(os.devnull, 'w') as quiet:
                call(['2to3', generalize_path(os.path.join(DATA_PATH, f))], stderr=quiet, stdout=quiet)
        finally:
            progress_bar.print_progress_bar(i + 1)


def generalize_path(path):
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith("\\"):
        return "C:" + path
    return path


# MAIN #


if __name__ == '__main__':
    process_set()
