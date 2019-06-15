#!/usr/bin/env python3


# This script is used for generating cfgs from python code
# Author: Nathan Cairns


# IMPORTS #


from staticfg import CFGBuilder
from subprocess import call, DEVNULL
import os
import datetime


# CONSTANTS #


REPO_ROOT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
DATA_PATH = os.path.join(REPO_ROOT_PATH, 'data', 'py150_files')
OUTPUT_DATA_PATH = os.path.join(DATA_PATH, 'data_cfg')

ERROR_LOG_PATH = os.path.join(REPO_ROOT_PATH, 'log', 'dataprocessing')
ERROR_LOG_FILE = os.path.join(ERROR_LOG_PATH, 'errorlog.csv')

TRAINING_SET_FILE_PATH = os.path.join(DATA_PATH, 'python100k_train.txt')
EVALUATION_SET_FILE_PATH = os.path.join(DATA_PATH, 'python50k_eval.txt')


# GLOBAL VARIABLES #

err_no = 0


# FUNCTIONS #

# TODO: convert dataset to python 3?
# TODO: add graphviz step in readme and add to envir vars


def process_set(file_path):
    content = []
    with open(file_path, encoding='utf8') as f:
        content = f.readlines()
        content = [line.strip() for line in content if os.path.basename(line.strip()) != '__init__.py']

    if not os.path.exists(OUTPUT_DATA_PATH):
        os.makedirs(OUTPUT_DATA_PATH)

    print_progress_bar(0, content.__len__(), prefix='Progress:', suffix='Complete')
    for i, f in enumerate(content):
        try:
            with open(os.devnull, 'w') as shut_up:
                call(['2to3', generalize_path(os.path.join(DATA_PATH, f))], stderr=shut_up, stdout=shut_up)
            build_cfg(f)
        except Exception as e:
            global err_no
            err_no += 1
            handle_exception(f, 'Error in building cfg file', e)
        finally:
            print_progress_bar(i + 1, content.__len__(), prefix='Progress:', suffix='Complete')


def generalize_path(path):
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith("\\"):
        return "C:" + path
    return path

def build_cfg(file_path):
    cfg = CFGBuilder().build_from_file(os.path.basename(file_path), os.path.join(DATA_PATH, file_path))
    cfg.build_visual(os.path.join(OUTPUT_DATA_PATH, file_path), format='dot', calls=False, show=False)
    os.remove(os.path.join(OUTPUT_DATA_PATH, file_path))  # Delete the other weird file created


def handle_exception(file_path, message, stacktrace):
    if not os.path.exists(ERROR_LOG_PATH):
        os.makedirs(ERROR_LOG_PATH)
    with open(ERROR_LOG_FILE, 'w+', encoding='utf8') as f:
        f.write('\r{},{},{},{}\n'.format(str(datetime.datetime.now()), message, file_path, stacktrace))


# courtesy of https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('%s |%s| %s%% (%s/%s) %s' % (prefix, bar, percent, iteration, total, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


# MAIN #

if __name__ == '__main__':
    process_set(TRAINING_SET_FILE_PATH)

    if err_no is not 0:
        print('WARN Data pre-processing was unable to process {} files!'.format(err_no))
        print('WARN Refer to log/dataprocessing/errorlog.csv for more details.')
