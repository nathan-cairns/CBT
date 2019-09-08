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
    plt.xticks(np.arange(len(distance_vectors)), ['Trained on 10% of data',
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
    plt.xticks(np.arange(len(first_keywords)), ['Trained on 10% of data',
                                                'Trained on 50% of data',
                                                'Trained on 75% of data',
                                                'Trained on 100% of data'])
    plt.legend()
    plt.show()


def plot_keyword_stats(eval_objects):
    gen_keywords = {k: v['keyword_stats']['generated_keyword_frequencies'] for k, v in eval_objects.items()}

    keywords = []
    gen_keyword_data = []
    for k in gen_keywords:
        sorted_kwords = sorted(gen_keywords[k].items(), key=lambda kv: kv[0])
        gen_keyword_data.append([kv[1] for kv in sorted_kwords])
        keywords = [kv[0] for kv in sorted_kwords]

    print(keywords)
    print(gen_keyword_data)

    gen_df = pd.DataFrame(data=gen_keyword_data, columns=keywords)
    print(gen_df)
    fig = px.bar(gen_df)
    fig.show()


if __name__ == '__main__':
    eval_dir = sys.argv[1]
    eval_files = {}
    for file in os.listdir(os.path.join(os.getcwd(), eval_dir)):
        with open(os.path.join(os.path.join(os.getcwd(), eval_dir, file), 'stats.json')) as f:
            eval_files[file] = json.load(f)

    sorted_eval_objects = sorted(eval_files.items(), key=lambda x: int(re.compile(r"[0-9]+").search(x[0]).group(0)))

    plot_first_keyword_and_variable_stats(sorted_eval_objects)
    plot_distance_vector_stats(sorted_eval_objects)

    #plot_keyword_stats(eval_files)