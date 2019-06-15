#!/usr/bin/env python3


# This script is used for generating cfgs from python code
# Author: Nathan Cairns


# IMPORTS #


from staticfg import CFGBuilder
import os
import datetime


# CONSTANTS #


REPO_ROOT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
DATA_PATH = os.path.join(REPO_ROOT_PATH, 'data', 'py150_files')

ERROR_LOG_PATH = os.path.join(REPO_ROOT_PATH, 'log', 'dataprocessing')
ERROR_LOG_FILE = os.path.join(ERROR_LOG_PATH, 'errorlog.csv')

TRAINING_SET_FILE_PATH = os.path.join(DATA_PATH, 'python100k_train.txt')
EVALUATION_SET_FILE_PATH = os.path.join(DATA_PATH, 'python50k_eval.txt')


# FUNCTIONS #

# TODO: if there are errors tell the user at the end
# TODO: progress bar

def process_set(file_path):
    content = []
    try:
        with open(file_path, encoding="utf8") as f:
            content = f.readlines()
            content = [line.strip() for line in content if os.path.basename(line.strip()) != '__init__.py']
    except Exception as e:
        print("exception!")
        handle_exception(file_path, 'Error in reading file', str(e))

    # for f in content[5:8]:
    #   build_cfg(f)


def build_cfg(file_path):
    cfg = CFGBuilder().build_from_file(os.path.basename(file_path), '{}/{}'.format(DATA_PATH, file_path))
    cfg.build_visual('./{}'.format(os.path.basename(file_path)), format='pdf')


def handle_exception(file_path, message, stacktrace):
    if not os.path.exists(ERROR_LOG_PATH):
        os.makedirs(ERROR_LOG_PATH)
    with open(ERROR_LOG_FILE, 'w+') as f:
        f.write('{},{},{},{}\n'.format(str(datetime.datetime.now()), message, file_path, stacktrace))


# MAIN #

if __name__ == '__main__':
    process_set(TRAINING_SET_FILE_PATH)
