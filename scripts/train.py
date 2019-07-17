# https://www.tensorflow.org/beta/tutorials/text/text_generation


from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
import numpy as np
import os
import time
import iteratortools as it
from programtokenizer import *
import sys
import tokenize
import model_maker
import json


# CONSTANTS #


ERROR_LOG_FILE = os.path.join(it.ERROR_LOG_PATH, 'modelload.csv')

BATCH_SIZE = 64
BUFFER_SIZE = 10000
CHECKPOINT_DIR = os.path.join('.', 'training_checkpoints')
WORD_TO_INDEX_FILE = 'word_to_index.json'

EPOCHS = 10


# FUNCTIONS #


def get_as_file(file_paths):
    to_return = ''
    files_not_found = 0
    progress_bar = it.ProgressBar(0, file_paths.__len__(), prefix='Progress:', suffix='Complete')
    progress_bar.print_progress_bar()
    for file_path in file_paths:
        try:
            with open(os.path.join(it.DATA_PATH, file_path), 'r', encoding='utf8') as f:
                to_return += tokenize_file(f.read())
                #to_return += tokenize_file(text)
        except Exception as e:
            files_not_found += 1
            it.handle_exception(ERROR_LOG_FILE, file_path, 'Unluggy', e)
            progress_bar.increment_errors()
        finally:
            progress_bar.increment_work()
            progress_bar.print_progress_bar()
    if files_not_found is not 0:
        print('{} files were unable to be found / parsed'.format(files_not_found))
    return to_return


def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text


def loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)


def write_index(index):
    if not os.path.exists(CHECKPOINT_DIR):
        os.makedirs(CHECKPOINT_DIR)
    with open(os.path.join(CHECKPOINT_DIR, WORD_TO_INDEX_FILE), 'w') as fp:
        json.dump(index, fp)

# MAIN METHOD #


if __name__ == '__main__':
    print('Scanning contents of files into memory')
    file_paths = it.get_file_paths()
    text = get_as_file(file_paths[:10])
    print('Length of text: {} characters'.format(len(text)))
    vocab = sorted(set(text))  # TODO: tokenize smarter
    print('{} unique tokens'.format(len(vocab)))

    token_to_index = {t: i for i, t in enumerate(vocab)}
    index_to_token = np.array(vocab)
    write_index(token_to_index)

    text_as_int = np.array([token_to_index[t] for t in text])

    seq_length = 100
    examples_per_epoch = len(text)//seq_length

    # Create training examples/targets
    char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int)
    sequences = char_dataset.batch(seq_length + 1, drop_remainder=True)

    dataset = sequences.map(split_input_target)
    dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)

    # Model:
    vocab_size = len(vocab)
    model = model_maker.build_model(
        vocab_size=len(vocab),
        embedding_dim=model_maker.EMBEDDING_DIMENSION,
        rnn_units=model_maker.RNN_UNITS,
        batch_size=BATCH_SIZE
    )

    for input_example_batch, target_example_batch in dataset.take(1):
        example_batch_predictions = model(input_example_batch)
        sampled_indices = tf.random.categorical(example_batch_predictions[0], num_samples=1)
        sampled_indices = tf.squeeze(sampled_indices, axis=-1).numpy()

        example_batch_loss = loss(target_example_batch, example_batch_predictions)
        print("Prediction shape: ", example_batch_predictions.shape, " # (batch_size, sequence_length, vocab_size)")
        print("scalar_loss:      ", example_batch_loss.numpy().mean())

    model.compile(optimizer='adam', loss=loss)

    # Checkpoints:
    checkpoint_prefix = os.path.join(CHECKPOINT_DIR, "ckpt_{epoch}")
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_prefix,
        save_weights_only=True
    )

    history = model.fit(dataset, epochs=EPOCHS, callbacks=[checkpoint_callback])
