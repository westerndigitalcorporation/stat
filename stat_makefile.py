#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import re

_STAT_FILE_NAMES_TO_IGNORE = ["stat_core.mak"]

_REG_EXP_VARIABLE = r'\s*(\w+)\s*=([\w\s\./:;\(\)$=]*)\s*'
_REG_EXP_SUBSTITUTION = r'(\$\()\s*([\w]*)\s*(\))'
_REG_EXP_INCLUDE = r'\s*!INCLUDE\s+(<\s*)?([\w\./:\s]*)(\s*>)?\s*$'
_DEFAULT_INCLUDE = '' if os.getenv('INCLUDE') is None else os.getenv('INCLUDE')

class StatMakefile(object):
    """
    Parser for Makefiles formatted for STAT
    """
    SOURCES = 'SOURCES'
    INCLUDES = 'INCLUDES'
    INTERFACES = 'DUMMY_INTERFACES'
    DEFINES = 'DEFINES'
    INCLUDE = 'INCLUDE'
    NAME = 'NAME'

    def __init__(self, filePath):
        self.__name = os.path.splitext(os.path.basename(filePath))[0]
        self.__file = _MakefileReader(filePath)
        self.__items = {self.INCLUDE: _DEFAULT_INCLUDE}
        self.__parse()

    @property
    def fileName(self):
        return self.__name

    def __getitem__(self, key):
        _key = key.upper()
        return self.__items[_key] if _key in self else ''

    def __setitem__(self, key, value):
        _key = key.upper()
        self.__items[_key] = (self.__interpretString(value)).strip()

    def __contains__(self, key):
        _key = key.upper()
        return _key in self.__items

    def __iter__(self):
        for key in self.__items:
            yield key

    def __parse(self):
        for line in self.__file.readLines():
            if not self.__parseForInclude(line):
                self.__parseForVariable(line)

    def __parseForInclude(self, currentLine):
        regexResults = re.search(_REG_EXP_INCLUDE, currentLine, re.IGNORECASE)
        if regexResults:
            includePathSuffix, fileName, includePathPrefix = regexResults.groups()
            if (includePathSuffix is None) ^ (includePathPrefix is None):
                raise StatMakFileException(
                    "Invalid inclusion '{0}' in Makefile '{1}'!".format(currentLine, self.__file.getCurrentFilePath()))
            if os.path.basename(fileName) not in _STAT_FILE_NAMES_TO_IGNORE:
                self.__file.includeNestedFile(fileName, self[self.INCLUDE])
                return True
        else:
            return False

    def __parseForVariable(self, currentLine):
        regexResults = re.search(_REG_EXP_VARIABLE, currentLine)
        if regexResults:
            variable, values = regexResults.groups()
            self[variable] = values

    def __interpretString(self, string):
        def interpretVariable(regMatch):
            variable = regMatch.group(2)
            return self[variable]
        return re.sub(_REG_EXP_SUBSTITUTION, interpretVariable, string)

class _MakefileReader(object):
    """
    Mak-file reader that allows reading with included files
    """

    def __init__(self, filePath):
        if not os.path.isfile(filePath):
            raise StatMakFileException("Makefile '{fileName}' doesn't exist!".format(fileName = filePath))
        self.__filePath = filePath
        self.__nested = None

    def includeNestedFile(self, filename, includePaths):
        if self.__nested is not None:
            self.__nested.includeNestedFile(filename, includePaths)
        else:
            self.__nested = _MakefileReader(self.__findFilePath(filename, includePaths))

    def getCurrentFilePath(self):
        if self.__nested is not None:
            return self.__nested.getCurrentFilePath()
        else:
            return self.__filePath

    def readLines(self):
        for line in self.__readSyntacticLines():
            yield line
            for nested in self.__readNestedFileLines():
                yield nested

    def __readNestedFileLines(self):
        if self.__nested is not None:
            for line in self.__nested.readLines():
                yield line
            else:
                self.__nested = None

    def __readSyntacticLines(self):
        line = ''
        for nextLine in self.__readTextFileLines():
            line = line + nextLine if line else nextLine
            if line.endswith('\\'):
                line = line[:-1]
                continue
            yield line
            line = ''
        else:
            if line:
               yield  line

    def __readTextFileLines(self):
        _file = open(self.__filePath)
        for line in _file:
            yield line.rstrip()
        else:
            _file.close()

    def __findFilePath(self, filename, includePaths):
        filePath = os.path.join(os.path.dirname(self.__filePath), filename)
        if os.path.isfile(filePath):
            return filePath
        else:
            return self.__findFileWithinIncludePaths(filename, includePaths)

    def __findFileWithinIncludePaths(self, filename, includePaths):
        for filePath in includePaths.split(';'):
            filePath = os.path.join(filePath, filename)
            if os.path.isfile(filePath):
                return filePath
        else:
            raise StatMakFileException(
                "Attempt to include not existing file '{0}' within '{1}'.".format(filename, self.__filePath))


class StatMakFileException(Exception):
    """
    Custom exception for STAT mak-file parser
    """