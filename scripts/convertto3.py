#!/usr/bin/env python3


# This script is used for converting existing python program from python version 2 to python version 3.
# Author: Buster Major


# IMPORTS #


from subprocess import call
import iteratortools as it
import os


# CONSTANTS #


PROCESSING_CHUNK_SIZE = 50


# FUNCTIONS #


def normalize_indenting(string):
    lines = string.split('\n')
    space_no = 0
    start_line = 0
    while len(lines[start_line]) == 0:
        start_line += 1
    line_index = 0
    char = lines[start_line][line_index]
    while char == ' ' or char == '\n':
        if char == ' ':
            space_no += 1
        line_index += 1
        char = lines[start_line][line_index]

    for i, line in enumerate(lines):
        lines[i] = line[space_no:]

    return '\n'.join(lines)


def process_set():
    if not os.path.exists(it.ERROR_LOG_PATH):
        os.makedirs(it.ERROR_LOG_PATH)

    if not os.path.exists(os.path.join(os.getcwd(), 'temp')):
        os.mkdir(os.path.join(os.getcwd(), 'temp'))
    print('Reading in Python files...')
    programs = it.get_lang_files('python')
    file_id = 0
    print('Writing python files to temp directory...')
    progress_bar = it.ProgressBar(0, len(programs))
    for program in programs:
        try:
            with open(os.path.join(os.getcwd(), 'temp', str(file_id) + '.py'), 'w+', encoding='utf8') as f:
                f.write(normalize_indenting(program))
            file_id += 1
            progress_bar.increment_work()
        except Exception:
            progress_bar.increment_errors()
        finally:
            progress_bar.print_progress_bar()

    content = [os.path.join(os.getcwd(), 'temp', '{}.py'.format(i)) for i in range(file_id)]
    # content = content[int(content.__len__()*239/240):]
    print('Converting from python2 to python3 syntax...')

    in_chunks = chunks(content, PROCESSING_CHUNK_SIZE)
    progress_bar = it.ProgressBar(0, content.__len__(), prefix='Progress:', suffix='Complete')
    progress_bar.print_progress_bar()
    for i, chunk in enumerate(in_chunks):
        try:
            for j, f in enumerate(chunk):
                chunk[j] = it.generalize_path(os.path.join(it.DATA_PATH, f))
            with open(os.devnull, 'w') as quiet:
                call(['2to3', '-w', '-n'] + chunk, stderr=quiet, stdout=quiet)
            progress_bar.increment_work()
        except Exception:
            progress_bar.increment_errors()
        finally:
            progress_bar.print_progress_bar()


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


# MAIN #


if __name__ == '__main__':
    process_set()
