#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

from __future__ import print_function

import os
import platform
import subprocess
import sys
from fnmatch import filter as filterFileNames
from shutil import rmtree
from threading import Thread
from time import sleep
from json import dump as dumpJson
from shlex import split as splitCmdLine

import stat_attributes as attributes


def countCpuCores():
    try:
        from psutil import cpu_count
    except ImportError:
        try:
            from multiprocessing import cpu_count
        except ImportError:
            return 1
    try:
        return cpu_count()
    except NotImplementedError:
        return 1


def isWindows():
    return True if platform.system() == "Windows" else False


def getPlatform():
    # 'Linux32/64', 'Darwin32/64', 'Java32/64', 'Windows32/64'
    machine = "64" if platform.machine()[-2:] == "64" else "32"
    platformMode = platform.system() + machine
    return platformMode


def toWindowsPath(path):
    return path.replace('/', '\\')


def toPosixPath(path):
    return path.replace('\\', '/')


def toNativePath(path):
    return toWindowsPath(path) if isWindows() else toPosixPath(path)


def nameExecutable(fileOnlyName):
    return fileOnlyName + '.exe' if isWindows() else fileOnlyName


def mkdir(path, exist_ok=False):
    if exist_ok and os.path.isdir(path):
        return
    os.makedirs(path)


def formatCommandLine(command):
    if isWindows():
        return " ".join(command) if isinstance(command, (list, tuple)) else command
    else:
        return command if isinstance(command, (list, tuple)) else splitCmdLine(command)


