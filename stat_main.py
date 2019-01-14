#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT
from __future__  import print_function

import sys

import stat_attributes as attributes
from stat_argument_parser import StatArgumentParser
from stat_configuration import StatConfiguration
from stat_makefile_generator import StatMakefileGenerator
from services import writeJsonFile, remove, mkdir
from ide_writer import IdeWorkspaceWriter
from tests_runner import TestsRunner, TestsRunnerException

STAT_RESULT_DELIMITER = "=" * 70
STAT_RESULT_SUMMARY = "Total:  {total} Runs  {passed} Passed  {failed} Failed"
STAT_SILENT_OUTPUT = "{0:50}:{1}"

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
        self.__failures = []
        self.__report = StatReport()

    def _run(self, manualArguments):
        self.__parser.parse(manualArguments)
        if self.__parser.ide is not None:
            self.__createIdeWorkspace()
        else:
            self.__runTests()

    def __runTests(self):
        remove(attributes.LOGS_DIRECTORY)
        total = 0
        for testFile in self.__packageFiles():
            total += 1
            self.__runTestPackage(testFile)
        failures = len(self.__failures)
        self.__report.write()
        print(STAT_RESULT_DELIMITER)
        print(STAT_RESULT_SUMMARY.format(total=total, passed=total - failures, failed=failures))
        if self.__failures:
            raise StatException('The following packages failed:\n\t{0}'.format('\n\t'.join(set(self.__failures))))

    def __createIdeWorkspace(self):
        self.__prepareTarget(self.__parser.targetProducts[0])
        writer = IdeWorkspaceWriter(self.__parser.ide, self.__parser.makeFiles[0])
        writer.write()

    def __packageFiles(self):
        for target in self.__parser.targetProducts:
            self.__prepareTarget(target)
            for makeFile in self.__parser.makeFiles:
                yield makeFile

    def __prepareTarget(self, name):
        self.__report.logTarget(name)
        if self.__config.isStale() or self.__parser.targetProducts != [self.__config.defaultProduct]:
            targetMakefile = StatMakefileGenerator(name + ".mak")
            targetMakefile.generate()

    def __runTestPackage(self, testPackageFile):
        runner = TestsRunner(testPackageFile, self.__parser.shallBeVerbose())
        try:
            runner.compile()
            if self.__parser.shallRun():
                runner.run()
        except TestsRunnerException as exception:
            self.__log(testPackageFile, 'FAILED', exception.message, runner.getLog())
        except Exception as exception:
            self.__log(testPackageFile, 'CRASHED', str(exception), [])
        else:
            self.__log(testPackageFile, 'PASSED', '', [])

    def __log(self, testPackageFile, status, exception, screenLog):
        self.__report[testPackageFile] = {'Status': status, 'Info': exception}
        if exception:
            self.__failures.append(testPackageFile)
            if screenLog:
                mkdir(attributes.LOGS_DIRECTORY, exist_ok=True)
                logFilePath = '/'.join([attributes.LOGS_DIRECTORY, testPackageFile[:-4] + '.log'])
                with open(logFilePath, 'w') as fp:
                    fp.writelines(screenLog)
        if not self.__parser.shallBeVerbose():
            print(STAT_SILENT_OUTPUT.format(testPackageFile, status))

class StatReport(object):

    def __init__(self):
        self.__finalReport = {}
        self.__targetReport = self.__finalReport

    def logTarget(self, name):
        self.__targetReport = {}
        self.__finalReport[name] = self.__targetReport

    def __setitem__(self, key, value):
        self.__targetReport[key] = value

    def write(self):
        writeJsonFile(attributes.REPORT_FILENAME, self.__finalReport)

class StatException(Exception):
    """
    Custom exception for the STAT framework managed failures
    """

if __name__ == '__main__':
    try:
        StatMain.run()
    except Exception as e:
        print(e)
        print("\n=== FAILED ===")
        sys.exit(-1)
    else:
        print("\n=== PASSED ===")
