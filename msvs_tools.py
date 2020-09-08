#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

import os

from stat_attributes import TOOL_PATH, RESOURCES_DIRECTORY
from services import executeForOutput, toPosixPath, Configuration
from build_tools import BuildTools

NMAKE_ARGUMENTS = "/S /C /NOLOGO /F"
SUPPORTED = {8.0: 2005, 9.0: 2008, 10.0: 2010, 11.0: 2012, 12.0: 2013, 14.0: 2015, 15.0: 2017, 16.0: 2019}
SOLUTION_FORMATS = {8.0: 9.0, 9.0: 10.0, 10.0: 11.0, 11.0: 11.0, 12.0: 12.0, 14.0: 12.0, 15.0: 12.0, 16.0: 12.0}


class MsvsTools(BuildTools):

    def __init__(self, configuration):
        """
        :type configuration: Configuration
        """
        super(MsvsTools, self).__init__(configuration)
        self.__toolsPath, self.__versionId = locateTools(configuration.getInt('MSVS_VERSION', None))
        self.__devBatchFile = self.__determineDevBatchFile()
        configuration.update(MSVS_DEV=toPosixPath(self.__devBatchFile))
        self.__nmakeFile = None

    @property
    def path(self):
        return self.__toolsPath

    @property
    def devBatchFile(self):
        return self.__devBatchFile

    @property
    def nmakeFilePath(self):
        if not self.__nmakeFile:
            self.__nmakeFile = self.__queryDevEnvironment("where nmake").splitlines()[-1]
        return self.__nmakeFile

    @property
    def versionId(self):
        return self.__versionId

    @property
    def year(self):
        return SUPPORTED[self.__versionId]

    @property
    def solutionFormat(self):
        return SOLUTION_FORMATS[self.__versionId]

    def getCommandToCompile(self):
        return '"{nmake}" {arguments} {{0}}'.format(nmake=self.nmakeFilePath, arguments=NMAKE_ARGUMENTS)

    def __determineDevBatchFile(self):
        filename = os.path.join(self.__toolsPath, "VsDevCmd.bat")
        if not os.path.isfile(filename):
            filename = os.path.join(self.__toolsPath, "vsvars32.bat")
            if not os.path.isfile(filename):
                raise VsToolsException(VsToolsException.INCOMPATIBLE_TOOLS)
        return filename

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


def locateTools(versionYear):
    return __findSpecific(versionYear) if versionYear else __findLatest()


def __versionYearToVersionId(versionYear):
    for version in SUPPORTED:
        if SUPPORTED[version] == versionYear:
            return version
    else:
        raise VsToolsException(VsToolsException.UNSUPPORTED_TOOLS.format(versionYear))


def __queryVswhereForPath(version=None):
    cmd = os.path.join(TOOL_PATH, RESOURCES_DIRECTORY, "vswhere.exe")
    if not version:
        version = executeForOutput(" ".join([cmd, "-legacy", "-property", "installationVersion", "-latest"]))
        version = float(version.split(".")[0]) if version else None
    searchPattern = '-version [{0},{1})'.format(version, version + 1.0) if version else ''
    cmdLine = " ".join([cmd, "-legacy", searchPattern, "-property", "installationPath", "-latest"])
    toolsPath = executeForOutput(cmdLine)
    if not toolsPath == '':
        toolsPath = os.path.join(toolsPath, "Common7", "Tools")
    return toolsPath, version


def __findSpecific(versionYear):
    versionId = __versionYearToVersionId(versionYear)
    toolsPath = __queryOsEnvironmentForPath(versionId)
    if not toolsPath:
        toolsPath, _ = __queryVswhereForPath(versionId)
    if not toolsPath:
        raise VsToolsException(VsToolsException.NO_TOOLS_FOUND)
    return toolsPath, versionId


def __findLatest():
    toolsPath, versionId = __queryVswhereForPath()
    if toolsPath:
        return toolsPath, versionId
    for versionId in sorted(SUPPORTED, reverse=True):
        toolsPath = __queryOsEnvironmentForPath(versionId)
        if toolsPath:
            return toolsPath, versionId
    else:
        raise VsToolsException(VsToolsException.NO_TOOLS_FOUND)


def __queryOsEnvironmentForPath(version):
    return os.environ.get("VS{0}0COMNTOOLS".format(int(version)), '')


if __name__ == '__main__':
    pass
