#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------
# debinsight/debinsight.py
#
# debinsight algorithm
#
# This file is part of debinsight.
# See the LICENSE file for the software license.
# (C) Copyright 2019, Oliver Maurhart, dyle71@gmail.com
# ------------------------------------------------------------

"""Within this module resides the debinsight algorithm."""

import asyncio
import os.path
import sys

from .configuration import Configuration
from . import color


async def _collect_targets() -> None:
    """Collect all targets to inspect."""
    tasks = []
    for target in Configuration().targets:
        tasks.append(asyncio.create_task(_detect_target(target)))
    await asyncio.wait(tasks)


def _detect_package_for_file(path: str) -> None:
    """Detect the package which installed a certain file and if so add the package to insight.

    :param path:        path to file
    """
    path = os.path.abspath(path)
    print('==DBG==: path: ' + str(path))


async def _detect_target(target: str) -> None:
    """Search for the given target name.
    This searches the local operating system if the given target
    is a package name of a file.

    :param target:  the target to search
    """
    print('Searching for ' + color.package(target) + '...')
    if os.path.exists(target):
        _detect_package_for_file(target)
    else:
        _grab_package(target)


def _ensures_apt_cache_presence() -> None:
    """Asserts that apt-cache is found on the system."""
    if Configuration().apt_cache is None:
        sys.stderr.write('apt-cache not found on the system.\n')
        sys.stderr.write('Is this a Debian (or Debian derivate) system?\n')
        sys.exit(1)
    print('Found apt-cache: ' + color.tool(Configuration().apt_cache))


def _ensures_dpkg_query_presence() -> None:
    """Asserts that dpkg-query is found on the system."""
    if Configuration().dpkg_query is None:
        sys.stderr.write('dpkg-query not found on the system.\n')
        sys.stderr.write('Is this a Debian (or Debian derivate) system?\n')
        sys.exit(1)
    print('Found dpkg-query: ' + color.tool(Configuration().dpkg_query))


def _grab_package(pkg: str) -> None:
    """Grab the given package if installed.

    :param pkg:     the name of the package
    """
    pass


async def run() -> None:
    """The debinsight algorithm."""
    try:
        _ensures_apt_cache_presence()
        _ensures_dpkg_query_presence()
        await _collect_targets()
    except Exception as e:
        sys.stderr.write('Error: ' + str(e))
        sys.exit(1)
