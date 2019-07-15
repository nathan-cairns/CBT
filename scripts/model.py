from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
import numpy as np
import os
import time
import iteratortools as it
from programtokenizer import *
import sys
import tokenize

# https://www.tensorflow.org/beta/tutorials/text/text_generation


# CONSTANTS #

ERROR_LOG_FILE = os.path.join(it.ERROR_LOG_PATH, 'modelload.csv')

BATCH_SIZE = 64
BUFFER_SIZE = 10000

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


def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(vocab_size, embedding_dim, batch_input_shape=[batch_size, None]),
        tf.keras.layers.LSTM(rnn_units, return_sequences=True, stateful=True, recurrent_initializer='glorot_uniform'),
        tf.keras.layers.Dense(vocab_size)
    ])
    return model


def loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)


def generate_text(model, start_string):
    # Evaluation step (generating text using the learned model)

    # Number of characters to generate
    num_generate = 10000

    # Converting our start string to numbers (vectorizing)
    input_eval = [token_to_index[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)

    # Empty string to store our results
    text_generated = []

    # Low temperatures results in more predictable text.
    # Higher temperatures results in more surprising text.
    # Experiment to find the best setting.
    temperature = 1.0

    # Here batch size == 1
    model.reset_states()
    for i in range(num_generate):
        predictions = model(input_eval)
        # remove the batch dimension
        predictions = tf.squeeze(predictions, 0)

        # using a categorical distribution to predict the word returned by the model
        predictions = predictions / temperature
        predicted_id = tf.random.categorical(predictions, num_samples=1)[-1, 0].numpy()

        # We pass the predicted word as the next input to the model
        # along with the previous hidden state
        input_eval = tf.expand_dims([predicted_id], 0)

        text_generated.append(index_to_token[predicted_id])

    return untokenize_string(start_string + ''.join(text_generated))


# MAIN METHOD #


if __name__ == '__main__':

    print('Scanning contents of files into memory')
    file_paths = it.get_file_paths()
    text = get_as_file(file_paths[:100])
    print('Length of text: {} characters'.format(len(text)))
    vocab = sorted(set(text))  # TODO: tokenize smarter
    print('{} unique tokens'.format(len(vocab)))

    token_to_index = {t: i for i, t in enumerate(vocab)}
    index_to_token = np.array(vocab)

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
    embedding_dimension = 256
    rnn_units = 1024

    model = build_model(
        vocab_size=len(vocab),
        embedding_dim=embedding_dimension,
        rnn_units=rnn_units,
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
    checkpoint_dir = os.path.join('.', 'training_checkpoints')
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_prefix,
        save_weights_only=True
    )

    if len(sys.argv) == 1:
        history = model.fit(dataset, epochs=EPOCHS, callbacks=[checkpoint_callback])
    else:
        model = build_model(vocab_size, embedding_dimension, rnn_units, batch_size=1)
        model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
        model.build(tf.TensorShape([1, None]))
        print(generate_text(model, start_string=u"import numpy as np\n"))
