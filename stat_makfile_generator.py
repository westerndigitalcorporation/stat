#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

import os

from services import vsTools, toPosixPath, config, isWindows

_makFileTemplate = """# Makfile generated by STAT
TOOL_VERSION = {version}
NAME = {name}
TOOL_DIR = {tool_path}
DUMMIES_DIR = {dummies_path}
OUTPUT_DIR = {output_path}
VS_TOOL = {vs_tool}

!INCLUDE {product_file_path}
!INCLUDE {tool_path}/tools.mak
!INCLUDE {tool_path}/stat_core.mak
"""

class StatMakefileGenerator:
    AUTO_GENERATED_MAKEFILE = '/'.join([config.OUTPUT_DIRECTORY, "stat.mak"])

    def __init__(self, productMakefile):
        toolPath = toPosixPath(config.getToolDirectory())
        productFilePath = '/'.join([toPosixPath(config.PRODUCT_DIRECTORY), productMakefile])
        if not os.path.isfile(productFilePath):
            raise StatMakefileGeneratorException("The product makefile '{0} was not found".format(productFilePath))

        self.__fileContext = _makFileTemplate.format(version=config.VERSION,
                                                     name = productMakefile.split('.')[0],
                                                     tool_path = toolPath,
                                                     dummies_path = config.DUMMIES_DIRECTORY,
                                                     output_path = config.OUTPUT_DIRECTORY,
                                                     vs_tool = toPosixPath(vsTools.getToolChainPath()) if isWindows() else '',
                                                     product_file_path = productFilePath)

    def generate(self):
        fileName = self.AUTO_GENERATED_MAKEFILE
        directory = os.path.dirname(fileName)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        fileHandle = open(fileName, 'w')
        fileHandle.write(self.__fileContext)
        fileHandle.flush()
        fileHandle.close()

class StatMakefileGeneratorException(Exception):
    """
    Custom exception for STAT mak-file generator
    """