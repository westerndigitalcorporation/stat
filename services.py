#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

from __future__ import print_function

import os
import platform
import subprocess
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


def toWindowsPath(path):
    return path.replace('/', '\\')


def toPosixPath(path):
    return path.replace('\\', '/')


def toNativePath(path):
    return toWindowsPath(path) if isWindows() else toPosixPath(path)


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
            commandLine = 'cmd /c mklink /D "{target}" "{source}"'
        else:
            commandLine = 'cmd /c mklink "{target}" "{source}"'
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


def listMakefiles(pathName, *patterns):
    allFiles = filterFileNames(os.listdir(pathName), '*.mak')
    if patterns:
        selected = __selectFilesByPatterns(allFiles, patterns)
    else:
        selected = set(allFiles)
    ignored = __selectIgnoredFiles(allFiles, pathName)
    if ignored:
        selected.difference_update(ignored)
    return sorted(selected)


def readTextFileLines(filePath):
    _file = open(filePath)
    for line in _file.readlines():
        yield line.rstrip()
    else:
        _file.close()


def readTextFileAtOnce(filePath):
    with open(filePath, 'r') as aFile:
        text = aFile.read()
    return text


def locateResource(filename):
    resource = os.path.join(attributes.TOOL_PATH, attributes.RESOURCES_DIRECTORY, filename)
    if not os.path.isfile(resource):
        raise ServicesException(ServicesException.RESOURCE_NOT_FOUND.format(resource))
    return resource


def __selectIgnoredFiles(makefiles, pathName):
    statIgnoreFile = os.path.join(pathName, attributes.IGNORE_FILENAME)
    if os.path.exists(statIgnoreFile):
        ignoreFile = open(statIgnoreFile, 'r')
        ignoreList = [line.strip() for line in ignoreFile.readlines()]
        ignoreFile.close()
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


class Configuration(object):

    def __init__(self, **kwargs):
        super(Configuration, self).__init__()
        self.__configuration = kwargs

    def __getitem__(self, key):
        return self.__configuration.get(key, None)

    def __iter__(self):
        for key in self.__configuration:
            yield key

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
