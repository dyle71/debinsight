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


def dependency(t: str) -> str:
    """Color for dependencies of a package

    :param t:   the text
    :return:    a colorized version of the text
    """
    if not Configuration().no_color:
        return colors.color(t, fg='green')
    return t


def error(t: str) -> str:
    """Color for file names.

    :param t:   the text
    :return:    a colorized version of the text
    """
    if not Configuration().no_color:
        return colors.color(t, fg='red')
    return t


def file(t: str) -> str:
    """Color for file names.

    :param t:   the text
    :return:    a colorized version of the text
    """
    if not Configuration().no_color:
        return colors.color(t, fg='green')
    return t


def file_size(t: str) -> str:
    """Color for file sizes.

    :param t:   the text
    :return:    a colorized version of the text
    """
    if not Configuration().no_color:
        return colors.color(t, fg='magenta')
    return t


def package(t: str) -> str:
    """Color for package names.
    
    :param t:   the text
    :return:    a colorized version of the text
    """
    if not Configuration().no_color:
        return colors.color(t, fg='white', style='bold')
    return t


def rev_dependency(t: str) -> str:
    """Color for reverse dependencies of a package

    :param t:   the text
    :return:    a colorized version of the text
    """
    if not Configuration().no_color:
        return colors.color(t, fg='red', style='negative')
    return t


def tool(t: str) -> str:
    """Color for tool names.

    :param t:   the text
    :return:    a colorized version of the text
    """
    if not Configuration().no_color:
        return colors.color(t, fg='cyan')
    return t


def version(t: str) -> str:
    """Color for version string of packages.

    :param t:   the text
    :return:    a colorized version of the text
    """
    if not Configuration().no_color:
        return colors.color(t, fg='white', style='bold')
    return t
