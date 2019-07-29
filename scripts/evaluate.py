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

# CONSTANTS #


OUTPUT_PATH = os.path.join(it.REPO_ROOT_PATH, 'data', 'eval_output')


# ARGPARSE #


parser = argparse.ArgumentParser(description='Evaluate CBT generated code', prog='CBT')
parser.add_argument('checkpoint_dir', help='The directory of the most recent training checkpoint')
parser.add_argument('--lines', help='The number of lines to remove and then generate, the default is 1', type=int, choices=range(1,21), default=1)


# FUNCTIONS #


# TODO NEED TO COME UP WITH A BETTER WAY TO DELETE LINES CURRENTLY THIS IS SET TO +1 TO COVER DELETING EMPTY LINES AND THEN A LINE OF CODE HOWEVER THIS IS BAD AS SOMETIMES DELETES TWO LINES OF CODE
def remove_last_lines(file_path, num_lines):
    content = []
    with open(file_path, encoding='ISO-8859-1') as f:
        content += f.readlines()
    
    # TODO handle removing too many lines more gracefully
    try:
        del content[-num_lines]
    except:
        print('{} not processed as removing more lines than in file'.format(file_path))

    return content


def get_style_fails(model_output):
    # TODO Return a list of the style fails
    # Reference: text = subprocess.run(['ls', '-l'], capture_output=True)
    pass


def get_critical_fails(model_output):
    # TODO Return a list of the critical files
    # Reference: text = subprocess.run(['ls', '-l'], capture_output=True)
    pass


def get_executable(model_output):
    # TODO Return whether the file was executable
    # Reference: text = subprocess.run(['ls', '-l'], capture_output=True)
    pass


def is_same(model_output, orginal):
    # TODO return whether generated line was different or same as orginal
    # Reference: text = subprocess.run(['ls', '-l'], capture_output=True)
    pass


def evaluate(model, num_lines, state, file_paths):
    for file_path in file_paths:
        gen_start_string = ''
        with open(file_path, 'r') as f:
            gen_start_string = f.read()

        model_output = generator.generate_text(model, gen_start_string, num_lines, state['index_to_token'], state['variable_char_start'])

        # TODO aggregate results
        get_style_fails(model_output)
        get_critical_fails(model_output)
        get_executable(model_output)

    # TODO print results


# MAIN #


if __name__ == '__main__':
    # Parse Arguments
    args = parser.parse_args()
    # TODO NEED TO COME UP WITH A BETTER WAY TO DELETE LINES CURRENTLY THIS IS SET TO +1 TO COVER DELETING EMPTY LINES AND THEN A LINE OF CODE HOWEVER THIS IS BAD AS SOMETIMES DELETES TWO LINES OF CODE
    num_lines = args.lines + 1 # TODO remove + 1
    checkpoint_dir = args.checkpoint_dir

    # Remove last n lines from file and write to new file.
    file_paths = [file_path for file_path in it.get_eval_file_paths()]
    for file_path in file_paths:
        modified_text = remove_last_lines(os.path.join(it.DATA_PATH, file_path), num_lines)

        # Ensure dirs exist
        output_file_path = os.path.join(OUTPUT_PATH, file_path)
        if not os.path.exists(os.path.dirname(output_file_path)):
            try:
                os.makedirs(os.path.dirname(output_file_path))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

        with open(output_file_path, 'w') as output_file:
            output_file.writelines(modified_text)



    with open(os.path.join(checkpoint_dir, train.WORD_TO_INDEX_FILE)) as json_file:
        state = json.load(json_file)

        model = model_maker.build_model(int(state['vocab_size']), model_maker.EMBEDDING_DIMENSION, model_maker.RNN_UNITS, batch_size=1)
        model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
        model.build(tf.TensorShape([1, None]))

        # TODO use more than the first file!!!!!
        evaluate(model, num_lines, state, file_paths[0])
