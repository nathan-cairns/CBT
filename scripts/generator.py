import tensorflow as tf
import model_maker
import argparse
import programtokenizer
import json
import train
import os


# CONSTANTS #


NEW_LINE_TOKEN = programtokenizer.word_to_token['\n']


# ARGPARSE #


parser = argparse.ArgumentParser(description='Automatically Generate Code', prog='CBT')
parser.add_argument('checkpoint_dir', help='The directory of the most recent training checkpoint')
parser.add_argument('vocab_size', help='The size of the vocabulary', type=int)
parser.add_argument('--Cin', help='Provide input via the console')
parser.add_argument('--Fin', help='Specify a python file to take as input')
parser.add_argument('--Fout', help='Specify a file to output to')
parser.add_argument('--lines', help='The number of lines to generate, the default is 1', type=int, choices=range(1,21), default=1)


# FUNCTIONS #


def generate_text(model, start_string, num_lines):
    # Evaluation step (generating text using the learned model)

    # Converting our start string to numbers (vectorizing)
    with open(os.path.join(train.CHECKPOINT_DIR, train.WORD_TO_INDEX_FILE)) as json_file:
        index_to_token = json.load(json_file)
        token_to_index = {t: i for i, t in index_to_token.items()}

        input_eval = [index_to_token[s] for s in start_string]
        input_eval = tf.expand_dims(input_eval, 0)

        # Empty string to store our results
        text_generated = []

        # Low temperatures results in more predictable text.
        # Higher temperatures results in more surprising text.
        # Experiment to find the best setting.
        temperature = 1.0

        # Here batch size == 1
        model.reset_states()

        new_lines = 0

        while new_lines != num_lines:
            predictions = model(input_eval)
            # remove the batch dimension
            predictions = tf.squeeze(predictions, 0)

            # using a categorical distribution to predict the word returned by the model
            predictions = predictions / temperature
            predicted_id = tf.random.categorical(predictions, num_samples=1)[-1, 0].numpy()

            # We pass the predicted word as the next input to the model
            # along with the previous hidden state
            input_eval = tf.expand_dims([predicted_id], 0)

            generated_character = token_to_index[predicted_id]
            text_generated.append(generated_character)

            if generated_character == NEW_LINE_TOKEN:
                new_lines = new_lines + 1

    return programtokenizer.untokenize_string(start_string + ''.join(text_generated))


# MAIN #


if __name__ == '__main__':
    # Parse arguments
    args = parser.parse_args()
    vocab_size = args.vocab_size
    checkpoint_dir = args.checkpoint_dir
    input_dir = args.Fin
    output_dir = args.Fout
    console_input = args.Cin
    num_lines = args.lines
    gen_start_string = ''

    # Build the model
    model = model_maker.build_model(vocab_size, model_maker.EMBEDDING_DIMENSION, model_maker.RNN_UNITS, batch_size=1)
    model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
    model.build(tf.TensorShape([1, None]))

    # Read input
    if (input_dir and console_input):
        parser.error('Please specify either --Fin or --Cin, not both')

    if (input_dir):
        print('Taking input from file {}'.format(input_dir))
        with open(input_dir, 'r') as f:
            gen_start_string = f.read()
    elif (console_input):
        gen_start_string = console_input
    else:
        parser.error('No input method specified')

    # Generate output
    generated_text = generate_text(model, start_string=gen_start_string, num_lines=num_lines)

    if (output_dir):
        print("Outputing to file {}".format(output_dir))
        with open(output_dir, 'w') as f:
            f.write(generated_text)
    else:
        print(generated_text)
