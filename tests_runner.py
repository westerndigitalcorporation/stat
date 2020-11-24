#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

import os

import stat_attributes as attributes
from services import execute, formatMakeCommand
from stat_makefile import StatMakefile


class TestsRunner(object):

    def __init__(self, makefileName, makeArguments, isVerbose=True):
        self.__fileName = makefileName
        self.__makefile = StatMakefile(makefileName)
        self.__beSilent = not isVerbose
        self.__log = []
        self.__arguments = makeArguments

    def __getOutputPath(self, *args):
        makefile = self.__makefile
        return os.path.join(attributes.OUTPUT_DIRECTORY, makefile[self.__makefile.NAME], makefile.name, *args)

    def compile(self):
        environ = dict(os.environ, STAT_NAMESPACE=self.__makefile.name)
        makeCommand = formatMakeCommand(self.__fileName, self.__arguments, )
        status, log = execute(makeCommand, beSilent=self.__beSilent, env=environ)
        self.__log.extend(log)
        if status:
            raise TestsRunnerException('Package "{0}" failed to compile.'.format(self.__fileName))

    def run(self):
        status, log = execute(self.__getOutputPath('bin', self.__makefile[StatMakefile.EXEC]), beSilent=self.__beSilent)
        self.__log.extend(log)
        if status:
            message = 'The executable of package "{0}" failed with error-code {1:#X}.\n'.format(self.__fileName,
                                                                                                status & 0xFFFFFFFF)
            self.__log.append(message)
            raise TestsRunnerException(message)

    def getLog(self):
        return self.__log

    def writeLog(self, extraInfo=''):
        logFilePath = '/'.join([attributes.LOGS_DIRECTORY, self.__makefile.name + '.log'])
        with open(logFilePath, 'a') as fp:
            fp.writelines(self.__log)
            fp.write(extraInfo)


class TestsRunnerException(Exception):
    """
    Custom exception for STAT test-package runner
    """