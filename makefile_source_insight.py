# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

import os

from stat_makfile_project import StatMakefileProject
from services import StatConfiguration
import zipfile

class MakefileToSourceInsight(object):
    PROJECT_FOLDER_NAME = "{basePath}/{name}.si4project"
    FILE_LIST_FILENAME = "{path}/si_filelist.txt"
    SOURCE_INSIGHT_4_FILENAME = "si4project.zip"


    def __init__(self, makfile):
        self.__makfile = makfile
        self.__project = StatMakefileProject(makfile)

    def __createSourceInsightFileList(self, folder):
        fileName = self.FILE_LIST_FILENAME.format(path=folder)
        self.__writeSourceInsightFileList(fileName)

    def __writeSourceInsightFileList(self, fileName):
        targetFile = open(fileName, 'w')
        targetFile.write(self.__makfile + "\n")
        targetFile.writelines([file + "\n" for file in self.__project.files()])
        targetFile.close()

    def buildProject(self):
        config = StatConfiguration()
        folder = self.PROJECT_FOLDER_NAME.format(basePath=config.OUTPUT_DIRECTORY, name=self.__project.projectName)
        if not os.path.isdir(folder):
            os.makedirs(folder)
            zipSource = os.path.join(config.getToolDirectory(), config.RESOURCES_DIRECTORY, self.SOURCE_INSIGHT_4_FILENAME)
            with zipfile.ZipFile(zipSource, "r") as source:
                source.extractall(folder)
            outputText = 'Source-Insight project "{path}" has been build.'
        else:
            outputText = 'Source-Insight file-list for project "{path}" has been rebuilt.'
        self.__createSourceInsightFileList(folder)
        print(outputText.format(path=folder))