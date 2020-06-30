#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

from __future__ import print_function

import sys
from multiprocessing import Pool, freeze_support

import stat_attributes as attributes
from stat_argument_parser import StatArgumentParser
from stat_configuration import StatConfiguration
from stat_debug import Profiler
from stat_makefile_generator import StatMakefileGenerator
from services import writeJsonFile, remove, mkdir
from ide_writer import IdeWorkspaceWriter
from tests_runner import TestsRunner, TestsRunnerException

STAT_OUTPUT_DELIMITER = "=" * 70
STAT_SUMMARY = "Total:  {total} Runs  {passed} Passed  {failed} Failed"
STAT_SILENT_OUTPUT = "{0:50}:{1}"
MAKEFILE_CORRUPTION = 'Processing "{filename}" failed with exception: \n{exception}'


def runTestPackage(makefile, commandToCompile, shallRun, shallBeVerbose):
    try:
        runner = TestsRunner(makefile, commandToCompile, shallBeVerbose)
        try:
            runner.compile()
            if shallRun:
                runner.run()
        except TestsRunnerException as exception:
            runner.writeLog(exception)
            status, description = 'FAILED', str(exception)
        except Exception as exception:
            runner.writeLog(exception)
            status, description = 'CRASHED', str(exception)
        else:
            status, description = 'PASSED', ''
    except Exception as exception:
        status, description = 'CRASHED', MAKEFILE_CORRUPTION.format(filename=makefile, exception=str(exception))
    return makefile, status, description


def prepareOutputDirectories():
    remove(attributes.LOGS_DIRECTORY)
    mkdir(attributes.LOGS_DIRECTORY)
    mkdir(attributes.OUTPUT_DIRECTORY, exist_ok=True)


class StatMain(object):

    @staticmethod
    def run(manualArguments=None):
        """
        :param manualArguments: if specified, used instead of system command-line arguments
        """
        main = StatMain()
        main._run(manualArguments)

    def __init__(self):
        self.__config = StatConfiguration()
        self.__parser = StatArgumentParser(self.__config.products, self.__config.defaultProduct)
        self.__commandToCompile = self.__config.getToolchain().getCommandToCompile()
        self.__report = StatReport()

    def _run(self, manualArguments):
        self.__parser.parse(manualArguments)
        if self.__parser.ide is not None:
            self.__createIdeWorkspace()
        else:
            self.__runTests()
        if self.__parser.redundant:
            raise StatWarning('WARNING: The arguments {0} are redundant!'.format(self.__parser.redundant))

    def __runTests(self):
        prepareOutputDirectories()
        for target in self.__parser.targetProducts:
            self.__runTestsOnTarget(target)
        self.__report.write()
        print(STAT_OUTPUT_DELIMITER)
        print(STAT_SUMMARY.format(total=self.__report.total, passed=self.__report.passed, failed=self.__report.failed))
        if self.__report.failed:
            raise StatException('The following packages failed:\n\t{0}'.format('\n\t'.join(self.__report.failedList)))

    def __runTestsOnTarget(self, target):
        if self.__parser.processes:
            self.__runTestsOnTargetInParallel(target)
        else:
            self.__runTestsOnTargetInSerial(target)

    def __runTestsOnTargetInSerial(self, target):
        self.__prepareTarget(target)
        for testPackageFile in self.__parser.makeFiles:
            result = runTestPackage(testPackageFile, self.__commandToCompile, self.__parser.shallRun(),
                                    self.__parser.shallBeVerbose())
            self.__log(*result)

    def __runTestsOnTargetInParallel(self, target):
        def handleResult(result):
            self.__log(*result)
        self.__prepareTarget(target)
        pool = Pool(self.__parser.processes)
        # pool = get_context("spawn").Pool(self.__parser.processes)
        for makefile in self.__parser.makeFiles:
            args = (makefile, self.__commandToCompile, self.__parser.shallRun(), self.__parser.shallBeVerbose())
            pool.apply_async(runTestPackage, args, callback=handleResult)
        pool.close()
        pool.join()

    def __createIdeWorkspace(self):
        self.__prepareTarget(self.__parser.targetProducts[0])
        writer = IdeWorkspaceWriter(self.__parser.ide, self.__parser.makeFiles[0])
        writer.write()

    def __prepareTarget(self, name):
        self.__report.logTarget(name)
        if self.__config.isStale() or self.__parser.targetProducts != [self.__config.defaultProduct]:
            targetMakefile = StatMakefileGenerator(name + ".mak")
            targetMakefile.generate()

    def __log(self, makefile, status, info):
        self.__report[makefile] = status, info
        if not self.__parser.shallBeVerbose():
            print(STAT_SILENT_OUTPUT.format(makefile, status))


class StatReport(object):

    def __init__(self):
        self.__finalReport = {}
        self.__targetReport = self.__finalReport

    @property
    def total(self):
        return len([makefile for target in self.__finalReport for makefile in self.__finalReport[target]])

    @property
    def passed(self):
        return self.total - self.failed

    @property
    def failed(self):
        return len(self.__extractFailedOnes())

    @property
    def failedList(self):
        return set(self.__extractFailedOnes())

    def logTarget(self, name):
        self.__targetReport = {}
        self.__finalReport[name] = self.__targetReport

    def write(self):
        writeJsonFile(attributes.REPORT_FILENAME, self.__finalReport)

    def __setitem__(self, makefile, results):
        status, info = results
        self.__targetReport[makefile] = {'Status': status, 'Info': info}

    def __extractFailedOnes(self):
        return [makefile for target in self.__finalReport for makefile in self.__finalReport[target]
                if not self.__finalReport[target][makefile]['Status'] == 'PASSED']


class StatWarning(Exception):
    """
    Custom exception for the STAT-framework managed warnings
    """


class StatException(Exception):
    """
    Custom exception for the STAT-framework managed failures
    """


if __name__ == '__main__':
    freeze_support()
    try:
        if '--debug=profile' in sys.argv:
            with Profiler():
                StatMain.run()
        else:
            StatMain.run()
    except StatWarning as w:
        print("\n")
        print(w)
        print("\n=== PASSED ===")
    except Exception as e:
        print(e)
        print("\n=== FAILED ===")
        sys.exit(-1)
    else:
        print("\n=== PASSED ===")
