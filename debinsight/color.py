# ------------------------------------------------------------
# debinsight/color.py
#
# provides colorfull output
#
# This file is part of debinsight.
# See the LICENSE file for the software license.
# (C) Copyright 2019, Oliver Maurhart, dyle71@gmail.com
# ------------------------------------------------------------

"""This module generated colorized text outputs for the terminal."""

import colors

from .configuration import Configuration


def tool(t: str) -> str:
    """Color for tool names.

    :param t:   the text
    :return:    a colorized version of the text
    """
    if not Configuration().no_color:
        return colors.color(t, fg='cyan')
    return t


def package(t: str) -> str:
    """Color for package names.
    
    :param t:   the text
    :return:    a colorized version of the text
    """
    if not Configuration().no_color:
        return colors.color(t, fg='white', style='bold')
    return t


