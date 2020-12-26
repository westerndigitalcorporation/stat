#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

import os
from zipfile import ZipFile

import stat_attributes as attributes
from ide_writer import IdeWriter


WORKSPACE_PATH = "{basePath}/{name}"
SOURCE_INSIGHT_4 = "si4project.zip"
FILE_LIST_FILENAME = "{path}/si_filelist.txt"
SI_FILES_PREFIX = 'stat'


class SourceInsightWriter(IdeWriter):
    IDE = 'SourceInsight'

    def __init__(self, ide, contents, *args):
        super(SourceInsightWriter, self).__init__(contents, *args)
        self.__files = [self._contents.makefile]
        self.__workspacePath = \
            WORKSPACE_PATH.format(basePath=attributes.IDE_DIRECTORY, name=self._contents.name)

    def createRootToken(self):
        return None

    def createDirectoryToken(self, name, parentDirectoryToken):
        pass

    def addFile(self, filePath, parentDirectoryToken):
        self.__files.append(filePath)

    def write(self):
        if not os.path.isdir(self.__workspacePath):
            self.__createWorkspace()
            outputText = 'Source-Insight project "{path}" has been build.'
        else:
            outputText = 'Source-Insight file-list for project "{path}" has been rebuilt.'
        self.__writeProjectFileList()
        print(outputText.format(path=self.__workspacePath))

    def __createWorkspace(self):
        os.makedirs(self.__workspacePath)
        zipSource = os.path.join(attributes.TOOL_PATH, attributes.RESOURCES_DIRECTORY, SOURCE_INSIGHT_4)
        with ZipFile(zipSource, "r") as source:
            for member in source.filelist:
                member.filename = member.filename.replace(SI_FILES_PREFIX, self._contents.name)
                source.extract(member, self.__workspacePath)

    def __writeProjectFileList(self):
        fileName = FILE_LIST_FILENAME.format(path=self.__workspacePath)
        targetFile = open(fileName, 'w')
        targetFile.write('\n'.join(self.__files))
        targetFile.close()
