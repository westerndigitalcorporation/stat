import os
import sys

from shutil import rmtree

import stat_attributes as attributes
from makefile_logger import MakefileLogger
from testing_tools import FileBasedTestCase

class TestMakefileLogger(FileBasedTestCase):

    def setUp(self):
        self.makefile = 'simplified_example.mak'
        self.logfile = '/'.join([attributes.LOGS_DIRECTORY, self.makefile.replace('.mak', '.log')])

    def tearDown(self):
        if os.path.isfile(self.logfile):
            os.remove(self.logfile)
        if os.path.isdir(attributes.LOGS_DIRECTORY):
            rmtree(attributes.LOGS_DIRECTORY)

    def test__init__basics(self):
        if not os.path.isdir(attributes.LOGS_DIRECTORY):
            os.mkdir(attributes.LOGS_DIRECTORY)
        logger = MakefileLogger(self.makefile)
        self.assertEqual(logger._makefile, self.makefile)
        self.assertFalse(logger._isSilent)
        self.assertTrue(os.path.isfile(self.logfile))
        logfileReference = logger._logfile
        del logger
        self.assertTrue(logfileReference.closed)

    def test_writeBasics(self):
        testLines = ['test line1\n', 'test line2\n']
        logger = MakefileLogger(self.makefile)
        lines = []
        for testLine in testLines:
            lines.append(self.writeToLoggerAndCapturePrintLines(logger, testLine))
        self.assertEqual(testLines, lines)
        del logger
        resultFile = open(self.logfile, 'r')
        lines = resultFile.readlines()
        resultFile.close()
        self.assertEqual(lines, testLines)

    def test_writeUponSilent(self):
        testLine = 'test line\n'
        logger = MakefileLogger(self.makefile, beSilent=True)
        lines = self.writeToLoggerAndCapturePrintLines(logger, testLine)
        self.assertEqual('', lines)
        del logger
        resultFile = open(self.logfile, 'r')
        lines = resultFile.readlines()
        resultFile.close()
        self.assertEqual(lines, [testLine])

    def writeToLoggerAndCapturePrintLines(self, logger, line):
        class StdoutSpy(object):
            def __init__(self):
                self.contents = ''
            def write(self, string):
                self.contents += string
        stream = StdoutSpy()
        stdoutOriginal = sys.stdout
        sys.stdout = stream
        logger.write(line)
        sys.stdout = stdoutOriginal
        return stream.contents
