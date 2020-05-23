#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

import os
import re

_STAT_FILE_NAMES_TO_IGNORE = ["stat_core.mak"]

_REG_EXP_VARIABLE = '\s*(\w+)\s*=\s*(.+)\s*'
_REG_EXP_SUBSTITUTION = '\$\((?P<variable>[^\(\)\$]+)\)'
_REG_EXP_INCLUDE = '^\s*!INCLUDE\s+(<)?(?P<path>[^><]+)(?(1)>|\s*)$'

class StatMakefile(object):
    """
    Parser for Makefiles formatted for STAT
    """
    SOURCES = 'SOURCES'
    INCLUDES = 'INCLUDES'
    INTERFACES = 'DUMMY_INTERFACES'
    DEFINES = 'DEFINES'
    NAME = 'OUTPUT_NAME'
    EXEC = 'OUTPUT_EXEC'

    def __init__(self, filePath):
        self.__name = os.path.splitext(os.path.basename(filePath))[0]
        self.__file = _MakefileReader(filePath)
        self.__items = {}
        self.__parse()

    @property
    def name(self):
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
            fileName = regexResults.group('path')
            if os.path.basename(fileName) not in _STAT_FILE_NAMES_TO_IGNORE:
                self.__file.includeNestedFile(fileName)
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
            variable = regMatch.group('variable')
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

    def includeNestedFile(self, filename):
        if self.__nested is not None:
            self.__nested.includeNestedFile(filename)
        elif os.path.isfile(filename):
            self.__nested = _MakefileReader(filename)
        else:
            raise StatMakFileException(
                "Attempt to include not existing file '{0}' within '{1}'.".format(filename, self.__filePath))

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


class StatMakFileException(Exception):
    """
    Custom exception for STAT mak-file parser
    """