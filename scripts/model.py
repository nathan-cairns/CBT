from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
import numpy as np
import os
import time
import iteratortools as it


def get_as_file(file_paths):
    to_return = ''
    files_not_found = 0
    progress_bar = it.ProgressBar(0, file_paths.__len__(), prefix='Progress:', suffix='Complete')
    progress_bar.print_progress_bar()
    for file_path in file_paths:
        try:
            with open(os.path.join(it.DATA_PATH, file_path), 'r', encoding='utf8') as f:
                to_return += '\n' + f.read()  # TODO: insert some end of file character here?
        except FileNotFoundError:
            files_not_found += 1
            progress_bar.increment_errors()
        finally:
            progress_bar.increment_work()
            progress_bar.print_progress_bar()
    if files_not_found is not 0:
        print('{} files were unable to be found'.format(files_not_found))
    return to_return


def tokenize():
    a = 1


if __name__ == '__main__':
    print('Scanning contents of files into memory')
    file_paths = it.get_file_paths()
    text = get_as_file(file_paths[:1000])
    print('Length of text: {} characters'.format(len(text)))
    vocab = sorted(set(text))  # TODO: tokenize smarter
    print('{} unique tokens'.format(len(vocab)))

    token_to_index = {t: i for i, t in enumerate(vocab)}
    index_to_token = np.array(vocab)

    text_as_int = np.array([token_to_index[t] for t in text])

    
