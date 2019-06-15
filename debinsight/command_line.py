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
@click.option('--version', '-v', is_flag=True, help='Show version and exit.')
@click.option('--json', is_flag=True, help='Dump found information as json.')
@click.argument('target', required=False, nargs=-1)
def cli(no_color, version, json, target) -> None:

    """debinsight is collects package information by examining the reverse dependency
    of packages installed in the Debian (or Ubuntu and derivates) operating systems.

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

    uvloop.install()
    asyncio.run(debinsight.run())


def show_version() -> None:
    """Shows the program version."""
    from . import __version__
    print('debinsight V' + __version__)
