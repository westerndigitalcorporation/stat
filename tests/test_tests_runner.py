import os

import stat_attributes as attributes
from services import execute, remove, formatMakeCommand
from stat_makefile import StatMakefile
from tests_runner import TestsRunner, TestsRunnerException
from tests.testing_tools import FileBasedTestCase, call

CUT = TestsRunner.__module__

TEST_MAKE_ARGUMENTS = ['clean', 'build']
TEST_MAKEFILE_NAME = 'simple.mak'
TEST_PACKAGE_NAME = TEST_MAKEFILE_NAME[:-4]
TEST_LOGFILE_NAME = TEST_PACKAGE_NAME + '.log'
TEST_ENVIRONMENT_MOCK = dict(user='Arseniy Aharonov', path='/the/right/way', encoding='UTF-8')


def createRunner(isVerbose=True):
    return TestsRunner(TEST_MAKEFILE_NAME, TEST_MAKE_ARGUMENTS, isVerbose)


def formatMakeCommandFake(filename, args):
    return filename + ":" + ",".join(args)


class TestTestsRunner(FileBasedTestCase):

    def setUp(self):
        self.makefile = StatMakefile(TEST_MAKEFILE_NAME)
        self.execute = self.patch(CUT, execute.__name__, return_value=(0, []))
        self.patch(CUT, 'os.environ', new=TEST_ENVIRONMENT_MOCK)
        self.patch(CUT, formatMakeCommand.__name__, side_effect=formatMakeCommandFake)
        self.expectedCommand = formatMakeCommandFake(TEST_MAKEFILE_NAME, TEST_MAKE_ARGUMENTS)

    def test_compile(self):
        runner = createRunner()
        runner.compile()

        expectedEnv = dict(TEST_ENVIRONMENT_MOCK, STAT_NAMESPACE=self.makefile.name)
        self.assertCalls(self.execute, [call(self.expectedCommand, beSilent=False, env=expectedEnv)])

    def test_run(self):
        runner = createRunner()
        runner.run()

        execPath = os.path.join(attributes.OUTPUT_DIRECTORY, TEST_PACKAGE_NAME, 'bin', self.makefile[StatMakefile.EXEC])
        self.assertCalls(self.execute, [call(execPath, beSilent=False)])

    def test_get_log(self):
        self.execute.side_effect = [(0, ['compile-1', 'compile-2']), (0, ['run-1', 'run-2', 'run-3'])]
        expected = ['compile-1', 'compile-2', 'run-1', 'run-2',  'run-3']

        runner = createRunner()
        runner.compile()
        runner.run()

        self.assertEqual(expected, runner.getLog())

    def test_silent(self):
        runner = createRunner(isVerbose=False)
        runner.compile()
        runner.run()

        expectedEnv = dict(TEST_ENVIRONMENT_MOCK, STAT_NAMESPACE=self.makefile.name)
        execPath = os.path.join(attributes.OUTPUT_DIRECTORY, TEST_PACKAGE_NAME, 'bin', self.makefile[StatMakefile.EXEC])
        expected = [call(self.expectedCommand, beSilent=True, env=expectedEnv), call(execPath, beSilent=True)]
        self.assertCalls(self.execute, expected)

    def test_compile_uponFailure(self):
        self.execute.return_value = (11, ['output of compilation execution'])

        runner = createRunner()

        try:
            runner.compile()
        except TestsRunnerException:
            self.assertEqual(['output of compilation execution'], runner.getLog())
        else:
            self.fail('The code was supposed to fire an exception!')

    def test_run_uponFailure(self):
        self.execute.return_value = (17, ['output of execution run'])

        runner = createRunner()

        try:
            runner.run()
        except TestsRunnerException:
            self.assertEqual([
                'output of execution run',
                'The executable of package "{0}" failed with error-code 0X11.\n'.format(TEST_MAKEFILE_NAME)],
                runner.getLog())
        else:
            self.fail('The code was supposed to fire an exception!')

    def test_writeLog(self):
        executeResults = [(0, ['compile-1', 'compile-2']), (0, ['run-1', 'run-2', 'run-3'])]
        expectedPrintOut = [line for results in executeResults for line in results[1]]
        exceptionExtraInfo = "ERROR: Some extra information"
        self.execute.side_effect = executeResults
        runner = createRunner()
        runner.compile()
        runner.run()
        openMock = self.patchOpen()

        runner.writeLog(exceptionExtraInfo)

        expected = [call('/'.join([attributes.LOGS_DIRECTORY, TEST_LOGFILE_NAME]), 'a'),
                    call().__enter__(),
                    call().writelines(expectedPrintOut),
                    call().write(exceptionExtraInfo),
                    call().__exit__(None, None, None)]
        self.assertCalls(openMock, expected)
