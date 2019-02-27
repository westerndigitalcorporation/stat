from services import config, vsTools


class VisualStudioBuilder(object):
    def __init__(self, projectName, makfile, executable):
        self.__name = projectName
        self.__makfile = makfile
        self.__executable = executable
        self.__projectFile = None
        self.__sourceFiles = []
        self.__headerFiles = []
        self.__definitions = VisualStudioStrings.DEFAULT_DEFINITIONS[:]

    def createSolutionFile(self):
        fileName = VisualStudioStrings.SOLUTION_FILENAME.format(name=self.__name)
        solutionFile = open(fileName, 'w')
        solutionFile.write(VisualStudioStrings.SOLUTION_FILE_CONTENTS.format(solutionName=self.__name, projectName=self.__name))
        solutionFile.close()
        print('Solution "{fileName}" has been built'.format(fileName=fileName))

    def createProjectFile(self):
        fileName = VisualStudioStrings.PROJECT_FILENAME.format(name=self.__name)
        buildCommandLine = '&quot;{0}&quot; {1} {2}'.format(vsTools.getMakeToolLocation(), vsTools.NMAKE_ARGUMENTS, self.__makfile)
        cleanCommandLine = buildCommandLine + ' clean'
        executablePath = '/'.join([config.OUTPUT_DIRECTORY, config.OUTPUT_SUB_DIRECTORIES[2], self.__executable])
        self.__projectFile = open(fileName, 'w')
        self.__write(VisualStudioStrings.PROJECT_FILE_OPENING.format(
            projectName=self.__name, intermediateDirectory=config.OUTPUT_DIRECTORY,
            buildCommandLine=buildCommandLine, rebuildCommandLine=buildCommandLine, cleanCommandLine=cleanCommandLine,
            outputExecutable=executablePath, definitions=";".join(self.__definitions), includePaths=config.MASTER_INCLUDE_PATH))
        self.__write(VisualStudioStrings.HEADER_SECTION_OPENING)
        self.__write('\n'.join(self.__headerFiles))
        self.__write(VisualStudioStrings.HEADER_SECTION_CLOSING)
        self.__write(VisualStudioStrings.SOURCE_SECTION_OPENING)
        self.__write('\n'.join(self.__sourceFiles))
        self.__write(VisualStudioStrings.SOURCE_SECTION_CLOSING)
        self.__write(VisualStudioStrings.PROJECT_FILE_CLOSING)
        self.__projectFile.close()
        print('Project "{fileName}" has been built'.format(fileName=fileName))

    def addDefinition(self,definition):
        self.__definitions.append(definition)

    def openSourceFolder(self, name):
        self.__sourceFiles.append(VisualStudioStrings.DIRECTORY_OPENING.format(name=name))

    def closeSourceFolder(self):
        self.__sourceFiles.append(VisualStudioStrings.DIRECTORY_CLOSING)

    def openHeaderFolder(self, name):
        self.__headerFiles.append(VisualStudioStrings.DIRECTORY_OPENING.format(name=name))

    def closeHeaderFolder(self):
        self.__headerFiles.append(VisualStudioStrings.DIRECTORY_CLOSING)

    def addSourceFile(self, path):
        self.__sourceFiles.append(VisualStudioStrings.FILE_NODE.format(filePath=path))

    def addHeaderFile(self, path):
        self.__headerFiles.append(VisualStudioStrings.FILE_NODE.format(filePath=path))

    def __write(self, line):
        self.__projectFile.write(line + '\n')

class VisualStudioBuilderException(Exception):
    """
    Exception for Visual-Studio Builder
    """

class VisualStudioStrings(object):
    _SOLUTION_G_UID = '{{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}}'
    _PROJECT_G_UID = '{{DDA5FFAB-D686-495D-8A10-39EC29788B15}}'

    SOLUTION_FILENAME = "vs_{name}.sln"
    PROJECT_FILENAME = "vs_{name}.vcproj"

    #arguments: solutionName, projectName
    SOLUTION_FILE_CONTENTS = r'''Microsoft Visual Studio Solution File, Format Version 10.00
# Visual Studio 2008
Project("{solutionGUid}") = "{{solutionName}}", "vs_{{projectName}}.vcproj", "{projectGUid}"
EndProject
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|Win32 = Debug|Win32
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
		{projectGUid}.Debug|Win32.ActiveCfg = Debug|Win32
		{projectGUid}.Debug|Win32.Build.0 = Debug|Win32
	EndGlobalSection
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
EndGlobal
    '''.format(solutionGUid=_SOLUTION_G_UID, projectGUid=_PROJECT_G_UID)

    # arguments: projectName, intermediateDirectory, buildCommandLine, rebuildCommandLine, cleanCommandLine, outputExecutable, definitions, includePaths
    PROJECT_FILE_OPENING =r'''<?xml version="1.0" encoding="Windows-1252"?>
      <VisualStudioProject
        ProjectType="Visual C++"
        Version="9.00"
        Name="{{projectName}}"
        ProjectGUID="{projectGUid}"
        Keyword="MakeFileProj"
        TargetFrameworkVersion="196613"
        RootNamespace="{{projectName}}"
        >
        <Platforms>
          <Platform
            Name="Win32"
          />
        </Platforms>
        <ToolFiles>
        </ToolFiles>
        <Configurations>
          <Configuration
            Name="Debug|Win32"
            OutputDirectory="{{intermediateDirectory}}"
            IntermediateDirectory="{{intermediateDirectory}}"
            ConfigurationType="0"
            >
            <Tool
              Name="VCNMakeTool"
              BuildCommandLine="{{buildCommandLine}}"
              ReBuildCommandLine="{{rebuildCommandLine}}"
              CleanCommandLine="{{cleanCommandLine}}"
              Output="{{outputExecutable}}"
              PreprocessorDefinitions="{{definitions}}"
              IncludeSearchPath="{{includePaths}}"
              ForcedIncludes=""
              AssemblySearchPath=""
              ForcedUsingAssemblies=""
              CompileAsManaged=""
            />
          </Configuration>
        </Configurations>
        <References>
        </References>
        <Files>'''.format(projectGUid=_PROJECT_G_UID)
    PROJECT_FILE_CLOSING = r'''
        </Files>
        <Globals>
        </Globals>
      </VisualStudioProject>
      '''

    DIRECTORY_OPENING = r'              <Filter Name="{name}">'
    DIRECTORY_CLOSING = r'              </Filter>'

    SOURCE_SECTION_OPENING = r'         <Filter Name="Source Files" Filter="cpp;c;cc;cxx;def;odl;idl;hpj;bat;asm;asmx">'
    SOURCE_SECTION_CLOSING = r'         </Filter>'

    HEADER_SECTION_OPENING = r'         <Filter Name="Header Files" Filter="h;hpp">'
    HEADER_SECTION_CLOSING = r'         </Filter>'

    FILE_NODE = r'                  <File RelativePath="{filePath}"></File>'

    DEFAULT_DEFINITIONS = ['WIN32','_DEBUG']

