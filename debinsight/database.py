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

import json


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
            
    def dump(self) -> str:
        """Dumps the package content to string as JSON.
        
        :return:    a json string of the current DB.
        """
        return json.dumps(self.packages, ensure_ascii=True)

    def fix_installed_rdependencies(self):
        """Fix installed entry for reverse dependencies.
        
        Within a list of installed reverse dependencies, we cannot
        at the first glance detect, if the reverse dependent package
        is installed or not. Within this step we fix this.
        """
        for p in self.packages:
            for rdep in self.packages[p].get('rdepend', {}):
                rdep['installed'] = rdep['package'] in self.packages

    @property
    def open(self) -> list:
        """Gets the list of unresolved, open packages still not yet examined.
        
        :return:    list of open (unexamined) packages.
        """
        return [p for p in self.packages if self.packages[p] is None]
