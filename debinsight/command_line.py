# ------------------------------------------------------------
# debinsight/command_line.py
#
# handle command line stuff and arguments
#
# This file is part of debinsight.
# See the LICENSE file for the software license.
# (C) Copyright 2019, Oliver Maurhart, dyle71@gmail.com
# ------------------------------------------------------------

"""This module provides all command line stuff and figures."""

import asyncio
import click
import uvloop
import sys

from .configuration import Configuration
from . import debinsight


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option('--no-color', is_flag=True, help='Turn off color output.')
@click.option('--no-depend', is_flag=True, help='Turn off output for dependencies.')
@click.option('--no-rdepend', is_flag=True, help='Turn off output for reverse dependencies.')
@click.option('--no-files', is_flag=True, help='Turn off list of files.')
@click.option('--version', '-v', is_flag=True, help='Show version and exit.')
@click.option('--json', type=click.Path(), help='Dump found information as json into a file.')
@click.option('--follow-depend', is_flag=True, help='Follow dependency graph (use with caution).')
@click.option('--follow-rdepend', is_flag=True, help='Follow reverse dependency graph (use with caution).')
@click.option('--drop-not-installed', is_flag=True, help='Do not list not installed packages.')
@click.argument('target', required=False, nargs=-1)
def cli(no_color=False,
        no_depend=False,
        no_rdepend=False,
        no_files=False,
        version=False,
        json=None,
        follow_depend=False,
        follow_rdepend=False,
        drop_not_installed=False,
        target=None) -> None:

    """debinsight collects package information by examining the dependency
    and reverse dependencies of packages installed in the Debian
    (or Ubuntu and derivates) operating systems. On default, it prints the
    current stats of a package and all files the package installs.

    TARGET can be either a package name or a file on the local system.

    \b
    E.g.:
        TARGET = openssl ............ start with the openssl package installed.
        TARGET = /usr/bin/openssl ... start with the package containing which had
                                      installed the file "/usr/bin/openssl".
    """

    if version:
        show_version()
        sys.exit(0)

    if len(target) == 0:
        raise click.UsageError('This tool needs at least one TARGET to operate.')

    config = Configuration()
    config.targets = target
    config.json = json
    config.no_color = no_color
    config.no_depend = no_depend
    config.no_rdepend = no_rdepend
    config.no_files = no_files
    config.follow_depend = follow_depend
    config.follow_rdepend = follow_rdepend
    config.drop_not_installed = drop_not_installed

    uvloop.install()
    asyncio.run(debinsight.run())


def show_version() -> None:
    """Shows the program version."""
    from . import __version__
    print('debinsight V' + __version__)
