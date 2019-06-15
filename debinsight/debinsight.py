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
from typing import Union

from .configuration import Configuration
from .database import Database
from . import color


async def _collect_package_status(pkg: str) -> None:
    """Collect the status information of a single package (and put it into the database).
    
    :param pkg:     name of the package.
    """
    print('Collecting status information for ' + color.package(pkg) + '...')
    proc = await asyncio.create_subprocess_exec(Configuration().dpkg_query, '--status', pkg,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if proc.returncode == 0:
        Database().packages[pkg] = {}
        for line in stdout.decode().splitlines():
            m = re.search(r'(^.*): (.*)', line)
            if m:
                key = m.group(1).lower()
                value = _expand_deb_query_value(key, m.group(2))
                Database().packages[pkg][key] = value
    else:
        print(color.error('Failed to collect status information for ') + color.package(pkg) + color.error('. o.O'))
        del Database().packages[pkg]


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
        for line in stdout.decode().splitlines():
            m = re.search(r'(^.*):.*', line)
            if m:
                pkg = m.group(1)
                print('Found ' + color.file(path) + ' in package ' + color.package(pkg))
                await _grab_package(pkg)


async def _detect_target(target: str) -> None:
    """Search for the given target name.
    This searches the local operating system if the given target
    is a package name or a file.

    :param target:  the target to search
    """
    if os.path.exists(target):
        await _detect_package_for_file(target)
    else:
        await _grab_package(target)


async def _examine_open_packages() -> None:
    """Collect information about all current open packages."""
    for pkg in Database().open:
        await _examine_package(pkg)


async def _examine_package(pkg: str) -> None:
    """Collect information about a single package.
    
    :param pkg:     the name of the package to collect information for.
    """
    await _collect_package_status(pkg)


def _expand_deb_query_value(key: str, value: str) -> Union[str, list]:
    """Expands a value gained from deb-query --status if necessary.
    
    Some keys like 'Debends' are a list of other packages, which
    might contain package information. For further ease of computation
    we break them into a list of tuples of necessary.
    
    :param key:     the key as gained by deb-query
    :param value:   the value of this key
    :return:
    """
    if key in ['replaces', 'depends', 'breaks', 'recommends', 'conflicts', 'suggests', 'pre-depends']:
        package_version_list = []
        for pkg in value.split(','):
            pkg = pkg.strip()
            m = re.match(r'(^.*).\((.*)\)', pkg)
            if m:
                package_version_list.append({'package': m.group(1), 'version': m.group(2)})
            else:
                package_version_list.append({'package': pkg})
        return package_version_list
    return value


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
    """Grab the given package if installed and add it then to the database.

    :param pkg:     the name of the package
    """
    if pkg in Database().packages:
        return
    
    print('Searching for ' + color.package(pkg) + '...')
    proc = await asyncio.create_subprocess_exec(Configuration().dpkg_query, '--status', pkg,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    await proc.communicate()
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
        
        while Database().open:
            await _examine_open_packages()
            
        if Configuration().json:
            with open(Configuration().json, 'wt') as f:
                f.write(Database().dump())

    except Exception as e:
        sys.stderr.write('Error: ' + str(e))
        sys.exit(1)
