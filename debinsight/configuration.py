# ------------------------------------------------------------
# debinsight/configuration.py
#
# debinsight configuration stuff
#
# This file is part of debinsight.
# See the LICENSE file for the software license.
# (C) Copyright 2019, Oliver Maurhart, dyle71@gmail.com
# ------------------------------------------------------------

"""This module holds the application wide configuration."""

import shutil


class _Singleton(type):

    """Singleton class instance."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Configuration(metaclass=_Singleton):

    """The debinsight program configuration."""

    def __init__(self):
        self.json = False
        self.no_color = False
        self.targets = None
        self._apt_cache = None
        self._dpkg_query = None

    @property
    def apt_cache(self) -> str:
        """Return the path to the apt-cache executable."""
        if self._apt_cache is None:
            self._apt_cache = shutil.which(cmd='apt-cache')
        return self._apt_cache

    @property
    def dpkg_query(self) -> str:
        """Return the path to the dpkg-query executable."""
        if self._dpkg_query is None:
            self._dpkg_query = shutil.which(cmd='dpkg-query')
        return self._dpkg_query
