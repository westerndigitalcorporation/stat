#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
from shutil import copyfile, rmtree
from time import sleep

from makfile_logger import MakfileLogger
from services import vsTools, config, remove
from stat_makefile import StatMakefile
import subprocess

class StatMakefileExecutor(object):

    def __init__(self, fileName, beSilent = False):
        self._makfileName = fileName
        self._makfile = StatMakefile(fileName)
        self._logger = MakfileLogger(fileName, beSilent)

    def compile(self):
        commandLine = ' '.join(['"{0}"'.format(vsTools.getMakeToolLocation()), vsTools.NMAKE_ARGUMENTS, self._makfileName])
        if self.__execute(commandLine):
            raise StatMakFileExecutorException(StatMakFileExecutorException.BUILD_FAILURE)
    
    def run(self):
        avBypassExecutable = os.path.normcase('/'.join([config.AV_BYPASS_DIRECTORY, self.__name, self._makfile.fileName + '.exe']))
        if not os.path.isdir(os.path.dirname(avBypassExecutable)):
            os.makedirs(os.path.dirname(avBypassExecutable))
        remove(avBypassExecutable)
        copyfile(self.executablePathName, avBypassExecutable)
        if self.__execute(avBypassExecutable):
            raise StatMakFileExecutorException(StatMakFileExecutorException.EXECUTION_FAILURE)

    def pack(self):
        packedExecutable = os.path.join(config.PACKED_DIRECTORY, self._makfile.fileName + '.exe')
        if not os.path.isdir(config.PACKED_DIRECTORY):
            os.makedirs(config.PACKED_DIRECTORY)
        copyfile(self.executablePathName, packedExecutable)

    @staticmethod
    def clear():
        for subDirectory in config.OUTPUT_SUB_DIRECTORIES:
            fullPath = os.path.join(config.OUTPUT_DIRECTORY, subDirectory)
            remove(fullPath)

    def __execute(self, commandLine):
        process = subprocess.Popen(commandLine, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        while True:
            line = process.stdout.readline()
            if line == '':
                if None != process.poll():
                    break
            else:
                self._logger.write(line)
        return process.wait()
    
    def __del__(self):
        pass

    @property
    def executablePathName(self):
        return os.path.join(config.OUTPUT_DIRECTORY, 'bin', self.__nameOfExecutable)

    @property
    def __nameOfExecutable(self):
        return '{0}.exe'.format(self.__name)

    @property
    def __name(self):
        return self._makfile[self._makfile.NAME]

class StatMakFileExecutorException(Exception):
    """
    Custom exception for STAT mak-file executor
    """
    BUILD_FAILURE = "Failed on building (i.e. compilation and linking)!"
    EXECUTION_FAILURE = "Failed on test-execution!"