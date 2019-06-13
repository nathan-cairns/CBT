#!/usr/bin/env python3


# This script is used for generating cfgs from python code
# Author: Nathan Cairns


# IMPORTS #


from staticfg import CFGBuilder
import os


# CONSTANTS #


DATA_PATH = './../data/py150_files'
TRAINING_SET_FILE_PATH = '{}/python100k_train.txt'.format(DATA_PATH)
EVALUATION_SET_FILE_PATH = '{}/python50k_eval.txt'.format(DATA_PATH)


# FUNCTIONS #


def process_set(file_path):
    content = []
    with open(file_path) as f:
        content = f.readlines()
        content = [line.strip() for line in content if os.path.basename(line.strip()) != '__init__.py']

    for f in content[5:8]:
        build_cfg(f)

def build_cfg(file_path):
    cfg = CFGBuilder().build_from_file(os.path.basename(file_path), '{}/{}'.format(DATA_PATH, file_path))
    cfg.build_visual('./{}'.format(os.path.basename(file_path)), format='pdf')


# MAIN #


if __name__ == '__main__':
    process_set(TRAINING_SET_FILE_PATH)