def execute(command, beSilent=False, **kwargs):
    commandLine = formatCommandLine(command)
    arguments = dict(bufsize=1, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    arguments.update(kwargs)
    process = subprocess.Popen(commandLine, **arguments)
    lines = []
    thread = Thread(target=__captureOutputLines, args=(process, beSilent, lines))
    thread.setDaemon(True)
    thread.start()
    thread.join()
    process.communicate()
    return process.returncode, lines


def __captureOutputLines(process, beSilent, lines):
    for _line in iter(process.stdout.readline, b''):
        if _line == '':
            break
        lines.append(_line)
        if not beSilent:
            print(_line, end='')


def executeForOutput(command, **kwargs):
    commandLine = formatCommandLine(command)
    arguments = dict(bufsize=1, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    arguments.update(kwargs)
    process = subprocess.Popen(commandLine, **arguments)
    output, _ = process.communicate()
    return output.strip()


def remove(path):
    doesExist, attemptRemoval, typeName = \
        (os.path.isdir, rmtree, 'directory') if os.path.isdir(path) else (os.path.isfile, os.remove, 'file')
    while doesExist(path):
        try:
            attemptRemoval(path)
        except OSError:
            print("Waiting for {type} '{path}' to find unlocked (probably by AntiVirus)!".format(type=typeName,
                                                                                                 path=path))
            sleep(1)


def writeJsonFile(filePath, data):
    with open(filePath, 'w') as fp:
        dumpJson(data, fp, indent=3)


def createLink(sourcePath, targetPath):
    source = os.path.relpath(sourcePath, os.path.dirname(targetPath))
    target = targetPath

    if isWindows():
        source = toWindowsPath(source)
        target = toWindowsPath(target)
        if os.path.isdir(source):
            commandLine = 'cmd /c mklink /D "{target}" "{source}" >nul'
        else:
            commandLine = 'cmd /c mklink "{target}" "{source}" >nul'
        subprocess.Popen(formatCommandLine(commandLine.format(target=target, source=source)), shell=True).wait()
    else:
        os.symlink(source, target)  # pylint: disable=no-member


def findSubFolderOnPath(subFolder, path='.'):
    currentPath = os.getcwd() if path == '.' else path
    subFolderPath = os.path.join(currentPath, subFolder)
    while not os.path.isdir(subFolderPath):
        currentPath = os.path.dirname(currentPath)
        if currentPath == os.path.dirname(currentPath):
            return None
        subFolderPath = os.path.join(currentPath, subFolder)
    return subFolderPath


def getFileLocationThroughoutCurrentPath(fileName, currentPath='.'):
    previousDirectory = None
    currentDirectory = currentPath if currentPath != '.' else os.getcwd()
    while previousDirectory != currentDirectory:
        fileLocation = os.path.join(currentDirectory, fileName)
        if os.path.isfile(fileLocation):
            return fileLocation
        previousDirectory = currentDirectory
        currentDirectory = os.path.dirname(previousDirectory)
    return None


def listFilenames(pathName, encompassingPattern, *patternsForSubsets):
    files = filterFileNames(os.listdir(pathName), encompassingPattern)
    return __selectFilesByPatterns(files, patternsForSubsets) if patternsForSubsets else set(files)


def listMakefiles(pathName, *patterns):
    files = listFilenames(pathName, '*.mak', *patterns)
    if len(patterns) != len(files) or set(patterns) != files:
        ignored = __selectIgnoredFiles(files, pathName)
        if ignored:
            files.difference_update(ignored)
    return sorted(files)


def readFileLines(filepath):
    with open(filepath, 'r') as _file:
        return _file.readlines()


def readNonEmptyLines(filepath):
    for line in readFileLines(filepath):
        line = line.strip()
        if line:
            yield line


def readTextFileAtOnce(filepath):
    with open(filepath, 'r') as aFile:
        text = aFile.read()
    return text


def locateFile(filename, mode=None, path=None):
    def _locateFileOnPath(_filename, _path):
        _filepath = os.path.join(_path, _filename)
        if isWindows() and mode and mode & os.X_OK:
            _, _ext = os.path.splitext(_filepath)
            exeExtensions = os.environ.get("PATHEXT", "").split(os.pathsep)
            if not _ext:
                return _matchExtensionToFile(_filepath, exeExtensions)
            elif _ext not in exeExtensions:
                return ""
        return _filepath if _isFileAccessible(_filepath) else ""

    def _matchExtensionToFile(_filepath, _extensions):
        for _ext in _extensions:
            if _isFileAccessible(_filepath + _ext):
                return _filepath + _ext
        else:
            return ""

    def _isFileAccessible(_filepath):
        return os.path.isfile(_filepath) and (not mode or os.access(_filepath, mode))

    if isinstance(path, str):
        return _locateFileOnPath(filename, path)
    else:
        paths = [os.path.abspath(".")] + os.environ.get("PATH", "").split(os.pathsep) if not path else path
        for _path in paths:
            filepath = _locateFileOnPath(filename, _path)
            if filepath:
                return filepath
        else:
            return ""


def locateResource(filename):
    resource = os.path.join(attributes.TOOL_PATH, attributes.RESOURCES_DIRECTORY, filename)
    if not os.path.isfile(resource):
        raise ServicesException(ServicesException.RESOURCE_NOT_FOUND.format(resource))
    return resource


def formatMakeCommand(makefile, args=(), **variables):
    makeTool = attributes.MAKE_TOOL.get(getPlatform(), "make")
    command = [makeTool, "-f", makefile]
    command.extend(args)
    command.extend(['{0}="{1}"'.format(*pair) for pair in variables.items()])
    return command


def __selectIgnoredFiles(makefiles, pathName):
    ignoreFilePathname = os.path.join(pathName, attributes.IGNORE_FILENAME)
    if os.path.isfile(ignoreFilePathname):
        ignoreList = [line.strip() for line in readNonEmptyLines(ignoreFilePathname)]
        if ignoreList:
            return __selectFilesByPatterns(makefiles, ignoreList)
    return set()


def __selectFilesByPatterns(makefiles, patterns):
    filtered = []
    for pattern in patterns:
        filtered.extend(filterFileNames(makefiles, pattern))
    return set(filtered)


def meta_class(mcs, *cls, **mewAttributes):
    mangledName = "_".join(("_", mcs.__name__,) + tuple(item.__name__ for item in cls))
    return mcs(mangledName, cls, mewAttributes)


def abstract_method(method):
    return abstract_callable(method)


def abstract_callable(callableObject):
    def call_wrapper(*args, **kwargs):
        typeName = 'method' if args and hasattr(args[0], callableObject.__name__) else callableObject.__class__.__name__
        raise NotImplementedError("The {0} '{1}' must be implemented!".format(typeName, callableObject.__name__))
    return call_wrapper


class SingletonMeta(type):
    """ A metaclass that creates a Singleton base class when called. """
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls.__instances[cls]

    def clear(cls):
        try:
            del cls.__instances[cls]  # pylint: disable=no-member
        except KeyError:
            pass


class FactoryByLegacy(type):

    def __init__(cls, name, bases, spec):
        super(FactoryByLegacy, cls).__init__(name, bases, spec)
        if not hasattr(cls, '_announcedFactoryItems'):
            cls._announcedFactoryItems = {}
        cls.__registerIfAnnounced()

    def __registerIfAnnounced(cls):
        uidAttribute = getattr(cls, 'uidAttribute', 'UID')
        uidValue = getattr(cls, uidAttribute, None)
        if uidValue:
            cls._announcedFactoryItems[uidValue] = cls

    def __iter__(cls):
        for _uid in cls._announcedFactoryItems:
            yield _uid

    def __contains__(cls, uid):
        return uid in cls._announcedFactoryItems

    def __len__(cls):
        return len(cls._announcedFactoryItems)

    def get(cls, uid, default=None):
        return cls._announcedFactoryItems.get(uid, default)

    def create(cls, uid, *args, **kwargs):
        _cls = cls._announcedFactoryItems.get(uid, cls)
        return _cls(*args, **kwargs)


class Configuration(object):

    def __init__(self, **kwargs):
        super(Configuration, self).__init__()
        self.__configuration = kwargs

    def __iter__(self):
        for key in self.__configuration:
            yield key

    def __getitem__(self, key):
        return self.__configuration.get(key, None)

    def update(self, iterable=None, **kwargs):
        if iterable:
            self.__configuration.update({key: iterable[key] for key in iterable})
        self.__configuration.update(kwargs)

    def getInt(self, key, default=0):
        try:
            return int(self.__configuration.get(key, ''))
        except ValueError:
            return default

    def get(self, key, default):
        return self.__configuration.get(key, default)


class ServicesException(Exception):
    """
    Custom exception for STAT services
    """
    NO_VS_TOOLS_FOUND = "No VS TOOLS were found on this PC."
    NO_NMAKE_FOUND = "No NMAKE was found on this PC."
    RESOURCE_NOT_FOUND = "No resource by filename '{0}' was found."


if __name__ == '__main__':
    pass
