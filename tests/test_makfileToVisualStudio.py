import os
from xml.dom import minidom

from services import toWindowsPath
from makefile_visual_studio import MakefileToVisualStudio
from stat_makfile_project import StatMakefileProject
from testing_tools import FileBasedTestCase
from visual_studio_builder import VisualStudioStrings

CUT = 'makefile_visual_studio'
TEST_MAKEFILE = 'simplified_example.mak'

class TestMakefileToVisualStudio(FileBasedTestCase):

    def setUp(self):
        self._project = StatMakefileProject(TEST_MAKEFILE)
        self._solutionFilename = VisualStudioStrings.SOLUTION_FILENAME.format(name=self._project.projectName)
        self._projectFilename = VisualStudioStrings.PROJECT_FILENAME.format(name=self._project.projectName)

    def tearDown(self):
        if os.path.isfile(self._solutionFilename):
            os.remove(self._solutionFilename)
        if os.path.isfile(self._projectFilename):
            os.remove(self._projectFilename)

    def test__init__basic(self):
        spyVisualStudioBuilder = self.patchWithSpy(CUT, 'VisualStudioBuilder')
        MakefileToVisualStudio(TEST_MAKEFILE)
        self.assertEqual(1, len(spyVisualStudioBuilder.instances))
        arguments = spyVisualStudioBuilder.instances[0].getArguments('__init__', callId=0)
        expected =(self._project.projectName, TEST_MAKEFILE, self._project.outputName + '.exe')
        self.assertEqual(expected,arguments.args)

    def test_buildSolutionFile(self):
        builder = MakefileToVisualStudio(TEST_MAKEFILE)
        builder.buildSolutionFile()
        self.assertTrue(os.path.isfile(self._solutionFilename))

    def test_buildProjectFile(self):
        self.skipWindowsTest() # TODO: Fix these tests for Linux
        builder = MakefileToVisualStudio(TEST_MAKEFILE)
        builder.buildProjectFile()
        self.assertTrue(os.path.isfile(self._projectFilename))

        xmlDoc = minidom.parse(self._projectFilename)
        tool = xmlDoc.getElementsByTagName('Tool')[0]
        definitions = tool.attributes['PreprocessorDefinitions'].value.split(';')
        for definition in self._project.definitions:
            self.assertIn(definition, definitions)
        files = xmlDoc.getElementsByTagName('Files')[0]
        headerFiles, sourceFiles = self.__getChildElementsByTagName(files, 'Filter')
        self.__verifyFiles(self._project.headers, headerFiles)
        self.__verifyFiles(self._project.sources, sourceFiles)

    def __verifyFiles(self, makFileNode, projectFileNode):
        """
        @type makFileNode: directory_tree_node.DirectoryTreeNode
        @type projectFileNode:  minidom.Element
        """
        makfileDirs = makFileNode.dirs
        makfileFiles = [toWindowsPath(makFileNode[fileName]) for fileName in makFileNode.files]
        projectFileDirNodes = list(self.__getChildElementsByTagName(projectFileNode, 'Filter'))
        projectFileDirs = [node.attributes['Name'].value for node in projectFileDirNodes]
        projectFileFiles = [node.attributes['RelativePath'].value for node in self.__getChildElementsByTagName(projectFileNode, 'File')]
        self.assertSameItems(makfileDirs, projectFileDirs)
        self.assertEqual(makfileFiles, projectFileFiles)
        for directoryName, projectFileDirectory in zip(makfileDirs, projectFileDirNodes):
            self.__verifyFiles(makFileNode[directoryName], projectFileDirectory)

    @staticmethod
    def __getChildElementsByTagName(xmlNode, tagName):
        return (node for node in xmlNode.getElementsByTagName(tagName) if node in xmlNode.childNodes)

