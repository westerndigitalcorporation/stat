#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

import os
import platform

import stat_attributes as attributes
from services import toPosixPath, isWindows, mkdir
from stat_configuration import StatConfiguration
from build_tools_crawler import BuildToolsCrawler
from stat_makefile import StatMakefile

_makFileTemplate = """# Makefile autogenerated by STAT
{variables}

include {product_file_path}
include {tool_path}/components.mak
include {tool_path}/stat_build.mak
"""


class StatMakefileGenerator(object):

    def __init__(self, productMakefile):
        self.__targetName = productMakefile.split('.')[0]
        self.__productFilePath = '/'.join([toPosixPath(attributes.PRODUCT_DIRECTORY), productMakefile])
        if not os.path.isfile(self.__productFilePath):
            raise StatMakefileGeneratorException("The product file '{0}' was not found".format(self.__productFilePath))

    def generate(self):
        variables = self.__constructVariablesInitialization()
        fileContext = _makFileTemplate.format(variables=variables,
                                              tool_path=toPosixPath(os.path.relpath(attributes.TOOL_PATH)),
                                              product_file_path=self.__productFilePath)
        fileName = attributes.AUTO_GENERATED_MAKEFILE
        directory = os.path.dirname(fileName)
        mkdir(directory, exist_ok=True)
        fileHandle = open(fileName, 'w')
        fileHandle.write(fileContext)
        fileHandle.flush()
        fileHandle.close()

    def __constructVariablesInitialization(self):
        def _formatAssignment(_variable, _value):
            return '{0} = {1}'.format(_variable, _value)

        def _getValues(*_valueSets):
            return [_formatAssignment(_key, _values[_key]) for _values in _valueSets for _key in iter(_values)]

        values = [
            _formatAssignment(StatMakefile.OS, platform.system()),
            _formatAssignment(StatMakefile.NAME, self.__targetName),
            _formatAssignment(StatMakefile.EXEC, self.__targetName + '.exe' if isWindows() else self.__targetName)
        ]
        values += _getValues(StatConfiguration(), BuildToolsCrawler().getBuildAttributes())
        return '\n'.join(values)


class StatMakefileGeneratorException(Exception):
    """
    Custom exception for STAT mak-file generator
    """
