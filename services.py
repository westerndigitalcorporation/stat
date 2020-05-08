#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT
from __future__ import print_function

import os
import platform
import subprocess
from fnmatch import filter as filterFileNames
from shutil import rmtree
from time import sleep
from json import dump as dumpJson

import stat_attributes as attributes

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

def execute(command, beSilent=False, **kwargs):
    lines = []
    arguments = dict(bufsize=1, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    arguments.update(kwargs)
    commandLine = " ".join(command) if isinstance(command, (list, tuple)) else command
    process = subprocess.Popen(commandLine, **arguments)
    for line in iter(process.stdout.readline, ''):
        if not beSilent:
            print(line, end='')
        lines.append(line)
    process.wait()
    return process.returncode,lines

def executeForOutput(command, **kwargs):
    return ''.join(execute(command, beSilent=True, **kwargs)[1]).strip()

def remove(path):
    doesExist, attemptRemoval, typeName = (os.path.isdir,rmtree,'directory') if os.path.isdir(path) else (os.path.isfile, os.remove, 'file')
    while doesExist(path):
        try:
            attemptRemoval(path)
        except OSError:
            print("Waiting for {type} '{path}' to find unlocked (probably by AntiVirus)!".format(type=typeName,path=path))
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
        subprocess.Popen(commandLine.format(target = target, source = source), shell=True).wait()
    else:
        os.symlink(source, target)

def findSubFolderOnPath(subFolder, path='.'):
    currentPath = os.getcwd() if path=='.' else path
    subFolderPath = os.path.join(currentPath, subFolder)
    while not os.path.isdir(subFolderPath):
        currentPath = os.path.dirname(currentPath)
        if currentPath == os.path.dirname(currentPath):
            return None
        subFolderPath = os.path.join(currentPath, subFolder)
    return subFolderPath

def getFileLocationThroughoutCurrentPath(fileName, currentPath = '.'):
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
    statIgnoreFile = os.path.join(pathName, '.statignore')
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

class _Singleton(type):
    """ A metaclass that creates a Singleton base class when called. """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(_Singleton('SingletonMeta', (object,), {})):

    @classmethod
    def clear(cls):
        try:
            del cls._instances[cls]
        except KeyError:
            pass

class ServicesException(Exception):
    """
    Custom exception for STAT services
    """
    NO_VS_TOOLS_FOUND = "No VS TOOLS were found on this PC."
    NO_NMAKE_FOUND = "No NMAKE was found on this PC."
    RESOURCE_NOT_FOUND = "No resource by filename '{0}' was found."


if __name__ == '__main__':
    pass