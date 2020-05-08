#!/usr/bin/env python
import os

from stat_attributes import TOOL_PATH, RESOURCES_DIRECTORY
from services import executeForOutput, execute
from stat_tool_chain import StatToolchain

NMAKE_ARGUMENTS = "/S /NOLOGO /ERRORREPORT:NONE /F"
SUPPORTED = {8.0 : 2005, 9.0 : 2008, 10.0: 2010, 11.0: 2012, 12.0: 2013, 14.0: 2015, 15.0: 2017, 16.0: 2019}
SOLUTION_FORMATS = {8.0 : 9.0, 9.0 : 10.0, 10.0: 11.0, 11.0: 11.0, 12.0: 12.0, 14.0: 12.0, 15.0: 12.0, 16.0: 12.0}

TO_FIND_LATER_ON_DEMAND = None


class MsvsTools(StatToolchain):
    __LATEST_FOUND = None

    @classmethod
    def find(cls, versionYear=None):
        """
        :rtype: MsvsTools
        """
        if not versionYear:
            return cls.__findLatest()
        else:
            return cls.__findSpecific(versionYear)

    @classmethod
    def reset(cls):
        cls.__LATEST_FOUND = None

    @classmethod
    def __findLatest(cls):
        if not cls.__LATEST_FOUND:
            cls.__LATEST_FOUND = MsvsTools()
        return cls.__LATEST_FOUND

    @classmethod
    def __findSpecific(cls, versionYear):
        for version in SUPPORTED:
            if SUPPORTED[version] == versionYear:
                return MsvsTools(version)
        else:
            raise VsToolsException(VsToolsException.UNSUPPORTED_TOOLS.format(versionYear))

    def __init__(self, versionId = None):
        self.__versionId = None
        if versionId:
            self.__findSpecificVersion(versionId)
        else:
            self.__findLatestVersion()
        self.__devBatchFile = TO_FIND_LATER_ON_DEMAND
        self.__nmakeFile = TO_FIND_LATER_ON_DEMAND
        self.__environment = TO_FIND_LATER_ON_DEMAND
        #print("Toolchain: MSVS (v.{0})".format(self.year))

    @property
    def path(self):
        return self.__toolsPath

    @property
    def devBatchFile(self):
        if not self.__devBatchFile:
            self.__devBatchFile = self.__determineDevBatchFile()
        return self.__devBatchFile

    @property
    def nmakeFilePath(self):
        if not self.__nmakeFile:
            self.__nmakeFile = self.__queryDevEnvironment("where nmake").splitlines()[-1]
        return self.__nmakeFile

    @property
    def versionId(self):
        if not self.__versionId:
            self.__versionId = self.__determineVersionId()
        return self.__versionId

    @property
    def year(self):
        return SUPPORTED[self.versionId]

    @property
    def solutionFormat(self):
        return SOLUTION_FORMATS[self.versionId]

    def getCommandToCompile(self):
        return '"{nmake}" {arguments} {{0}}'.format(nmake=self.nmakeFilePath, arguments=NMAKE_ARGUMENTS)

    def __findSpecificVersion(self, version):
        self.__versionId = version
        toolsPath = self.__queryOsEnvironmentForPath(version)
        if not toolsPath:
            toolsPath = self.__queryVswhereForPathOfSpecific(version)
        if not toolsPath:
            raise VsToolsException(VsToolsException.NO_TOOLS_FOUND)
        self.__toolsPath = toolsPath

    def __findLatestVersion(self):
        self.__versionId = TO_FIND_LATER_ON_DEMAND
        toolsPath = self.__queryVswhereForPathOfLatest()
        if not toolsPath:
            for version in sorted(SUPPORTED, reverse=True):
                toolsPath = self.__queryOsEnvironmentForPath(version)
                if toolsPath:
                    self.__versionId = version
                    break
            else:
                raise VsToolsException(VsToolsException.NO_TOOLS_FOUND)
        self.__toolsPath = toolsPath

    def __queryVswhereForPathOfLatest(self):
        self.__vswhereSelect = ''
        return self.__queryVswhereForPath('')

    def __queryVswhereForPathOfSpecific(self, version):
        searchPattern = '-version [{0},{1})'.format(version, version + 1.0)
        return self.__queryVswhereForPath(searchPattern)

    @staticmethod
    def __queryVswhereForPath(searchPattern):
        cmdLine = os.path.join(TOOL_PATH, RESOURCES_DIRECTORY,
                               "vswhere.exe -legacy {0} -property installationPath -latest")
        toolsPath = executeForOutput(cmdLine.format(searchPattern))
        if not toolsPath == '':
            toolsPath = os.path.join(toolsPath,"Common7", "Tools")
        return toolsPath

    @staticmethod
    def __queryOsEnvironmentForPath(version):
        return os.environ.get("VS{0}0COMNTOOLS".format(int(version)), '')

    def __determineDevBatchFile(self):
        filename = os.path.join(self.path, "VsDevCmd.bat")
        if not os.path.isfile(filename):
            filename = os.path.join(self.path, "vsvars32.bat")
            if not os.path.isfile(filename):
                raise VsToolsException(VsToolsException.INCOMPATIBLE_TOOLS)
        return filename

    def __determineVersionId(self):
        output = self.__queryDevEnvironment("set VisualStudioVersion").splitlines()[-1]
        try:
            versionId = float(output.split('=')[1])
        except:
            raise VsToolsException(VsToolsException.INCOMPATIBLE_TOOLS)
        return versionId

    def __queryDevEnvironment(self, queryCommandLine):
        commandLine = " ".join(['"{0}"'.format(self.devBatchFile), "&&", queryCommandLine])
        output = executeForOutput(commandLine)
        if not output:
            raise VsToolsException(VsToolsException.INCOMPATIBLE_TOOLS)
        return output

class VsToolsException(Exception):
    """
    Custom exception for STAT VS-Tools
    """
    NO_TOOLS_FOUND = "No MSVS Tools were found on this PC."
    UNSUPPORTED_TOOLS = "MSVS Tools {0} are not explicitly supported."
    INCOMPATIBLE_TOOLS = "MSVS Tools are not operable."

if __name__ == '__main__':
    for _tools in (MsvsTools.find(2008), MsvsTools.find()):
        print(_tools.nmakeFilePath)
        print(_tools.versionId)