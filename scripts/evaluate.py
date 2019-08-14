#!/usr/bin/env python3


# This script is used for Evaluating the results of a trained CBT model.
# Author: Nathan Cairns


# IMPORTS #


import iteratortools as it
import generator
import train
import model_maker
import evaluator

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
STAT_FILE_PATH = os.path.join(it.REPO_ROOT_PATH, 'data', 'stats.json')


# ARGPARSE #


parser = argparse.ArgumentParser(description='Evaluate CBT generated code', prog='CBT')
parser.add_argument('checkpoint_dir', help='The directory of the most recent training checkpoint')
parser.add_argument('language', help='Pick a programming language to evaluate.', choices=['py', 'c'])
parser.add_argument('--lines', help='The number of lines to remove and then generate, the default is 1', type=int, choices=range(1,21), default=1)


# FUNCTIONS #


def remove_last_lines(file_path, num_lines):
    """Removes the last n lines which contain code"""
    content = []
    with open(file_path, encoding='ISO-8859-1') as f:
        content += f.readlines()
    
    removed_counter = 0
    for i, line in reversed(list(enumerate(content))):
        if not line.isspace():
            removed_counter = removed_counter + 1
        del content[i]

        if removed_counter == num_lines:
            break

    return content


def write_output_file(output_file_path, modified_text):
    # Ensure dirs exist
    if not os.path.exists(os.path.dirname(output_file_path)):
        os.makedirs(os.path.dirname(output_file_path))

    # write to file
    with open(output_file_path, 'w') as output_file:
        output_file.writelines(modified_text)


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


def write_stats_to_file(stats, file_path_output):
    with open(file_path_output, 'w') as fp:
        json.dump(stats, fp)


# MAIN #


if __name__ == '__main__':
    # Parse Arguments
    args = parser.parse_args()
    num_lines = args.lines
    checkpoint_dir = args.checkpoint_dir
    language = args.language

    language_evaluator = None
    if language == 'py':
        language_evaluator = evaluator.PyEvaluator()
    elif language == 'c':
        language_evaluator = evaluator.CEvaluator()
    else:
        raise Exception('A language must be specified!!')

    print('Emptying eval directory...')
    shutil.rmtree(OUTPUT_PATH, ignore_errors=True)

    # Remove last n lines from file and write to new file.
    print('Preparing evaluation set...')
    file_paths = [file_path for file_path in it.get_eval_file_paths()]
    for file_path in file_paths:
        modified_text = remove_last_lines(os.path.join(it.DATA_PATH, file_path), num_lines)
        if not modified_text:
            print('Error: In {} couldn\'t remove {} lines from the file as it was not long enough. Not considering for evaluation.'.format(file_path, num_lines) )
        else:
            write_output_file(os.path.join(OUTPUT_PATH, file_path), modified_text)

    with open(os.path.join(checkpoint_dir, train.WORD_TO_INDEX_FILE)) as json_file:
        print('Building model...')
        state = json.load(json_file)
        model = model_maker.build_model(int(state['vocab_size']), model_maker.EMBEDDING_DIMENSION, model_maker.RNN_UNITS, batch_size=1)
        model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
        model.build(tf.TensorShape([1, None]))

        print('Generating model output...')
        evaluation_files = [os.path.join(OUTPUT_PATH, file_path) for file_path in it.get_eval_file_paths()]
        generate_model_output(evaluation_files)

        # TODO generate_content = 
        # {
        #   [
        #       orginal_lines: []
        #       generated_lines: []
        #       line#s: []
        #       file_name: ''
        #   ]
        # }
        generated_content = None


        print('Evaluating...')
        stats = {
            'total_number_of_files': len(evaluation_files),
            'num_lines_removed': num_lines
        }

        stats.update(language_evaluator.get_linter_stats(generated_content))

        print('Printing stats...')
        print_stats(stats)

        print('Writing stats to file...')
        write_stats_to_file(stats, STAT_FILE_PATH)

        print('Evaluation complete.')
