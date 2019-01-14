import os

from mock import Mock, call

import stat_attributes as attributes
from services import execute, remove
from stat_configuration import StatConfiguration
from stat_makefile import StatMakefile
from testing_tools import AdvancedTestCase, FileBasedTestCase
from tests_runner import TestsRunner, TestsRunnerException
from vs_tools import StatToolchain

CUT = TestsRunner.__module__

TEST_COMPILATION_CMD_PATTERN = '<command of "{0}"-compilation>'
TEST_MAKEFILE_NAME = 'simple.mak'
TEST_PACKAGE_NAME = TEST_MAKEFILE_NAME[:-4]

class TestTestsRunner(FileBasedTestCase):

    def setUp(self):
        self.makefile = StatMakefile(TEST_MAKEFILE_NAME)
        self.remove = self.patch(CUT, remove.__name__, return_value=False)
        self.execute = self.patch(CUT, execute.__name__, return_value=(0, []))

        self.toolchain = Mock(spec=StatToolchain)
        def  getCompilationCommand(makefile):
            return TEST_COMPILATION_CMD_PATTERN.format(makefile)
        self.toolchain.getCompilationCommand.side_effect = getCompilationCommand

        self.statConfiguration = self.patch(CUT, StatConfiguration.__name__, autospec=True)
        statConfiguration = self.statConfiguration.return_value # type: StatConfiguration
        statConfiguration.getToolchain.return_value = self.toolchain

    def test_cleanup(self):
        TestsRunner(TEST_MAKEFILE_NAME)
        self.assertCalls(self.remove, [call(os.path.join(attributes.OUTPUT_DIRECTORY, TEST_PACKAGE_NAME, directory))
                                       for directory in attributes.OUTPUT_SUB_DIRECTORIES])

    def test_compile(self):
        runner = TestsRunner(TEST_MAKEFILE_NAME)
        runner.compile()

        expectedEnv = dict(os.environ, PRIVATE_NAME=self.makefile.name)
        self.assertCalls(self.execute,[call(TEST_COMPILATION_CMD_PATTERN.format(TEST_MAKEFILE_NAME),
                                            beSilent=False, env=expectedEnv)])

    def test_run(self):
        runner = TestsRunner(TEST_MAKEFILE_NAME)
        runner.run()

        execPath = os.path.join(attributes.OUTPUT_DIRECTORY, TEST_PACKAGE_NAME, 'bin', self.makefile[StatMakefile.EXEC])
        self.assertCalls(self.execute, [call(execPath, beSilent=False)])

    def test_get_log(self):
        self.execute.side_effect = [(0, ['compile-1', 'compile-2']), (0, ['run-1', 'run-2', 'run-3'])]
        expected = ['compile-1', 'compile-2', 'run-1', 'run-2',  'run-3']

        runner = TestsRunner(TEST_MAKEFILE_NAME)
        runner.compile()
        runner.run()

        self.assertEqual(expected, runner.getLog())

    def test_silent(self):
        runner = TestsRunner(TEST_MAKEFILE_NAME, isVerbose=False)
        runner.compile()
        runner.run()

        expectedEnv = dict(os.environ, PRIVATE_NAME=self.makefile.name)
        execPath = os.path.join(attributes.OUTPUT_DIRECTORY, TEST_PACKAGE_NAME, 'bin', self.makefile[StatMakefile.EXEC])
        expected = [
            call(TEST_COMPILATION_CMD_PATTERN.format(TEST_MAKEFILE_NAME), beSilent=True, env=expectedEnv),
            call(execPath, beSilent=True)
        ]
        self.assertCalls(self.execute, expected)

    def test_compile_uponFailure(self):
        self.execute.return_value = (11, ['output of compilation execution'])

        runner = TestsRunner(TEST_MAKEFILE_NAME)

        try:
            runner.compile()
        except TestsRunnerException as e:
            self.assertEqual(['output of compilation execution'], runner.getLog())
        else:
            self.fail('The code was supposed to fire an exception!')

    def test_run_uponFailure(self):
        self.execute.return_value = (17, ['output of execution run'])

        runner = TestsRunner(TEST_MAKEFILE_NAME)

        try:
            runner.run()
        except TestsRunnerException as e:
            self.assertEqual(['output of execution run'], runner.getLog())
        else:
            self.fail('The code was supposed to fire an exception!')

