#!/usr/bin/env python3

from setuptools import setup
import subprocess
import os

setup(name='cbt',
      description='Generating code using machine learning',
      author='Buster & Nathan',
      install_requires=[
            'comment-filter',
            'tensorflow==2.9.3',
            'astunparse',
            'pylint ',
            'pycparser',
            'libclang-py3',
            'python-Levenshtein',
            'plotly',
            'pandas',
            'matplotlib'
      ],
      dependency_links=[
            'https://github.com/codeauroraforum/comment-filter/tarball/master#egg=comment-filter-v1.0.0'
      ])