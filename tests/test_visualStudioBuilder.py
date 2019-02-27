import os
from xml.dom import minidom

from services import config, vsTools
from testing_tools import FileBasedTestCase
from visual_studio_builder import VisualStudioBuilder, VisualStudioStrings


class TestVisualStudioBuilder(FileBasedTestCase):
    PROJECT_NAME = 'test_project'
    TEST_MAKFILE = 'test_makfile.mak'
    TEST_EXECUTABLE = 'test_executable.exe'
    SOLUTION_FILE = VisualStudioStrings.SOLUTION_FILENAME.format(name=PROJECT_NAME)
    PROJECT_FILE = VisualStudioStrings.PROJECT_FILENAME.format(name=PROJECT_NAME)
    FILE_LIST_EXAMPLE = {'..':
                             ([], {'..':
                                       ([], {'unity':
                                                 (['../../unity/unity.c'], {}),
                                             'lib':
                                                 ([], {'src':
                                                           (['../../lib/src/stat.c', '../../lib/src/stat_rng.c'], {})
                                                       }
                                                  )
                                             }
                                        )
                                   }
                              )
                         }

    def setUp(self):
        self.skipWindowsTest() # TODO: Fix these tests for Linux

    def tearDown(self):
        if os.path.isfile(self.SOLUTION_FILE):
            os.remove(self.SOLUTION_FILE)
        if os.path.isfile(self.PROJECT_FILE):
            os.remove(self.PROJECT_FILE)

    def test_createSolutionFile(self):
        builder = VisualStudioBuilder(self.PROJECT_NAME, self.TEST_MAKFILE, self.TEST_EXECUTABLE)
        builder.createSolutionFile()
        self.assertTrue(os.path.isfile(self.SOLUTION_FILE))
        expectedLines = VisualStudioStrings.SOLUTION_FILE_CONTENTS.format(solutionName=self.PROJECT_NAME,
                                                                     projectName=self.PROJECT_NAME)
        theFile = open(self.SOLUTION_FILE, 'r')
        for expected, line in zip(expectedLines.split('\n'), theFile):
            self.assertEqual(expected.strip(), line.strip())
        theFile.close()

    def test_createProjectFile(self):
        builder = VisualStudioBuilder(self.PROJECT_NAME, self.TEST_MAKFILE, self.TEST_EXECUTABLE)
        builder.createProjectFile()
        self.assertTrue(os.path.isfile(self.PROJECT_FILE))
        xmlDoc = minidom.parse(self.PROJECT_FILE)
        project = xmlDoc.getElementsByTagName('VisualStudioProject')[0]
        self.assertEqual(self.PROJECT_NAME, project.attributes['Name'].value)
        self.assertEqual(self.PROJECT_NAME, project.attributes['RootNamespace'].value)
        configurations = project.getElementsByTagName('Configurations')[0]
        configuration = configurations.getElementsByTagName('Configuration')[0]
        self.assertEqual(config.OUTPUT_DIRECTORY, configuration.attributes['OutputDirectory'].value)
        self.assertEqual(config.OUTPUT_DIRECTORY, configuration.attributes['IntermediateDirectory'].value)
        buildCommandLine = '"{0}" {1} {2}'.format(vsTools.getMakeToolLocation(), vsTools.NMAKE_ARGUMENTS, self.TEST_MAKFILE)
        cleanCommandLine = buildCommandLine + ' clean'
        executablePath = '/'.join([config.OUTPUT_DIRECTORY, config.OUTPUT_SUB_DIRECTORIES[2], self.TEST_EXECUTABLE])
        tool = configurations.getElementsByTagName('Tool')[0]
        self.assertEqual(buildCommandLine, tool.attributes['BuildCommandLine'].value)
        self.assertEqual(buildCommandLine, tool.attributes['ReBuildCommandLine'].value)
        self.assertEqual(cleanCommandLine, tool.attributes['CleanCommandLine'].value)
        self.assertEqual(executablePath, tool.attributes['Output'].value)
        self.assertEqual(";".join(VisualStudioStrings.DEFAULT_DEFINITIONS), tool.attributes['PreprocessorDefinitions'].value)
        self.assertEqual(config.MASTER_INCLUDE_PATH, tool.attributes['IncludeSearchPath'].value)
        files = project.getElementsByTagName('Files')
        self.assertEqual(1, len(files))
        fileFilters= files[0].getElementsByTagName('Filter')
        self.assertEqual(2, len(fileFilters))
        self.assertEqual('Header Files', fileFilters[0].attributes['Name'].value)
        self.assertEqual('Source Files', fileFilters[1].attributes['Name'].value)

    def test_addDefinition(self):
        userDefinitions = ['DEFINITION_A','DEFINITION_B=0','DEFINITION_C']
        builder = VisualStudioBuilder(self.PROJECT_NAME, self.TEST_MAKFILE, self.TEST_EXECUTABLE)
        for definition in userDefinitions:
            builder.addDefinition(definition)
        builder.createProjectFile()
        xmlDoc = minidom.parse(self.PROJECT_FILE)
        tool = xmlDoc.getElementsByTagName('Tool')[0]
        allDefinitions = VisualStudioStrings.DEFAULT_DEFINITIONS + userDefinitions
        self.assertEqual(";".join(allDefinitions), tool.attributes['PreprocessorDefinitions'].value)

    def test_addSourceFile(self):
        fileList = self.FILE_LIST_EXAMPLE
        builder = VisualStudioBuilder(self.PROJECT_NAME, self.TEST_MAKFILE, self.TEST_EXECUTABLE)
        for folder, files in self.__interpretFileList(fileList):
            if folder is not None:
                builder.openSourceFolder(folder)
                for aFile in files:
                    builder.addSourceFile(aFile)
            else:
                builder.closeSourceFolder()
        builder.createProjectFile()
        xmlDoc = minidom.parse(self.PROJECT_FILE)
        files = xmlDoc.getElementsByTagName('Files')[0]
        sourceFiles = [node for node in files.getElementsByTagName('Filter') if node.attributes['Name'].value == 'Source Files'][0]
        self.__verifyXmlTreeAgainstFileList(fileList, sourceFiles)

    def test_addHeaderFile(self):
        fileList = self.FILE_LIST_EXAMPLE
        builder = VisualStudioBuilder(self.PROJECT_NAME, self.TEST_MAKFILE, self.TEST_EXECUTABLE)
        for folder, files in self.__interpretFileList(fileList):
            if folder is not None:
                builder.openHeaderFolder(folder)
                for aFile in files:
                    builder.addHeaderFile(aFile)
            else:
                builder.closeHeaderFolder()
        builder.createProjectFile()
        xmlDoc = minidom.parse(self.PROJECT_FILE)
        files = xmlDoc.getElementsByTagName('Files')[0]
        headerFiles = [node for node in files.getElementsByTagName('Filter') if node.attributes['Name'].value == 'Header Files'][0]
        self.__verifyXmlTreeAgainstFileList(fileList, headerFiles)

    def __interpretFileList(self, fileList):
        entries = []
        for folderName in fileList:
            files, subFolders = fileList[folderName]
            entries.append((folderName, files))
            entries.extend(self.__interpretFileList(subFolders))
            entries.append((None, None))
        return entries

    def __verifyXmlTreeAgainstFileList(self, fileList, xmlTree):
        xmlFolders = [node for node in xmlTree.getElementsByTagName('Filter') if node in xmlTree.childNodes]
        self.assertEqual(len(list(fileList.keys())), len(xmlFolders))
        for folderName, xmlFolder in zip(fileList, xmlFolders):
            self.assertEqual(folderName, xmlFolder.attributes['Name'].value)
            files, subFolders = fileList[folderName]
            xmlFiles = [node.attributes['RelativePath'].value for node in xmlFolder.getElementsByTagName('File') if
                        node in xmlFolder.childNodes]
            self.assertSameItems(files, xmlFiles)
            xmlSubFolders = [node.attributes['Name'].value for node in xmlFolder.getElementsByTagName('Filter') if
                        node in xmlFolder.childNodes]
            self.assertSameItems(subFolders, xmlSubFolders)
            self.__verifyXmlTreeAgainstFileList(subFolders, xmlFolder)

