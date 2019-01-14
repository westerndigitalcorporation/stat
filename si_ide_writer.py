import os
from zipfile import ZipFile

import stat_attributes as attributes
from ide_writer import IdeWriter


WORKSPACE_PATH = "{basePath}/{name}.si4project"
SOURCE_INSIGHT_4 = "si4project.zip"
FILE_LIST_FILENAME = "{path}/si_filelist.txt"

class SourceInsightWriter(IdeWriter):
    IDE = 'SourceInsight'

    def __init__(self, ide, contents, *args):
        super(SourceInsightWriter, self).__init__(ide, contents, *args)
        self.__files = [self._contents.makeFile]
        self.__workspacePath = \
            WORKSPACE_PATH.format(basePath=attributes.IDE_DIRECTORY, name=self._contents.projectName)

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
            source.extractall(self.__workspacePath)

    def __writeProjectFileList(self):
        fileName = FILE_LIST_FILENAME.format(path=self.__workspacePath)
        targetFile = open(fileName, 'w')
        targetFile.write('\n'.join(self.__files))
        targetFile.close()
