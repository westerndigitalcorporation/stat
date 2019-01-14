import os

import stat_attributes as attributes
from services import execute, remove
from stat_configuration import StatConfiguration
from stat_makefile import StatMakefile
from vs_tools import StatToolchain

class TestsRunner(object):

    def __init__(self, makefileName, isVerbose=True):
        self.__fileName = makefileName
        self.__makefile = StatMakefile(makefileName)
        self.__beSilent = not isVerbose
        self.__log = []
        self.__clearOutputs()

    def __clearOutputs(self):
        for directory in attributes.OUTPUT_SUB_DIRECTORIES:
            remove(self.__getOutputPath(directory))

    def __getOutputPath(self, *args):
        return os.path.join(attributes.OUTPUT_DIRECTORY, self.__makefile.name, *args)

    def compile(self):
        toolchain = StatConfiguration().getToolchain() # type: StatToolchain
        status, log = execute(toolchain.getCompilationCommand(self.__fileName), beSilent=self.__beSilent,
                              env=dict(os.environ, PRIVATE_NAME=self.__makefile.name))
        self.__log.extend(log)
        if status:
            raise TestsRunnerException('Package "{0}" failed to compile.'.format(self.__fileName))

    def run(self):
        status, log = execute(self.__getOutputPath('bin', self.__makefile[StatMakefile.EXEC]), beSilent=self.__beSilent)
        self.__log.extend(log)
        if status:
            raise TestsRunnerException('Tests of package "{0}" failed.'.format(self.__fileName))

    def getLog(self):
        return self.__log

class TestsRunnerException(Exception):
    """
    Custom exception for STAT test-package runner
    """