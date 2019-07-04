#!/usr/bin/env python3


# This script is used for housing common tools for iterating through python150k data.
# Author: Buster Major


# IMPORTS #


import os
import datetime


# CONSTANTS #


REPO_ROOT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
DATA_PATH = os.path.join(REPO_ROOT_PATH, 'data', 'py150_files')

ERROR_LOG_PATH = os.path.join(REPO_ROOT_PATH, 'log', 'dataprocessing')

TRAINING_SET_FILE_PATH = os.path.join(DATA_PATH, 'python100k_train.txt')
EVALUATION_SET_FILE_PATH = os.path.join(DATA_PATH, 'python50k_eval.txt')


def generalize_path(path):
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith("\\"):
        return "C:" + path
    return path


def get_output_data_path(file_path):
    return os.path.join(DATA_PATH, 'data_cfg' + file_path[4:])


def get_file_paths():
    content = []
    with open(TRAINING_SET_FILE_PATH, encoding='utf8') as f:
        content += f.readlines()
    with open(EVALUATION_SET_FILE_PATH, encoding='utf8') as f:
        content += f.readlines()
    return [line.strip() for line in content if os.path.basename(line.strip()) != '__init__.py']


def get_output_file_paths():
    content = get_file_paths()
    return ['data_cfg' + line.strip()[4:] for line in content if os.path.basename(line.strip()) != '__init__.py']


def handle_exception(error_log_file_path, file_path, message, stacktrace):
    with open(error_log_file_path, 'a+', encoding='utf8') as f:
        f.write('\r{},{},{},{}\n'.format(str(datetime.datetime.now()), message, file_path, stacktrace))


class ProgressBar:
    def __init__(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
        self.iteration = iteration
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill

    def print_progress_bar(self, iteration, errors):
        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (iteration / float(self.total)))
        filled_length = int(self.length * iteration // self.total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)
        print('%s |%s| %s%% (%s/%s) %s, %s %s' % (self.prefix, bar, percent, iteration, self.total, self.suffix, str(errors), 'errors'), end='\r')
        # Print New Line on Complete
        if iteration == self.total:
            print()