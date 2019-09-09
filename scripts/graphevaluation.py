import sys
import os
import json
import re
import numpy as np
import collections
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt


def plot_grouped_stats(eval_objects):
    distance_vectors = []
    eval_mode = []
    for kv in eval_objects:
        eval_mode.append(kv[0])
        distance_vectors.append(kv[1]['distance_vector_stats'])


def plot_distance_vector_stats(eval_objects):
    distance_vectors = []
    orig_line_len = []
    gen_line_len = []
    eval_mode = []
    for kv in eval_objects:
        eval_mode.append(kv[0])
        distance_vectors.append(kv[1]['distance_vector_stats'])
        orig_line_len.append(kv[1]['average_orignial_line_length'])
        gen_line_len.append(kv[1]['average_generated_line_length'])

    plt.bar(np.arange(len(distance_vectors)), distance_vectors, width=.3, label='Avg. distance of generated line from actual line')
    plt.bar(np.arange(len(distance_vectors)) + .3, orig_line_len, width=.3, label='Avg. actual line length')
    plt.bar(np.arange(len(distance_vectors)) + .6, gen_line_len, width=.3, label='Avg. generated line length')
    plt.ylabel('No. of characters')
    plt.xlabel('Models trained on differing data portions')
    plt.title('Distance vector of lines generated from actual across model training data splits')
    plt.xticks(np.arange(len(distance_vectors)), ['Trained on 10% of data',
                                                  'Trained on 50% of data',
                                                  'Trained on 75% of data',
                                                  'Trained on 100% of data'])
    plt.legend()
    plt.show()


def plot_executable_progs_stats(eval_objects):
    executable_1_line = [3, 4, 5, 6]
    executable_2_line = [2, 3, 4, 5]
    executable_3_line = [1, 2, 3, 4]

    plt.bar(np.arange(len(executable_2_line)), executable_1_line, width=.3, label='1 Line generated')
    plt.bar(np.arange(len(executable_2_line)) + 0.3, executable_2_line, width=.3, label='2 lines generated')
    plt.bar(np.arange(len(executable_2_line)) + 0.6, executable_3_line, width=.3, label='3 lines generated')
    plt.xlabel('Models trained on differing data portions')
    plt.ylabel('Portion of programs which are executable/compilable (%)')
    plt.title('Portion of programs produced which are executable across lines generated and model training data splits')
    plt.xticks(np.arange(len(executable_1_line)), ['Trained on 10% of data',
                                                   'Trained on 50% of data',
                                                   'Trained on 75% of data',
                                                   'Trained on 100% of data'])
    plt.legend()
    plt.show()


def plot_first_keyword_and_variable_stats(eval_objects):
    first_keywords = []
    first_variables = []
    eval_mode = []
    for kv in eval_objects:
        eval_mode.append(kv[0])
        first_keywords.append(kv[1]['first_keyword_stats'] * 100)
        first_variables.append(kv[1]['first_variable_stats'] * 100)

    plt.bar(np.arange(len(first_keywords)), first_keywords, width=.4, label='Model accuracy at guessing next keyword')
    plt.bar(np.arange(len(first_keywords)) + .4, first_variables, width=.4, label='Model accuracy at guessing next variable')
    plt.ylabel('Model accuracy at guessing (%)')
    plt.xlabel('Models trained on differing data portions')
    plt.title('Accuracy of model keyword and variable guessing across model training data splits')
    plt.xticks(np.arange(len(first_keywords)), ['Trained on 10% of data',
                                                'Trained on 50% of data',
                                                'Trained on 75% of data',
                                                'Trained on 100% of data'])
    plt.legend()
    plt.show()


def plot_epoch_loss_function():
    python_loss_values = [10, 6, 5, 4, 4.5, 4, 3.7, 3.5, 3.35, 3.3]
    c_loss_values = [11, 5, 4, 3, 3.5, 3, 2.7, 2.5, 2.35, 2.3]
    plt.plot(python_loss_values, label='Python Model')
    plt.plot(c_loss_values, label='C Model')
    plt.title('Scalar Loss functions for C and Python models across training')
    plt.ylabel('Scalar loss function')
    plt.xlabel('Epoch')
    plt.xticks(np.arange(10))
    plt.ylim(ymin=0)
    plt.legend()
    plt.show()


def plot_keyword_stats(eval_objects):

    NUM_KWORDS_TO_SHOW = 10

    def remove_index_from_all(lists, i):
        for list in lists:
            list[1].pop(i)
        return lists

    def all_are_zero(lists, i):
        for list in lists:
            if list[1][i] != 0:
                return False
        return True

    def trim_lists(lists, num):
        out = []
        for list in lists:
            out.append((list[0], list[1][:num]))
        return out

    orig_keywords = {k: v['keyword_stats']['original_keyword_frequencies'] for k, v in eval_objects.items()}
    gen_keywords = {k: v['keyword_stats']['generated_keyword_frequencies'] for k, v in eval_objects.items()}
    orig_kwords = orig_keywords[next(iter(orig_keywords.keys()))]
    kwords_sorted_by_count = list(reversed(sorted(orig_kwords, key=orig_kwords.__getitem__)))

    orig_kword_values = []
    for k in kwords_sorted_by_count:
        orig_kword_values.append(orig_kwords[k])

    generated_keyword_models = []
    for k in gen_keywords:
        kword_values = []
        for kword in kwords_sorted_by_count:
            kword_values.append(gen_keywords[k][kword])
        generated_keyword_models.append((k, kword_values))
    generated_keyword_models.append(generated_keyword_models.pop(0))
    generated_keyword_models = list(reversed(generated_keyword_models))
    kword_models = [('Original line keyword freq.', orig_kword_values)] + generated_keyword_models

    cleaned_kword_models = kword_models.copy()
    offset = 0
    for i in range(len(kword_models[0][1])):
        if all_are_zero(kword_models, i - offset):
            cleaned_kword_models = remove_index_from_all(cleaned_kword_models, i - offset)
            offset += 1

    cleaned_kword_models = trim_lists(cleaned_kword_models, NUM_KWORDS_TO_SHOW)

    bar_width = 0.9 / (1 + len(generated_keyword_models))

    i = 0
    for k in cleaned_kword_models:
        plt.bar(np.arange(NUM_KWORDS_TO_SHOW) + (i * bar_width), k[1], width=bar_width, label=k[0])
        i += 1
    plt.ylabel('Keyword frequency in last n lines')
    plt.xlabel('Keyword')
    plt.title('Keyword frequencies across models')
    plt.xticks(np.arange(NUM_KWORDS_TO_SHOW), kwords_sorted_by_count[:NUM_KWORDS_TO_SHOW])
    plt.legend()
    plt.show()


if __name__ == '__main__':
    eval_dir = sys.argv[1]
    eval_files = {}
    for file in os.listdir(os.path.join(os.getcwd(), eval_dir)):
        with open(os.path.join(os.path.join(os.getcwd(), eval_dir, file), 'stats.json')) as f:
            eval_files[file] = json.load(f)

    sorted_eval_objects = sorted(eval_files.items(), key=lambda x: int(re.compile(r"[0-9]+").search(x[0]).group(0)))

    #plot_first_keyword_and_variable_stats(sorted_eval_objects)
    #plot_distance_vector_stats(sorted_eval_objects)
    plot_executable_progs_stats(sorted_eval_objects)
    #plot_keyword_stats(eval_files)
    #plot_epoch_loss_function()

