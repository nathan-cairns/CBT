#!/usr/bin/env python3


# This script is used for housing common tools for iterating through python150k data.
# Author: Buster Major


# IMPORTS #


import os


# CONSTANTS #


REPO_ROOT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
DATA_PATH = os.path.join(REPO_ROOT_PATH, 'data', 'py150_files')
OUTPUT_DATA_PATH = os.path.join(DATA_PATH, 'data_cfg')

ERROR_LOG_PATH = os.path.join(REPO_ROOT_PATH, 'log', 'dataprocessing')
ERROR_LOG_FILE = os.path.join(ERROR_LOG_PATH, 'errorlog.csv')

TRAINING_SET_FILE_PATH = os.path.join(DATA_PATH, 'python100k_train.txt')
EVALUATION_SET_FILE_PATH = os.path.join(DATA_PATH, 'python50k_eval.txt')


def get_file_paths():
    with open(TRAINING_SET_FILE_PATH, encoding='utf8') as f:
        content = f.readlines()
        return [line.strip() for line in content if os.path.basename(line.strip()) != '__init__.py']
        
        
class ProgressBar:
    def __init__(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
        self.iteration = iteration
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill

    def print_progress_bar(self, iteration):
        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (iteration / float(self.total)))
        filled_length = int(self.length * iteration // self.total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)
        print('%s |%s| %s%% (%s/%s) %s' % (self.prefix, bar, percent, iteration, self.total, self.suffix), end='\r')
        # Print New Line on Complete
        if iteration == self.total:
            print()