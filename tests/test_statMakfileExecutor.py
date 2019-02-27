import os
from shutil import copyfile, rmtree

import sys

from testing_tools import call

from services import config, vsTools, remove
from makfile_logger import MakfileLogger
from stat_makefile_executor import StatMakefileExecutor, StatMakFileExecutorException
from stat_makfile_generator import StatMakefileGenerator
from stat_makefile import StatMakefile
from testing_tools import FileBasedTestCase, StdOutputSubstitution


class TestStatMakefileExecutor(FileBasedTestCase):
    CUT = 'stat_makefile_executor'
    PRODUCT_FILE = 'product.mak'
    PRODUCT_NAME = PRODUCT_FILE[:-4]
    MAKFILE_NAME = 'full_example.mak'
    LOGFILE_NAME = os.path.join(config.LOGS_DIRECTORY, MAKFILE_NAME.replace('.mak', '.log'))
    EXE_FILE_NAME = os.path.join(config.OUTPUT_DIRECTORY, 'bin', PRODUCT_FILE.replace('.mak','.exe'))
    PACKED_FILE_NAME = os.path.join(config.PACKED_DIRECTORY, MAKFILE_NAME.replace('.mak','.exe'))
    AV_BYPASS_FILE_NAME = os.path.join(os.path.normcase(config.AV_BYPASS_DIRECTORY), PRODUCT_NAME, MAKFILE_NAME.replace('.mak','.exe'))

    @classmethod
    def setUpClass(cls):
        super(TestStatMakefileExecutor, cls).setUpClass()
        generator = StatMakefileGenerator(cls.PRODUCT_FILE)
        generator.generate()

    @classmethod
    def tearDownClass(cls):
        os.remove(StatMakefileGenerator.AUTO_GENERATED_MAKEFILE)
        if os.path.isfile(cls.LOGFILE_NAME):
            os.remove(cls.LOGFILE_NAME)
        super(TestStatMakefileExecutor, cls).tearDownClass()

    def setUp(self):
        self.skipWindowsTest() # TODO: Fix these tests for Linux
        self.__subprocess = self.patch(self.CUT, 'subprocess')
        for directoryName in config.OUTPUT_SUB_DIRECTORIES:
            directoryPath = self.getOutputDirectoryPath(directoryName)
            if not os.path.exists(directoryPath):
                os.makedirs(directoryPath)
        if os.path.exists(config.AV_BYPASS_DIRECTORY):
            rmtree(config.AV_BYPASS_DIRECTORY)


    def tearDown(self):
        for directoryName in config.OUTPUT_SUB_DIRECTORIES:
            rmtree(self.getOutputDirectoryPath(directoryName), ignore_errors=True)
        if os.path.isdir(config.AV_BYPASS_DIRECTORY):
            rmtree(os.path.normcase(config.AV_BYPASS_DIRECTORY), ignore_errors=True)

    def test___init__basics(self):
        executor = StatMakefileExecutor(self.MAKFILE_NAME)
        self.assertIsInstance(executor._makfile, StatMakefile)
        self.assertIn('PROJECT_EXAMPLE', executor._makfile[StatMakefile.DEFINES].split())
        self.assertIsInstance(executor._logger, MakfileLogger)
        self.assertTrue(os.path.isfile(self.LOGFILE_NAME))
        self.assertFalse(executor._logger._isSilent)

    def test___init__silentLog(self):
        executor = StatMakefileExecutor(self.MAKFILE_NAME, beSilent = True)
        self.assertTrue(executor._logger._isSilent)

    def test_compile(self):
        outputLines = self._generateMocksToCoverExecutionFlow()

        executor = StatMakefileExecutor(self.MAKFILE_NAME, beSilent=True)
        executor.compile()
        del executor._logger

        command = ' '.join(['"{0}"'.format(vsTools.getMakeToolLocation()), vsTools.NMAKE_ARGUMENTS, self.MAKFILE_NAME])
        self._verifyExecution(command)
        self._verifyLogging(outputLines)

    def test_compileWithFailure(self):
        outputLines = self._generateMocksToCoverExecutionFlow(status=-1)

        executor = StatMakefileExecutor(self.MAKFILE_NAME, beSilent=True)
        try:
            executor.compile()
        except StatMakFileExecutorException as e:
            self.assertEqual(StatMakFileExecutorException.BUILD_FAILURE, e.message)
        else:
            self.fail("An exception is expected in this test!")
        finally:
            del executor._logger
        self._verifyLogging(outputLines)

    def test_run(self):
        outputLines = self._generateMocksToCoverExecutionFlow()
        self._emulateCompilation()

        executor = StatMakefileExecutor(self.MAKFILE_NAME, beSilent=True)
        executor.run()
        del executor._logger

        self._verifyExecution(self.AV_BYPASS_FILE_NAME)
        self._verifyLogging(outputLines)

    def test_runWithAntiVirusBypassVariations(self):
        self._emulateCompilation()

        executor = StatMakefileExecutor(self.MAKFILE_NAME, beSilent=True)

        self._generateMocksToCoverExecutionFlow()
        executor.run()
        self.assertTrue(os.path.isfile(self.AV_BYPASS_FILE_NAME))

        os.remove(self.AV_BYPASS_FILE_NAME)
        self._generateMocksToCoverExecutionFlow()
        executor.run()
        self.assertTrue(os.path.isfile(self.AV_BYPASS_FILE_NAME))

        osRemove = self.patch(self.CUT, 'remove')
        self._generateMocksToCoverExecutionFlow()
        executor.run()
        self.assertTrue(os.path.isfile(self.AV_BYPASS_FILE_NAME))
        osRemove.assert_called_once_with(self.AV_BYPASS_FILE_NAME)

    def test_runWithFailure(self):
        outputLines = self._generateMocksToCoverExecutionFlow(status=-1)
        self._emulateCompilation()

        executor = StatMakefileExecutor(self.MAKFILE_NAME, beSilent=True)

        try:
            executor.run()
        except StatMakFileExecutorException as e:
            self.assertEqual(StatMakFileExecutorException.EXECUTION_FAILURE, e.message)
        else:
            self.fail("An exception is expected in this test!")
        finally:
            del executor._logger
        self._verifyLogging(outputLines)

    def test_packExecutable(self):
        if os.path.isdir(config.PACKED_DIRECTORY):
            rmtree(config.PACKED_DIRECTORY)

        executor = StatMakefileExecutor(self.MAKFILE_NAME, beSilent=True)
        self._emulateCompilation()
        executor.pack()

        self.assertTrue(os.path.isfile(self.PACKED_FILE_NAME))

        extraFileInTargetFolder = self.PACKED_FILE_NAME.replace('.exe', '.com')
        os.rename(self.PACKED_FILE_NAME, extraFileInTargetFolder)
        executor.pack()

        self.assertTrue(os.path.isfile(self.PACKED_FILE_NAME))
        self.assertTrue(os.path.isfile(extraFileInTargetFolder))

        os.remove(self.EXE_FILE_NAME)
        rmtree(config.PACKED_DIRECTORY)

    def test_clear(self):
        self._emulateCompilation()
        patcher = self.patch(self.CUT, 'remove')
        patcher.side_effect = remove

        executor = StatMakefileExecutor(self.MAKFILE_NAME, beSilent=True)
        executor.clear()

        for directoryName in config.OUTPUT_SUB_DIRECTORIES:
            self.assertFalse(os.path.isdir(os.path.join(config.OUTPUT_DIRECTORY, directoryName)))
        calls = [call(os.path.join(config.OUTPUT_DIRECTORY, directory)) for directory in config.OUTPUT_SUB_DIRECTORIES]
        self.assertEqual(calls, patcher.call_args_list)

    def _generateMocksToCoverExecutionFlow(self, status = 0):
        outputLines = ['line text 1\n', 'line text 2\n', '', 'line text 3\n', '']
        self.__subprocess.Popen().stdout.readline.side_effect = outputLines
        self.__subprocess.Popen().poll.side_effect = [None, True]
        self.__subprocess.Popen().wait.return_value = status
        self.__subprocess.STDOUT = "__subprocess.STDOUT"
        self.__subprocess.PIPE = "__subprocess.PIPE"
        self.__subprocess.reset_mock()
        return outputLines

    def _verifyExecution(self, command):
        expected = \
            [call.Popen(command, shell=True, stderr='__subprocess.STDOUT', stdout='__subprocess.PIPE')] + \
            [call.Popen().stdout.readline()]*3 + [call.Popen().poll()] + [call.Popen().stdout.readline()]*2 + \
            [call.Popen().poll(), call.Popen().wait()]
        self.assertCalls(self.__subprocess, expected)

    def _verifyLogging(self, outputLines):
        loggedLines = [line for line in outputLines if line != '']
        resultFile = open(self.LOGFILE_NAME, 'r')
        readLines = resultFile.readlines()
        resultFile.close()
        self.assertEqual(loggedLines, readLines)

    def _emulateCompilation(self):
        productMakfile = os.path.join(config.PRODUCT_DIRECTORY, self.PRODUCT_FILE)
        copyfile(productMakfile, self.EXE_FILE_NAME)

        for filename in self._listFilesByExtension(directory='.', extension='.h'):
            copyfile(filename, os.path.join(self.getOutputDirectoryPath('inc'), filename))

        for filename in self._listFilesByExtension(directory='.', extension='.c'):
            copyfile(filename, os.path.join(self.getOutputDirectoryPath('obj'), filename.replace('.c', '.obj')))

    @staticmethod
    def _listFilesByExtension(directory, extension):
        return (filename for filename in os.listdir(directory) if os.path.isfile(filename) and os.path.splitext(filename)[1] == extension)

    @staticmethod
    def getOutputDirectoryPath(directoryName):
        return os.path.join(config.OUTPUT_DIRECTORY, directoryName)
