# CBT (Code By Tensors)

This project aims to automatically generate code using LSTMs.

This repository contains scripts for preparing training data, training machine learning models, and generating code.

This is an University of Auckland Engineering Part Four Honours Project.
## Getting Started

1. Clone the repo and make sure you have ``python 3.0^`` installed!
2. Download the dataset [here](https://eth-sri.github.io/py150) under **Download Source Files** described as *An archive of source files used to generate the py150 Dataset*. 
3. Unzip *all* the contents of the downloaded file, and copy the directory ``py150_files`` from the unzipped contents to the ``data`` directory in your cloned repository. The contents of your data directory should look something like:
```
CBT
└── data
    ├── py150_files
    |   ├── data
    |   |   └──...
    |   ├── github_repos.txt
    |   ├── python50k_eval.txt
    |   ├── python100k_train.txt
    |   └── README.md
    └── .gitkeep

```
4. Run ``python setup.py install``

## Usage
### Generator
The generator can be used to generate a number of lines of code based on a seed sequence.

The generator requires the following arguments:
* The location of a model file (the latest checkpoint from training)
* The size of the vocabulary
* An input method (either from console or from file)

A full summary of arguments is provided below:
```
python3 scripts/generator.py --help

usage: CBT [-h] [--Cin CIN] [--Fin FIN] [--Fout FOUT]
           [--lines {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19, 20}]
           checkpoint_dir vocab_size

Automatically Generate Code

positional arguments:
  checkpoint_dir        The directory of the most recent training checkpoint
  vocab_size            The size of the vocabulary

optional arguments:
  -h, --help            show this help message and exit
  --Cin CIN             Provide input via the console
  --Fin FIN             Specify a python file to take as input
  --Fout FOUT           Specify a file to output to
  --lines {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19, 20}
                        The number of lines to generate, the default is 1
```

## Built With
* [Tensorflow](https://www.tensorflow.org)

## Authors
* [Nathan Cairns](https://github.com/Nathan-Cairns)
* [Buster Major](https://github.com/Buster-Darragh-Major)

## License
This project is licensed under the GPL-3.0 License - see the [License.md](https://github.com/Nathan-Cairns/CBT/blob/master/LICENSE) file for details.

## Acknowledgements
We would like to thank Jing Sun and Chenghao Cai for their guidance throughout this project.
