# ------------------------------------------------------------
# debinsight/database.py
#
# debinsight database
#
# This file is part of debinsight.
# See the LICENSE file for the software license.
# (C) Copyright 2019, Oliver Maurhart, dyle71@gmail.com
# ------------------------------------------------------------

"""This module holds the application wide database."""


class _Singleton(type):

    """Singleton class instance."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=_Singleton):

    """The debinsight program database."""

    def __init__(self):
        self.packages = {}

    def add_package(self, package: str) -> None:
        """Adds the package to the list of set of packages."""
        if package not in self.packages:
            self.packages[package] = None
