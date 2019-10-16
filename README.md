# CBT (Code By Tensors)

This project aims to automatically generate code using LSTMs.

This repository contains scripts for preparing training data, training machine learning models, and generating code.

This is an University of Auckland Engineering Part Four Honours Project.
## Getting Started
C code beautifier
Clang
1. Clone the repo and set up your Python environment to use `Python 3.6` (requirements from Tensorflow).
2. Run ``python setup.py install``. This will get you *most* of the dependencies needed for running training and generation scripts.
3. Download the datasets from [kaggle](https://www.kaggle.com/arjoonn/codechef-competitive-programming). Unzip the files and place them in the `data` directory of the cloned repository (see below).
```
CBT
└── data
    ├── codechef-competitive-programming
    |   ├── program_codes
    |   |   ├── first.csv
    |   |   ├── second.csv
    |   |   └── third.csv
    |   ├── questions.csv
    |   └── solutions.csv
    └── .gitkeep
```
4. Download the [C-Code-Beautifier](https://github.com/ayonious/C-Code-Beautifier/) library and follow the instructions to obtain a compiled binary called `C-Code-Beautifier` for your machine. You may have to compile directly from the source code if on Windows. Once you have an executable, move this to the `lib` directory in the cloned repository (see below).
```
CBT
└── lib
    ├── C-Code-Beautifier.exe
    └── .gitkeep
```
5. Download [LLVM](http://releases.llvm.org/download.html) and ensure it is callable from your command line. For Windows, this will mean adding `LLVM\bin` to your `PATH` and on Linux this will differ. To test its callability from the command line, use the command `> clang` and ensure the command is recognized.


## Usage
### generator.py
The generator can be used to generate a number of lines of code based on a seed sequence.

A summary of arguments is provided below:
```
positional arguments:
  checkpoint_dir        The directory of the most recent training checkpoint
  language              The language being generated

optional arguments:
  -h, --help            show this help message and exit
  --Cin CIN             Provide input via the console
  --Fin FIN             Specify a python file to take as input
  --Fout FOUT           Specify a file to output to
  --lines {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19, 20}
                        The number of lines to generate, the default is 1
```
Use `python generator.py --help` for more info.

### train.py
This script is used to train a LSTM code generation model.

The usage is as follows:
`python train.py [language] [checkpoint_dir] [portion_to_train] [load_from_file]`

### evaluate.py
This script is used to evaluate the performance of a given LSTM code generation model.

A summary of arguments is provided below:
```
positional arguments:
  checkpoint_dir        The directory of the most recent training checkpoint
  language              Pick a programming language to evaluate.
  output_environment    Distinct name of the directory where the evaluator will do its work, necessary if many of this script are run parallel

optional arguments:
  -h, --help            show this help message and exit
  --lines {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19, 20}
                        The number of lines to generate, the default is 1
  --num_files           Specify the number of files to evaluate, helpful if theres heaps to reduce work load
```

## Script Overview

* **convertto3.py** - Used to convert all python programs to python3. This is to ensure consistency amongst the data.
* **evaluate.py** - Evaluates the results of a trained LSTM code generation model.
* **evaluator.py** - Provides several helper classes which the evaluate.py script uses in a polymorphic fashion to evaluate generated code * in different langauges.
* **generator.py** - Uses a provided trained code generation LSTM model to generated lines of code from a source sequence.
* **graphevaluation.py** - Generates graphs from evaluation statistics.
* **iteratortools.py** - Provides several helper utility functions for iteration over the dataset.
* **model_maker.py** - Provides a helper function for building a LSTM model.
* **programtokenizer.py** - Tokenizes and untokenizes Python and C code for training and generation.
* **stripcomments.py** - Removes all comments from code examples. Used so the LSTM learns just the code and not the comments.
* **train.py** - Trains an code generation LSTM model.


## Built With
* [Tensorflow](https://www.tensorflow.org)

## Authors
* [Nathan Cairns](https://github.com/Nathan-Cairns)
* [Buster Major](https://github.com/Buster-Darragh-Major)

## License
This project is licensed under the GPL-3.0 License - see the [License.md](https://github.com/Nathan-Cairns/CBT/blob/master/LICENSE) file for details.

## Acknowledgements
We would like to thank Jing Sun and Chenghao Cai for their guidance throughout this project.
