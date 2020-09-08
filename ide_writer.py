#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

# noinspection PyUnresolvedReferences
from xml.dom.minidom import Document

import stat_attributes as attributes
from services import toNativePath, mkdir, abstract_method, meta_class, FactoryByLegacy
from stat_makefile_project import StatMakefileProject


class IdeWriter(meta_class(FactoryByLegacy, object, uidAttribute='IDE')):

    def __new__(cls, ide, *args, **kwargs):
        _cls = cls.get(ide, cls)
        return object.__new__(_cls)

    def __init__(self, ide, contents, *args, **kwargs):
        """
        :param ideName:
        :type contents: StatMakefileProject
        """
        self._contents = contents

    @abstract_method
    def createRootToken(self): pass

    @abstract_method
    def createDirectoryToken(self, name, parentDirectoryToken): pass

    @abstract_method
    def addFile(self, filePath, parentDirectoryToken): pass

    @abstract_method
    def write(self): pass


class IdeCompositeWriter(IdeWriter):
    writers = []

    def __init__(self, ideName, contents, *args):
        """
        :param ideName:
        :type contents: StatMakefileProject
        """
        super(IdeCompositeWriter, self).__init__(ideName, contents, args)
        self._instances = [writer(ideName, contents, args) for writer in self.writers]

    def createRootToken(self):
        return [writer.createRootToken() for writer in self._instances]

    def createDirectoryToken(self, name, parentDirectoryToken):
        return [writer.createDirectoryToken(name, token)
                for writer, token in zip(self._instances, parentDirectoryToken)]

    def addFile(self, filePath, parentDirectoryToken):
        for writer, token in zip(self._instances, parentDirectoryToken):
            writer.addFile(filePath, token)

    def write(self):
        for writer in self._instances:
            writer.write()


class IdeXmlWriter(IdeWriter):

    def __init__(self, ideName, contents, *args):
        """
        :param ideName:
        :type contents: StatMakefileProject
        """
        super(IdeXmlWriter, self).__init__(ideName, contents, args)
        self._doc = Document()
        self._filename = None

    def composeElement(self, name, context=(), **xmlAttributes):
        element = self._doc.createElement(name)
        for attribute, value in xmlAttributes.items():
            element.setAttribute(attribute, value)
        if context and not isinstance(context, dict):
            element.appendChild(self._doc.createTextNode(context))
        else:
            for childName in context:
                childElement = self._doc.createElement(childName)
                childElement.appendChild(self._doc.createTextNode(context[childName]))
                element.appendChild(childElement)
        return element

    def write(self):
        _file = open("./{0}/{1}".format(attributes.IDE_DIRECTORY, self._filename), "w")
        self._doc.writexml(_file, indent="", addindent="\t", newl="\n", encoding="utf-8")
        _file.flush()
        _file.close()


class IdeWorkspaceWriter(object):

    def __init__(self, ideName, makeFile):
        self.__contents = StatMakefileProject(makeFile)
        self.__writer = IdeWriter(ideName, self.__contents)

    def write(self):
        mkdir(attributes.IDE_DIRECTORY, exist_ok=True)
        self.__addFileTree(self.__contents.tree, self.__writer.createRootToken())
        self.__writer.write()

    def __addFileTree(self, fileTree, parentToken):
        for fileName in fileTree.files:
            self.__writer.addFile(toNativePath(fileTree[fileName]), parentToken)
        for directory in fileTree.dirs:
            directoryTag = self.__writer.createDirectoryToken(directory, parentToken)
            self.__addFileTree(fileTree[directory], directoryTag)


class IdeProjectWriterException(Exception):
    """
    Custom exception for STAT IDE-Project Writer
    """


if __name__ == '__main__':
    pass
