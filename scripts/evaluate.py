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
import sys
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
GENERATED_CONTENT_FILE_PATH = os.path.join(it.REPO_ROOT_PATH, 'data', 'generated_cotent.json')


# ARGPARSE #


parser = argparse.ArgumentParser(description='Evaluate CBT generated code', prog='CBT')
parser.add_argument('checkpoint_dir', help='The directory of the most recent training checkpoint')
parser.add_argument('language', help='Pick a programming language to evaluate.', choices=['py', 'c'])
parser.add_argument('output_environment', help='Distinct name of the directory where the evaluator will do its work, necessary if many of this script are run parallel')
parser.add_argument('--lines', help='The number of lines to remove and then generate, the default is 1', type=int, choices=range(1,21), default=1)
parser.add_argument('--num_files', help='Specify the number of files to evaluate, helpful if theres heaps to reduce work load', type=int, default=-1)


# FUNCTIONS #


def remove_last_lines(program, num_lines):
    """Removes the last n lines which contain code"""
    content = program.split('\n')
    removed_lines = []
    removed_counter = 0
    for i, line in reversed(list(enumerate(content))):
        if line.strip() and line.strip() != '}':
            removed_counter = removed_counter + 1
            removed_lines.append(content[i].strip())

        del content[i]

        if removed_counter == num_lines:
            break

    return content, removed_lines


def write_output_file(output_file_path, modified_text):
    # Ensure dirs exist
    if not os.path.exists(os.path.dirname(output_file_path)):
        os.makedirs(os.path.dirname(output_file_path))

    # write to file
    with open(output_file_path, 'w', encoding='utf8') as output_file:
        output_file.write('\n'.join(modified_text) + '\n')


def generate_model_output(generated_content, language):
    progress_bar = it.ProgressBar(0, len(generated_content))
    progress_bar.print_progress_bar()
    # Use model to generate evaulation set
    to_be_removed = []
    for i, item in enumerate(generated_content):
        try:
            # Read contents of file
            file_path = item['file_name']
            gen_start_string = ''
            with open(file_path, 'r', encoding='utf8') as f:
                gen_start_string = f.read()

            model_output, generated_lines = generator.generate_text(model, language, gen_start_string, num_lines, state['index_to_token'], state['variable_char_start'])
            with open(file_path, 'w') as output_file:
                output_file.writelines(model_output)
            generated_content[i].update({
                'generated_lines': generated_lines
            })
        except Exception as e:
            progress_bar.increment_errors()
            to_be_removed.append(item)
        finally:
            progress_bar.increment_work()
            progress_bar.print_progress_bar()

    for remove_me in to_be_removed:
        generated_content.remove(remove_me)
    return generated_content


def print_stats(stats):
    for stat, stat_values in stats.items():
        print('\n==============================')
        if isinstance(stat_values, dict):
            print('{}: {}'.format(stat, stat_values))
            print('==============================')
        else:
            print('{}: {}'.format(stat, stat_values))
            print('==============================')


def write_dict_to_file(stats, file_path_output):
    with open(file_path_output, 'w') as fp:
        json.dump(stats, fp)


def sorted_alphanumeric(data):
    convert = lambda text: int(text.split('.')[0]) if text.split('.')[0].isdigit() else text.split('.')[0].lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(data, key=alphanum_key)


# MAIN #


if __name__ == '__main__':
    generated_content = []

    # Parse Arguments
    args = parser.parse_args()
    num_lines = args.lines
    checkpoint_dir = args.checkpoint_dir
    language = args.language
    environment = args.output_environment
    num_files = args.num_files

    environment = os.path.join(it.REPO_ROOT_PATH, 'data', environment)

    language_evaluator = None
    if language == 'py':
        language_evaluator = evaluator.PyEvaluator()
    elif language == 'c':
        language_evaluator = evaluator.CEvaluator()
    else:
        raise Exception('A language must be specified!!')

    print('Emptying eval directory...')
    shutil.rmtree(environment, ignore_errors=True)

    # Remove last n lines from file and write to new file.
    print('Preparing evaluation set...')
    if language == 'c':
        programs = [file_path for file_path in it.get_lang_files(language, evaluation_only=True)] if num_files == -1 else [file_path for file_path in it.get_lang_files(language, evaluation_only=True)[:num_files]]
    if language == 'py':
        programs = []
        files = os.listdir(os.path.join(it.REPO_ROOT_PATH, 'data', 'python_files_use_this')) if num_files == -1 else sorted_alphanumeric(os.listdir(os.path.join(it.REPO_ROOT_PATH, 'data', 'python_files_use_this')))[:num_files]
        for file_name in files:
            with open(os.path.join(it.REPO_ROOT_PATH, 'data', 'python_files_use_this', file_name), encoding='utf8') as f:
                programs += [f.read()]

    progress_bar = it.ProgressBar(0, len(programs))
    progress_bar.print_progress_bar()
    for i, program in enumerate(programs):
        if num_files != None and i >= num_files:
            break

        modified_text, removed_lines = remove_last_lines(program, num_lines)
        if not modified_text:
            print('Error: In {} couldn\'t remove {} lines from the file as it was not long enough. Not considering for evaluation.'.format(str(i), num_lines) )
        else:
            output_file_name = os.path.join(environment, 'eval_output', '{}.py'.format(str(i)))
            write_output_file(output_file_name, modified_text)
            item = {
                'original_lines': removed_lines,
                'file_name': output_file_name,
                'original_program': program
            }
            generated_content.append(item)

        progress_bar.increment_work()
        progress_bar.print_progress_bar()

    with open(os.path.join(checkpoint_dir, train.WORD_TO_INDEX_FILE)) as json_file:
        print('Building model...')
        state = json.load(json_file)
        model = model_maker.build_model(int(state['vocab_size']), model_maker.EMBEDDING_DIMENSION, model_maker.RNN_UNITS, batch_size=1)
        model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
        model.build(tf.TensorShape([1, None]))

        print('Generating model output...')
        generated_content = generate_model_output(generated_content, language)

        stats = {
            'total_number_of_files': len(generated_content),
            'num_lines_removed': num_lines
        }

        print('Writing generated content to file...')
        write_dict_to_file(generated_content, os.path.join(environment, 'generated_content.json'))

        # TODO uncomment when lint stats work (return just lint for gen line number)
        # stats.update(language_evaluator.get_linter_stats(generated_content))
        print('Calculating evaluation statistics...')
        stats.update({
            'distance_vector_stats': language_evaluator.get_distance_vector_stats(generated_content),
            'average_orignial_line_length': language_evaluator.get_average_original_line_length(generated_content),
            'average_generated_line_length': language_evaluator.get_average_generated_line_length(generated_content),
            'keyword_stats': language_evaluator.get_keyword_stats(generated_content),
            'variable_stats': language_evaluator.get_variable_stats(generated_content),
            'first_keyword_stats': language_evaluator.get_first_keyword_stats(generated_content),
            'first_variable_stats': language_evaluator.get_first_variable_stats(generated_content),
            'avg_var_count_in_non_generated_prog': language_evaluator.get_avg_var_count_in_non_generated_prog(generated_content)
        })

        print('Printing stats...')
        print_stats(stats)

        print('Writing stats to file...')
        write_dict_to_file(stats, os.path.join(environment, 'stats.json'))

        print('Evaluation complete.')
