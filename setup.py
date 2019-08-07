#!/usr/bin/env python3

from setuptools import setup

setup(name='cbt',
      description='Generating code using machine learning',
      author='Buster & Nathan',
      install_requires=[
            'comment-filter',
            'tensorflow==2.0.0-beta1',
            'astunparse',
            'pylint ',
            'pycparser',
            'libclang-py3'
      ],
      dependency_links=[
            'https://github.com/codeauroraforum/comment-filter/tarball/master#egg=comment-filter-v1.0.0'
      ])
