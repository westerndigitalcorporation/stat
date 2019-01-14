import os

import stat_attributes as attributes
from stat_configuration import StatConfiguration
from ide_writer import IdeXmlWriter, IdeCompositeWriter
from services import locateResource, toNativePath


class MsvsSolutionWriter(object):
    _TEMPLATE_FILENAME = 'vs_solution.tsln'
    _SOLUTION_FILENAME = "vs_{name}.sln"

    def __init__(self, contents, tools, projectGuid, projectFilePath):
        """
        :type contents: StatMakefileProject
        :type tools: MsvsTools
        """
        self.__contents = contents
        self.__tools = tools
        self.__projectFilePath = projectFilePath
        self.__projectGuid = projectGuid
        pass

    def write(self):
        fileContents = self.__readSolutionFileTemplate()
        fileContents = fileContents.format(
            format=self.__tools.solutionFormat, version=self.__tools.versionId, year=self.__tools.year,
            name=self.__contents.projectName, project_file=self.__projectFilePath, guid=self.__projectGuid)
        filename = self._SOLUTION_FILENAME.format(name=self.__contents.projectName)
        filePath = "./{0}/{1}".format(attributes.IDE_DIRECTORY, filename)
        _file = open(filePath, "w")
        _file.write(fileContents)
        _file.flush()
        _file.close()
        print('\nVisual-Studio solution "{0}" has been created successfully.'.format(os.path.abspath(filePath)))

    def __readSolutionFileTemplate(self):
        filePath = locateResource(self._TEMPLATE_FILENAME)
        _file = open(filePath)
        _template = _file.read()
        _file.close()
        return _template


class MsvsLegacyWriter(IdeXmlWriter):
    _PROJECT_GUID = '86FC28D1-F4DE-4209-B544-10B5415D0C20'
    _PROJECT_FILENAME = "vs_{0}.vcproj"

    def __init__(self, ideName, contents, tools):
        """
        :param ideName:
        :type contents: StatMakefileProject
        :type tools: MsvsTools
        """
        super(MsvsLegacyWriter, self).__init__(ideName, contents)
        self._filename = self._PROJECT_FILENAME.format(self._contents.projectName)
        self.__tools = tools
        self.__executable = os.path.join(
            "..", attributes.OUTPUT_DIRECTORY, "bin", "{0}.exe".format(self._contents.outputName)
        )
        root = self.__composeBodyBase()
        for component in self.__composeComponents():
            root.appendChild(component)

    def __composeComponents(self):
        self.__rootDirectoryTag = self.composeElement("Files")
        return (
            self.__composePlatforms(),
            self.composeElement("ToolFiles"),
            self.__composeConfigurations(),
            self.composeElement("References"),
            self.__rootDirectoryTag,
            self.composeElement("Globals")
        )

    def __composeConfigurations(self):
        commandLine = 'cd..&&"{0}" /S /NOLOGO /ERRORREPORT:NONE /F {1}'.format(
            self.__tools.nmakeFilePath, self._contents.makeFile)
        tool = self.composeElement(
            "Tool",
            Name="VCNMakeTool",
            BuildCommandLine=commandLine,
            ReBuildCommandLine=commandLine,
            CleanCommandLine=commandLine + " clean",
            Output=self.__executable,
            PreprocessorDefinitions="WIN32;_DEBUG;{0}".format(';'.join(self._contents.definitions)),
            IncludeSearchPath="./inc",
            ForcedIncludes="",
            AssemblySearchPath="",
            ForcedUsingAssemblies="",
            CompileAsManaged=""
        )
        configuration = self.composeElement(
            "Configuration", Name="Debug|Win32", OutputDirectory=".", IntermediateDirectory=".", ConfigurationType="0")
        configuration.appendChild(tool)
        configurations = self.composeElement("Configurations")
        configurations.appendChild(configuration)
        return configurations

    def __composePlatforms(self):
        platforms = self.composeElement("Platforms")
        platforms.appendChild(self.composeElement("Platform", Name="Win32"))
        return platforms

    def __composeBodyBase(self):
        body = self.composeElement(
            "VisualStudioProject",
            ProjectType="Visual C++",
            Version="{0:.2f}".format(self.__tools.versionId),
            Name=self._contents.projectName,
            ProjectGUID="{{{0}}}".format(self._PROJECT_GUID),
            Keyword="MakeFileProj",
            RootNamespace=self._contents.projectName
        )
        self._doc.appendChild(body)
        return body

    def createRootToken(self):
        return self.__rootDirectoryTag

    def createDirectoryToken(self, name, parentDirectoryToken):
        childNodes = parentDirectoryToken.childNodes if parentDirectoryToken.hasChildNodes() else ()
        for element in [node for node in childNodes if node.tagName == "Filter"]:
            if element.getAttribute("Name") == name:
                break
        else:
            element = self._doc.createElement("Filter")
            element.setAttribute("Name", name)
            parentDirectoryToken.appendChild(element)
        return element

    def addFile(self, filePath, parentDirectoryToken):
        element = self._doc.createElement("File")
        element.setAttribute("RelativePath", os.path.join("..", toNativePath(filePath)))
        parentDirectoryToken.appendChild(element)

    def write(self):
        super(MsvsLegacyWriter, self).write()
        solution = MsvsSolutionWriter(self._contents, self.__tools, self._PROJECT_GUID, self._filename)
        solution.write()


class MsvsWriter(IdeCompositeWriter):
    IDE = 'MSVS'
    writers = []

    def __init__(self, ideName, contents, *args):
        """
        :param ideName:
        :type contents: StatMakefileProject
        """
        super(MsvsWriter, self).__init__(ideName, contents, args)
        config = StatConfiguration()
        self._instances.append(MsvsLegacyWriter(ideName, contents, config.getMsvsTools()))