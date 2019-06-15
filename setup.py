#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------
# setup.py
#
# debinsight setuptools main file
#
# This file is part of debinsight.
# See the LICENSE file for the software license.
# (C) Copyright 2019, Oliver Maurhart, dyle71@gmail.com
# ------------------------------------------------------------

from setuptools import setup

import debinsight

setup(
    name='debinsight',
    version=debinsight.__version__,
    description='Reverse dependency package information of installed packages',
    long_description='This tool gathers information of installed packages '
                     'on Debian or Ubuntu operating systems.',
    author='Oliver Maurhart',
    author_email='dyle71@gmail.com',
    maintainer='Oliver Maurhart',
    maintainer_email='dyle71@gmail.com',
    url='https://www.github.com/dyle71/debinsight',
    license='GPL-3',

    # sources
    packages=['debinsight'],
    py_modules=[],
    scripts=['bin/debinsight'],

    # data
    package_data={'': ['*.txt']},
    include_package_data=False,
)
