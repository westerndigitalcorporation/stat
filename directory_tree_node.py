#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

import os


class DirectoryTreeNode(object):
    def __init__(self):
        self.__files = []
        self.__dirs = []
        self.__items = {}

    def __getitem__(self, item):
        return self.__items[item]

    def __contains__(self, item):
        return item in self.__items

    @property
    def files(self):
        return self.__files

    @property
    def dirs(self):
        return self.__dirs

    def addFile(self, filePath):
        if not os.path.isfile(filePath):
            raise DirectoryTreeNodeException("The file '{filePath}' doesn't exist!".format(filePath=filePath))
        if filePath.startswith('./'):
            filePath = filePath[2:]
        leafNode = self.__retrieveLeafNode(os.path.dirname(filePath))
        leafNode.__addFile(filePath)

    def getAllFilePaths(self):
        for node in self.__getAllNodes():
            for fileName in node.files:
                yield node[fileName]

    def __retrieveLeafNode(self, dirPath):
        treeNode = self
        pathTail = dirPath
        while pathTail != '':
            pathRoot, pathTail = splitByRoot(pathTail)
            treeNode = treeNode.__retrieveNextTreeNode(pathRoot)
        return treeNode

    def __retrieveNextTreeNode(self, dirName):
        """
        @rtype: DirectoryTreeNode
        """
        if dirName not in self.__dirs:
            self.__dirs.append(dirName)
            self.__items[dirName] = DirectoryTreeNode()
        return self.__items[dirName]

    def __addFile(self, filePath):
        fileName = os.path.basename(filePath)
        self.__files.append(fileName)
        self.__items[fileName] = filePath

    def __getAllNodes(self):
        nodes = [self]
        while not len(nodes) == 0:
            for node in nodes:
                yield node
            nodes = [node[dirName] for node in nodes for dirName in node.dirs]


class DirectoryTreeNodeException(Exception):
    """
    Custom exception for Directory-Tree-Node failures
    """


def splitByRoot(path):
    pos = 0
    while pos < len(path) and path[pos] not in '/\\':
        pos += 1
    rootDir = path[:pos] or path[:pos + 1]
    pathTail = path[pos + 1:]
    return rootDir, pathTail
