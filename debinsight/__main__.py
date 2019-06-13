#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------
# debinsight/__main__.py
#
# debinsight package start
#
# This file is part of debinsight.
# See the LICENSE file for the software license.
# (C) Copyright 2019, Oliver Maurhart, dyle71@gmail.com
# ------------------------------------------------------------

"""This is the debinsight package start script."""

import sys

from . import command_line


def main() -> None:
    """debinsight main startup."""
    try:
        command_line.cli(prog_name='debinsight')
    except Exception as e:
        sys.exit(1)


if __name__ == '__main__':
    main()

