#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

import os

import stat_attributes as attributes
from build_tools_crawler import BuildToolsCrawler
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
            name=self.__contents.name, project_file=self.__projectFilePath, guid=self.__projectGuid)
        filename = self._SOLUTION_FILENAME.format(name=self.__contents.name)
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
        self._filename = self._PROJECT_FILENAME.format(self._contents.name)
        self.__tools = tools
        output = os.path.join("..", attributes.OUTPUT_DIRECTORY, self._contents.outputName,
                              "msvs_{0}".format(self._contents.name))
        self.__includePath = os.path.join(output, "inc")
        self.__executable = os.path.join(output, "bin", "{0}.exe".format(self._contents.outputName))
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
        commandLine = 'cd..&&"{0}" /S /NOLOGO /ERRORREPORT:NONE /F {1} PRIVATE_NAME="msvs_{2}"'.format(
            self.__tools.nmakeFilePath, self._contents.makefile, self._contents.name)
        tool = self.composeElement(
            "Tool",
            Name="VCNMakeTool",
            BuildCommandLine=commandLine + " build",
            ReBuildCommandLine=commandLine + " rebuild",
            CleanCommandLine=commandLine + " clean",
            Output=self.__executable,
            PreprocessorDefinitions="WIN32;_DEBUG;{0}".format(';'.join(self._contents.definitions)),
            IncludeSearchPath=self.__includePath,
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
            Name=self._contents.name,
            ProjectGUID="{{{0}}}".format(self._PROJECT_GUID),
            Keyword="MakeFileProj",
            RootNamespace=self._contents.name
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


class Msvs2010ProjectWriter(IdeXmlWriter):
    _PROJECT_GUID = '86FC28D1-F4DE-4209-B544-10B5415D0C20'
    _PROJECT_FILENAME = "vs_{0}.vcxproj"

    def __init__(self, ideName, contents, tools):
        """
        :param ideName:
        :type contents: StatMakefileProject
        :type tools: MsvsTools
        """
        super(Msvs2010ProjectWriter, self).__init__(ideName, contents)
        self._filename = self._PROJECT_FILENAME.format(self._contents.name)
        self.__tools = tools
        output = os.path.join("..", attributes.OUTPUT_DIRECTORY, self._contents.outputName,
                              "msvs_{0}".format(self._contents.name))
        self.__executable = os.path.join(output, "bin", "{0}.exe".format(self._contents.outputName))
        self.__includePath = os.path.join(output, "inc")
        self.__sources = self.composeElement("ItemGroup")
        self.__headers = self.composeElement("ItemGroup")
        body = self.__composeBodyBase()
        for element in self.__composeBodyElements():
            body.appendChild(element)

    def __composeBodyElements(self):
        return [
            self.___composeConfigGroup(),
            self.composeElement("PropertyGroup",
                                context=dict(ProjectName=self._contents.name,
                                             ProjectGuid="{{{0}}}".format(self._PROJECT_GUID),
                                             Keyword="MakeFileProj",
                                             RootNamespace=self._contents.name),
                                Label="Globals"),
            self.composeElement("Import", Project=r"$(VCTargetsPath)\Microsoft.Cpp.Default.props"),
            self.composeElement("PropertyGroup",
                                context=dict(ConfigurationType="Makefile", ),
                                Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'",
                                Label="Configuration"),
            self.composeElement("Import", Project=r"$(VCTargetsPath)\Microsoft.Cpp.props"),
            self.composeElement("ImportGroup", Label="ExtensionSettings"),
            self.__composePropertySheets(),
            self.composeElement("PropertyGroup", Label="UserMacros"),
            self.composeElement("PropertyGroup",
                                context=dict(_ProjectFileVersion="{0:.2f}".format(self.__tools.versionId))),
            self.__composeCommandLineGroup(),
            self.composeElement("ItemDefinitionGroup"),
            self.__sources,
            self.__headers,
            self.composeElement("Import", Project=r"$(VCTargetsPath)\Microsoft.Cpp.targets"),
            self.composeElement("ImportGroup", Label="ExtensionTargets"),
        ]

    def __composeCommandLineGroup(self):
        commandLine = 'cd..&&"{0}" /S /NOLOGO /ERRORREPORT:NONE /F {1} PRIVATE_NAME="msvs_{2}"'.format(
            self.__tools.nmakeFilePath, self._contents.makefile, self._contents.name)
        includePath = "{0};$(NMakeIncludeSearchPath)".format(self.__includePath)
        definitions = "WIN32;_DEBUG;{0};$(NMakePreprocessorDefinitions)".format(';'.join(self._contents.definitions))
        commandLineGroup = self.composeElement("PropertyGroup",
                                               dict(OutDir=".",
                                                    IntDir=".",
                                                    NMakeBuildCommandLine=commandLine + " build",
                                                    NMakeReBuildCommandLine=commandLine + " rebuild",
                                                    NMakeCleanCommandLine=commandLine + " clean",
                                                    NMakeOutput=self.__executable,
                                                    NMakePreprocessorDefinitions=definitions,
                                                    NMakeIncludeSearchPath=includePath
                                                    ),
                                               Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'")
        return commandLineGroup

    def __composePropertySheets(self):
        propertySheets = self.composeElement("ImportGroup",
                                             Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'",
                                             Label="PropertySheets")
        propertySheets.appendChild(self.composeElement(
            "Import",
            Project=r"$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props",
            Condition=r"exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')",
            Label="LocalAppDataPlatform"))
        return propertySheets

    def ___composeConfigGroup(self):
        configGroup = self.composeElement("ItemGroup", Label='ProjectConfigurations')
        projectConfig = self.composeElement("ProjectConfiguration",
                                            context=dict(Configuration="Debug", Platform="Win32"),
                                            Include="Debug|Win32")
        configGroup.appendChild(projectConfig)
        return configGroup

    def __composeBodyBase(self):
        body = self.composeElement(
            "Project", DefaultTargets="Build",
            ToolsVersion="{0:.2f}".format(self.__tools.versionId),
            xmlns="http://schemas.microsoft.com/developer/msbuild/2003"
        )
        self._doc.appendChild(body)
        return body

    def createRootToken(self):
        pass

    def createDirectoryToken(self, name, parentDirectoryToken):
        pass

    def addFile(self, filePath, parentDirectoryToken):
        if os.path.splitext(filePath)[1] == ".c":
            self.__sources.appendChild(self.composeElement("ClCompile", Include=os.path.join("..", filePath)))
        if os.path.splitext(filePath)[1] == ".h":
            self.__headers.appendChild(self.composeElement("ClInclude", Include=os.path.join("..", filePath)))

    def write(self):
        super(Msvs2010ProjectWriter, self).write()
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
        tools = BuildToolsCrawler().retrieve()
        writer = Msvs2010ProjectWriter if tools.year >= 2010 else MsvsLegacyWriter
        self._instances.append(writer(ideName, contents, tools))
