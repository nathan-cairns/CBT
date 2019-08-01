#!/usr/bin/env python3


# This script is used for Evaluating the results of a trained CBT model.
# Author: Nathan Cairns


# IMPORTS #


import iteratortools as it
import generator
import train
import model_maker

import subprocess
import os
import argparse
import json
import shutil
import re
import tensorflow as tf
import operator
import collections


# CONSTANTS #


OUTPUT_PATH = os.path.join(it.REPO_ROOT_PATH, 'data', 'eval_output')
PROCESSING_CHUNK_SIZE = 50


# ARGPARSE #


parser = argparse.ArgumentParser(description='Evaluate CBT generated code', prog='CBT')
parser.add_argument('checkpoint_dir', help='The directory of the most recent training checkpoint')
parser.add_argument('--lines', help='The number of lines to remove and then generate, the default is 1', type=int, choices=range(1,21), default=1)


# FUNCTIONS #


def remove_last_lines(file_path, num_lines):
    content = []
    with open(file_path, encoding='ISO-8859-1') as f:
        content += f.readlines()
    
    # TODO handle removing too many lines more gracefully
    # TODO remove more than just the last line
    # TODO only remove lines with code in them
    try:
        del content[-num_lines]
    except:
        print('{} not processed as removing more lines than in file'.format(file_path))

    return content


def write_output_file(output_file_path, modified_text):
    # Ensure dirs exist
    if not os.path.exists(os.path.dirname(output_file_path)):
        os.makedirs(os.path.dirname(output_file_path))

    # write to file
    with open(output_file_path, 'w') as output_file:
        output_file.writelines(modified_text)


def run_linter(chunk):
    # From: https://pylint.readthedocs.io/en/latest/user_guide/message-control.html
    # C convention related checks
    # R refactoring related checks
    # W various warnings
    # E errors, for probable bugs in the code
    # F fatal, if an error occurred which prevented pylint from doing further processing.
    pipeline = subprocess.Popen(['pylint', '--msg-template=\'{msg_id}\''] + chunk, stdout=subprocess.PIPE)
    console_output = pipeline.communicate()
    return re.findall(r'[CRWEF]\d{4}', str(console_output))


def is_same(model_output, orginal):
    # TODO return whether generated line was different or same as orginal
    pass


def generate_model_output(file_paths):
    # Use model to generate evaulation set
    for file_path in file_paths:
        # Read contents of file
        gen_start_string = ''
        with open(file_path, 'r') as f:
            gen_start_string = f.read()

        model_output = generator.generate_text(model, gen_start_string, num_lines, state['index_to_token'], state['variable_char_start'])
        with open(file_path, 'w') as output_file:
            output_file.writelines(model_output)


def evaluate(model, num_lines, state, file_paths):
    # For C and R prefixes
    style_fails = {}
    # For W and E prefixes
    warnings = {}
    # For F prefixes
    fatal_errors = {}

    # Batch and lint to evaluate
    in_chunks = chunks(file_paths, PROCESSING_CHUNK_SIZE)
    progress_bar = it.ProgressBar(0, file_paths.__len__(), prefix='Progress:', suffix='Complete')
    progress_bar.print_progress_bar()
    for chunk in in_chunks:
        linting_results = run_linter(chunk)
        print(linting_results)
        for linting_result in linting_results:
            prefix = linting_result[0]
            if prefix == 'C' or prefix == 'R':
                style_fails[linting_result] = 1 if linting_result not in style_fails else style_fails[linting_result] + 1 
            elif prefix == 'W' or prefix == 'E':
                warnings[linting_result] = 1 if linting_result not in warnings else warnings[linting_result] + 1
            elif prefix == 'F':
                fatal_errors[linting_result] = 1 if linting_result not in fatal_errors else fatal_errors[linting_result] + 1
            else:
                print('invalid prefix: {}'.format(prefix))

    return {
        'style_fails': style_fails,
        'warnings': warnings,
        'fatal_errors': fatal_errors
    }


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def print_stats(stats):
    for stat, stat_values in stats.items():
        print('\n==============================')
        if isinstance(stat_values, dict):
            print('{}:'.format(stat))
            print('==============================')
            sorted_tuple = sorted(stat_values.items(), key=operator.itemgetter(1))
            sorted_dict = collections.OrderedDict(sorted_tuple)
            for stat_value_key, stat_value in sorted_dict.items():
                print('{}: {}'.format(stat_value_key, stat_value))
        else:
            print('{}: {}'.format(stat, stat_values))
            print('==============================')


# MAIN #


if __name__ == '__main__':
    # Parse Arguments
    args = parser.parse_args()
    num_lines = args.lines
    checkpoint_dir = args.checkpoint_dir

    # Empty eval files dir
    print('Emptying eval directory...')
    shutil.rmtree(OUTPUT_PATH, ignore_errors=True)

    # Remove last n lines from file and write to new file.
    print('Preparing evaluation set...')
    file_paths = [file_path for file_path in it.get_eval_file_paths()]
    for file_path in file_paths:
        modified_text = remove_last_lines(os.path.join(it.DATA_PATH, file_path), num_lines)
        write_output_file(os.path.join(OUTPUT_PATH, file_path), modified_text)

    # Build model and evaluate
    print('Building model...')
    with open(os.path.join(checkpoint_dir, train.WORD_TO_INDEX_FILE)) as json_file:
        state = json.load(json_file)

        model = model_maker.build_model(int(state['vocab_size']), model_maker.EMBEDDING_DIMENSION, model_maker.RNN_UNITS, batch_size=1)
        model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
        model.build(tf.TensorShape([1, None]))

        # Generate model answers
        print('Generating model output')
        evaluation_files = [os.path.join(OUTPUT_PATH, file_path) for file_path in it.get_eval_file_paths()]
        generate_model_output(evaluation_files)

        # Evaluate the model
        print('Evaluating...')
        stats = {
            'total_number_of_files': len(evaluation_files)
        }
        stats.update(evaluate(model, num_lines, state, evaluation_files))

        print('Evaluation complete.')
        print_stats(stats)
