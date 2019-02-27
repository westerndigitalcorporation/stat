from services import toWindowsPath
from stat_makfile_project import StatMakefileProject
from visual_studio_builder import VisualStudioBuilder

class MakefileToVisualStudio(object):
    def __init__(self, makefile):
        self.__project = StatMakefileProject(makefile)
        self.__builder = VisualStudioBuilder(self.__project.projectName, makefile, self.__project.outputName + '.exe')

    def buildSolutionFile(self):
        self.__builder.createSolutionFile()

    def buildProjectFile(self):
        self.__addDefinitions()
        self.__addHeaderTreeToProject(self.__project.headers)
        self.__addSourceTreeToProject(self.__project.sources)
        self.__builder.createProjectFile()

    def __addDefinitions(self):
        for definition in self.__project.definitions:
            self.__builder.addDefinition(definition)

    def __addHeaderTreeToProject(self, fileTree):
        """
        @type fileTree: directory_tree_node.DirectoryTreeNode
        """
        for directory in fileTree.dirs:
            self.__builder.openHeaderFolder(directory)
            self.__addHeaderTreeToProject(fileTree[directory])
            self.__builder.closeHeaderFolder()
        for fileName in fileTree.files:
            filePath = toWindowsPath(fileTree[fileName])
            self.__builder.addHeaderFile(filePath)

    def __addSourceTreeToProject(self, fileTree):
        """
        @type fileTree: directory_tree_node.DirectoryTreeNode
        """
        for directory in fileTree.dirs:
            self.__builder.openSourceFolder(directory)
            self.__addSourceTreeToProject(fileTree[directory])
            self.__builder.closeSourceFolder()
        for fileName in fileTree.files:
            filePath = toWindowsPath(fileTree[fileName])
            self.__builder.addSourceFile(filePath)

