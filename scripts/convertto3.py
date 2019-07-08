#!/usr/bin/env python3


# This script is used for converting existing python program from python version 2 to python version 3.
# Author: Buster Major


# IMPORTS #


from subprocess import call
from iteratortools import *
import os


# CONSTANTS #


PROCESSING_CHUNK_SIZE = 50


# FUNCTIONS #


def process_set():
    if not os.path.exists(ERROR_LOG_PATH):
        os.makedirs(ERROR_LOG_PATH)

    content = get_file_paths()
    # content = content[int(content.__len__()*239/240):]
    print('Converting from python2 to python3 syntax:')

    in_chunks = chunks(content, PROCESSING_CHUNK_SIZE)
    progress_bar = ProgressBar(0, content.__len__(), prefix='Progress:', suffix='Complete')
    progress_bar.print_progress_bar(0, 0)
    for i, chunk in enumerate(in_chunks):
        try:
            for j, f in enumerate(chunk):
                chunk[j] = generalize_path(os.path.join(DATA_PATH, f))
            with open(os.devnull, 'w') as quiet:
                call(['2to3', '-w', '-n'] + chunk, stderr=quiet, stdout=quiet)
        finally:
            progress_bar.print_progress_bar((i + 1) * content.__len__(), 0)


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


# MAIN #


if __name__ == '__main__':
    process_set()
