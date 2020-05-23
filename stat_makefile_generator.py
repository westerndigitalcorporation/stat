#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

import os

import stat_attributes as attributes
from services import toPosixPath, isWindows, mkdir
from stat_configuration import StatConfiguration

_makFileTemplate = """# Makefile autogenerated by STAT
{configuration}
OUTPUT_NAME = {name}
OUTPUT_EXEC = {name}{extension}
VS_DEV = {vs_dev}

!INCLUDE {product_file_path}
!INCLUDE {tool_path}/tools.mak
!INCLUDE {tool_path}/stat_core.mak
"""

class StatMakefileGenerator(object):
    def __init__(self, productMakefile):
        self.__targetName = productMakefile.split('.')[0]
        self.__productFilePath = '/'.join([toPosixPath(attributes.PRODUCT_DIRECTORY), productMakefile])
        if not os.path.isfile(self.__productFilePath):
            raise StatMakefileGeneratorException("The product file '{0}' was not found".format(self.__productFilePath))

    def generate(self):
        config = StatConfiguration()
        tools = config.getMsvsTools()
        configuration = '\n'.join(['{0} = {1}'.format(key, config[key]) for key in config])
        fileContext = _makFileTemplate.format(configuration=configuration,
                                              name=self.__targetName,
                                              extension='.exe' if isWindows() else '',
                                              vs_dev=toPosixPath(tools.devBatchFile) if isWindows() else '',
                                              tool_path=toPosixPath(attributes.TOOL_PATH),
                                              product_file_path=self.__productFilePath)
        fileName = attributes.AUTO_GENERATED_MAKEFILE
        directory = os.path.dirname(fileName)
        mkdir(directory, exist_ok=True)
        fileHandle = open(fileName, 'w')
        fileHandle.write(fileContext)
        fileHandle.flush()
        fileHandle.close()

class StatMakefileGeneratorException(Exception):
    """
    Custom exception for STAT mak-file generator
    """
