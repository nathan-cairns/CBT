import tensorflow as tf
import model_maker
import argparse


# ARGPARSE #


parser = argparse.ArgumentParser(description='Automatically Generate Code', prog='CBT')
parser.add_argument('checkpoint_dir', help='The directory of the most recent training checkpoint')
parser.add_argument('vocab_size', help='The size of the vocabulary')
parser.add_argument('--Cin', help='Provide input via the console')
parser.add_argument('--Fin', help='Specify a python file to take as input')
parser.add_argument('--Fout', help='Specify a file to output to')


# FUNCTIONS #


def generate_text(model, start_string, num_generate):
    # Evaluation step (generating text using the learned model)

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


# MAIN #


if __name__ == '__main__':
    # Parse arguments
    args = parser.parse_args()
    vocab_size = args.vocab_size
    checkpoint_dir = args.checkpoint_dir
    input_dir = args.Fin
    output_dir = args.Fout
    console_input = args.Cin
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
    generated_text = generate_text(model, start_string=gen_start_string, num_generate=10)

    if (output_dir):
        print("Outputing to file {}".format(output_dir))
        with open(output_dir, 'w') as f:
            f.write(generated_text)
    else:
        print(generate_text)
