import os
import sys

from shutil import rmtree

from makfile_logger import MakfileLogger
from services import config
from testing_tools import FileBasedTestCase


class TestMakfileLogger(FileBasedTestCase):

    def setUp(self):
        self.makfile = 'simplified_example.mak'
        self.logfile = '/'.join([config.LOGS_DIRECTORY, self.makfile.replace('.mak', '.log')])

    def tearDown(self):
        if os.path.isfile(self.logfile):
            os.remove(self.logfile)
        if os.path.isdir(config.LOGS_DIRECTORY):
            rmtree(config.LOGS_DIRECTORY)

    def test__init__basics(self):
        if not os.path.isdir(config.LOGS_DIRECTORY):
            os.mkdir(config.LOGS_DIRECTORY)
        logger = MakfileLogger(self.makfile)
        self.assertEqual(logger._makfile, self.makfile)
        self.assertFalse(logger._isSilent)
        self.assertTrue(os.path.isfile(self.logfile))
        logfileReference = logger._logfile
        del logger
        self.assertTrue(logfileReference.closed)

    def test_writeBasics(self):
        testLines = ['test line1\n', 'test line2\n']
        logger = MakfileLogger(self.makfile)
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
        logger = MakfileLogger(self.makfile, beSilent=True)
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

