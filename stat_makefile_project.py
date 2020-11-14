#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

import os

import stat_attributes as attributes
from directory_tree_node import DirectoryTreeNode
from stat_makefile import StatMakefile
from itertools import chain


class StatMakefileProject(object):
    """
    Constructs a STAT project built based on STAT makefile
    """

    def __init__(self, fileName):
        self.__fileName = fileName
        self.__makefile = StatMakefile(fileName)
        self.__tree = None

    @property
    def makefile(self):
        return self.__fileName

    @property
    def name(self):
        return self.__makefile.name

    @property
    def outputName(self):
        return self.__makefile[StatMakefile.NAME]

    @property
    def tree(self):
        if self.__tree is None:
            self.__tree = self.__buildFileTree()
        return self.__tree

    @property
    def definitions(self):
        return self.__makefile[StatMakefile.DEFINES].split()

    def files(self):
        return chain(self.sources(), self.__headerFiles())

    def sources(self):
        for source in self.__makefile[StatMakefile.SOURCES].split():
            yield source

    def __getitem__(self, key):
        return self.__makefile[key]

    def __iter__(self):
        return iter(self.__makefile)

    def __buildFileTree(self):
        tree = DirectoryTreeNode()
        for _file in self.files():
            tree.addFile(_file)
        return tree

    def __headerFiles(self):
        files = []
        for _file in self.__makefile[StatMakefile.INTERFACES].split():
            filePath = os.path.join(attributes.DUMMIES_DIRECTORY, _file)
            files.append(os.path.basename(filePath))
            yield filePath
        for pathName in self.__makefile[StatMakefile.INCLUDES].split():
            for _file in os.listdir(pathName):
                if _file.endswith('.h') and _file not in files:
                    files.append(_file)
                    yield os.path.join(pathName, _file)
