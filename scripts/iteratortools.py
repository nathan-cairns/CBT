#!/usr/bin/env python3


# This script is used for housing common tools for iterating through python150k data.
# Author: Buster Major


# IMPORTS #


import os
import datetime
from threading import Lock
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing


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


def get_file_paths(training_only=False):
    content = []
    with open(TRAINING_SET_FILE_PATH, encoding='utf8') as f:
        content += f.readlines()
    if not training_only:
        with open(EVALUATION_SET_FILE_PATH, encoding='utf8') as f:
            content += f.readlines()
    return [line.strip() for line in content if os.path.basename(line.strip()) != '__init__.py']


def get_cfg_file_paths():
    content = get_file_paths()
    return ['data_cfg' + line.strip()[4:] + '.dot' for line in content if os.path.basename(line.strip()) != '__init__.py']


def handle_exception(error_log_file_path, file_path, message, stacktrace):
    with open(error_log_file_path, 'a+', encoding='utf8') as f:
        f.write('\r{},{},{},{}\n'.format(str(datetime.datetime.now()), message, file_path, stacktrace))


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def iterate(task, error_file_path, content, proportion=0, chunk_size=1):
    total = content.__len__() / chunk_size
    progress_bar = ProgressBar(total * proportion, total, prefix='Progress:', suffix='Complete')
    progress_bar.print_progress_bar()

    error_file_lock = Lock()
    increment_work_lock = Lock()
    increment_errors_lock = Lock()

    def an_iteration(file):
        try:
            task(file)
        except Exception as e:
            with increment_errors_lock:
                progress_bar.increment_errors()
            with error_file_lock:
                handle_exception(error_file_path, file, 'Error in doing thing', e)
        finally:
            with increment_work_lock:
                progress_bar.increment_work()
                progress_bar.print_progress_bar()

    pool = multiprocessing.dummy.Pool(multiprocessing.cpu_count())
    pool.map(an_iteration, content)


class ProgressBar:
    def __init__(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
        self.iteration = iteration
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.errors = 0

    def increment_work(self):
        self.iteration += 1

    def increment_errors(self):
        self.errors += 1

    def print_progress_bar(self):
        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (self.iteration / float(self.total)))
        filled_length = int(self.length * self.iteration // self.total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)
        print('%s |%s| %s%% (%s/%s) %s, %s %s' % (self.prefix, bar, percent, self.iteration, self.total, self.suffix, str(self.errors), 'errors'), end='\r')
        # Print New Line on Complete
        if self.iteration == self.total:
            print()
