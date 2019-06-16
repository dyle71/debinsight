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


def _add_dependencies(pkg: str) -> None:
    """Adds the dependencies of a package to the list of packages to examine.

    :param pkg:     name of the package to gather dependencies from
    """
    p = Database().packages.get(pkg, None)
    if p is None:
        return
    depends = p.get('depends', None)
    if depends:
        for d in depends:
            Database().add_package(d['package'])


def _add_reverse_dependencies(pkg: str) -> None:
    """Adds the reverse dependencies of a package to the list of packages to examine.

    :param pkg:     name of the package to gather reverse dependencies from
    """
    p = Database().packages.get(pkg, None)
    if p is None:
        return
    for rd in p.get('rdepend', []):
        Database().add_package(rd['package'])


async def _collect_package_files(pkg: str) -> None:
    """Collects the installed files of a package.

    :param pkg:     name of the package
    """
    if pkg not in Database().packages:
        return
    print(color.package(pkg) + ': collecting installed files...')
    proc = await asyncio.create_subprocess_exec(Configuration().dpkg_query, '--listfiles', pkg,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    if proc.returncode == 0:
        package_size = 0
        for line in stdout.decode().splitlines():
            if os.path.exists(line) and os.path.isfile(line) and not os.path.islink(line):
                file_size = os.path.getsize(line)
                Database().packages[pkg].setdefault('files', {})[line] = file_size
                package_size = package_size + file_size
        Database().packages[pkg]['installed'] = package_size


async def _collect_package_reverse_dependencies(pkg: str) -> None:
    """Collects the reverse dependencies of a package.

    :param pkg:     name of the package
    """
    if pkg not in Database().packages:
        return
    print(color.package(pkg) + ': collecting reverse dependencies...')
    proc = await asyncio.create_subprocess_exec(Configuration().apt_cache, 'rdepends', pkg,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    revdep = []
    if proc.returncode == 0:
        for line in stdout.decode().splitlines():
            m = re.search(r'^\s\s(\S*)$', line)
            if m and m.group(1) not in revdep:
                revdep.append(m.group(1))
    for rdep in revdep:
        entry = {'package': rdep, 'installed': False}
        Database().packages[pkg].setdefault('rdepend', []).append(entry)


async def _collect_package_status(pkg: str) -> None:
    """Collect the status information of a single package (and put it into the database).
    
    :param pkg:     name of the package.
    """
    print(color.package(pkg) + ': collectign status information...')
    proc = await asyncio.create_subprocess_exec(Configuration().dpkg_query, '--status', pkg,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    if proc.returncode == 0:
        Database().packages[pkg] = {}
        for line in stdout.decode().splitlines():
            m = re.search(r'(^.*): (.*)', line)
            if m:
                key = m.group(1).lower()
                value = _expand_deb_query_value(key, m.group(2))
                Database().packages[pkg][key] = value
    else:
        print(color.package(pkg) + color.dropping(' is not installed, dropping.'))
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
    await _collect_package_reverse_dependencies(pkg)
    await _collect_package_files(pkg)
    if Configuration().follow_depend:
        _add_dependencies(pkg)
    if Configuration().follow_rdepend:
        _add_reverse_dependencies(pkg)


def _expand_deb_query_value(key: str, value: str) -> Union[str, list]:
    """Expands a value gained from deb-query --status if necessary.
    
    Some keys like 'Depends' are a list of other packages, which
    might contain package version information too. For further
    ease of computation we break them into a list of tuples of necessary.
    
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


def _show_data() -> None:
    """Shows the gathered information to the user."""
    print(color.header('=== Collecting information done. ==='))
    for pkg in Database().packages:
        _show_package(pkg)
    if not Configuration().no_files:
        _show_sum_installed()


def _show_package(pkg: str) -> None:
    """Shows the gathered information to the user for a single package.

    :param pkg:     the package to show
    """
    p = Database().packages[pkg]
    print(color.package(pkg))
    print('\tInstalled version: ' + color.version(p['version']))
    if not Configuration().no_depend:
        _show_package_dependencies(p.get('depends', None))
    if not Configuration().no_rdepend:
        _show_package_reverse_dependencies(p.get('rdepend', None))
    if not Configuration().no_files:
        _show_package_files(p.get('files', None))
        _show_package_total_size(p.get('installed', None))


def _show_package_dependencies(dependencies: list) -> None:
    """Shows a dependency list to the user.

    :param dependencies:    the list of dependencies
    """
    if dependencies is None:
        return
    print('\tDependencies: ')
    for dep in dependencies:
        pkg_str = color.package(dep['package'])
        version_str = ''
        if 'version' in dep:
            version_str = color.dependency(' (' + dep['version'] + ')')
        print('\t\t' + pkg_str + version_str)


def _show_package_files(files: dict) -> None:
    """Shows files of a package to the user.

    :param files:       the files of a package
    """
    if files is None:
        return
    print('\tInstalled files: ')
    for f in files:
        file_str = color.file(f)
        filesize_str = ' ' + color.file_size('[' + str(files[f]) + ' Bytes]')
        print('\t\t' + file_str + filesize_str)


def _show_package_reverse_dependencies(dependencies: list) -> None:
    """Shows a reverse dependency list to the user.

    :param dependencies:    the list of dependencies
    """
    if dependencies is None:
        return
    print('\tReverse dependencies: ')
    for dep in dependencies:
        pkg_str = color.package(dep['package'])
        if dep['installed'] or not Configuration().drop_not_installed:
            if dep['installed']:
                installed_str = ' ' + color.installed('[installed]')
            else:
                installed_str = ' ' + color.not_installed('[not installed]')
            print('\t\t' + pkg_str + installed_str)


def _show_package_total_size(size: int) -> None:
    """Shows the total size of all installed files of a package to the user.

    :param size:    the total amount of bytes installed by the package
    """
    if size is None:
        return
    print('\tTotal amount of bytes of installed files: ' + color.file_size(str(size) + ' Bytes'))


def _show_sum_installed() -> None:
    """Shows the total sum of all installed files collected."""
    total_sum = 0
    for p in Database().packages:
        total_sum = total_sum + Database().packages[p].get('installed', 0)
    print('Total sum of bytes installed by these packages: ' + color.file_size(str(total_sum) + ' Bytes'))


async def run() -> None:
    """The debinsight algorithm."""
    try:
        _ensures_apt_cache_presence()
        _ensures_dpkg_query_presence()
        await _collect_targets()
        
        while Database().open:
            await _examine_open_packages()

        Database().fix_installed_rdependencies()
        _show_data()

        if Configuration().json:
            with open(Configuration().json, 'wt') as f:
                f.write(Database().dump())

    except Exception as e:
        sys.stderr.write('Error: ' + str(e))
        sys.exit(1)
