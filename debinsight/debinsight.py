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
import re
import sys

from .configuration import Configuration
from .database import Database
from . import color


async def _collect_targets() -> None:
    """Collect all targets to inspect."""
    tasks = []
    for target in Configuration().targets:
        tasks.append(asyncio.create_task(_detect_target(target)))
    await asyncio.wait(tasks)


async def _detect_package_for_file(path: str) -> None:
    """Detect the package which installed a certain file and if so add the package to insight.

    :param path:        path to file
    """
    path = os.path.abspath(path)
    print('Searching for ' + color.file(path) + '...')
    proc = await asyncio.create_subprocess_exec(Configuration().dpkg_query, '--search', path,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if proc.returncode == 0:
        for l in stdout.decode().splitlines():
            m = re.search(r'(^.*):.*', l)
            if m:
                pkg = m.group(1)
                print('Found ' + color.file(path) + ' in package ' + color.package(pkg))
                await _grab_package(pkg)


async def _detect_target(target: str) -> None:
    """Search for the given target name.
    This searches the local operating system if the given target
    is a package name of a file.

    :param target:  the target to search
    """
    if os.path.exists(target):
        await _detect_package_for_file(target)
    else:
        await _grab_package(target)


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


async def _grab_package(pkg: str) -> None:
    """Grab the given package if installed.

    :param pkg:     the name of the package
    """
    print('Searching for ' + color.package(pkg) + '...')
    proc = await asyncio.create_subprocess_exec(Configuration().dpkg_query, '--status', pkg,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        print(color.error('Failed to locate package ') + color.package(pkg) + color.error(' on the system.'))
    else:
        Database().add_package(pkg)
        print('Package ' + color.package(pkg) + ' found.')


async def run() -> None:
    """The debinsight algorithm."""
    try:
        _ensures_apt_cache_presence()
        _ensures_dpkg_query_presence()
        await _collect_targets()
    except Exception as e:
        sys.stderr.write('Error: ' + str(e))
        sys.exit(1)
