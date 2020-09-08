import sys
from multiprocessing import Pool, freeze_support
from time import sleep

import stat_attributes as attributes
from build_tools_crawler import BuildToolsCrawler
from ide_writer import IdeWorkspaceWriter
from msvs_ide_writer import MsvsWriter
from stat_main import StatMain, STAT_SUMMARY, STAT_OUTPUT_DELIMITER, STAT_SILENT_OUTPUT, StatException, \
    runTestPackage, MAKEFILE_CORRUPTION, StatWarning
from stat_makefile_generator import StatMakefileGenerator
from build_tools import BuildTools
from stat_configuration import StatConfiguration
from stat_argument_parser import StatArgumentParser
from tests_runner import TestsRunner, TestsRunnerException
from services import writeJsonFile, remove, mkdir
from tests.testing_tools import AdvancedTestCase, PropertyMock, call, Mock

CUT = StatMain.__module__

SINGLE_PRODUCT = 'single_product'
DEFAULT_PRODUCT = 'default_product'
TARGET_PRODUCT = 'target_product'
ALL_PRODUCT_FILES = {product: product + '.mak' for product in [SINGLE_PRODUCT, DEFAULT_PRODUCT, TARGET_PRODUCT]}
MANY_PRODUCTS = ALL_PRODUCT_FILES.keys()
MANY_PRODUCT_FILES = ALL_PRODUCT_FILES.values()

SINGLE_MAKE_FILE = "simple.mak"
MANY_MAKE_FILES = ['simplified_example.mak', SINGLE_MAKE_FILE, 'full_example.mak']
MANY_LOG_FILES = [filename[:-4] + '.log' for filename in MANY_MAKE_FILES]

COMPILATION_COMMAND = 'command to compile a makefile'

LOG_LINES = ['First line', 'second line', '3rd line']

FAKE_EXCEPTION_MESSAGE = 'This is exception emulator'
FAKE_SUCCESSFUL_RUNS = [(filename, 'PASSED', '') for filename in MANY_MAKE_FILES] * len(MANY_PRODUCTS)
FAKE_FAILED_RUNS = [(filename, 'FAILED', FAKE_EXCEPTION_MESSAGE) for filename in MANY_MAKE_FILES] * len(MANY_PRODUCTS)


class TestStatMainBase(AdvancedTestCase):
    def setupCommon(self):
        self.statMakefileGenerator = self.patch(CUT, StatMakefileGenerator.__name__)
        self.remove = self.patch(CUT, remove.__name__)
        self.mkdir = self.patch(CUT, mkdir.__name__)
        self.open = self.patchOpen()
        self.writeJsonFile = self.patch(CUT, writeJsonFile.__name__)
        self.ideWorkspaceWriter = self.patch(CUT, IdeWorkspaceWriter.__name__, autospec=True)

        self.tools = Mock(spec=BuildTools)
        self.tools.getCommandToCompile.return_value = COMPILATION_COMMAND
        toolsCrawler = self.patch(CUT, BuildToolsCrawler.__name__)
        toolsCrawler.return_value.retrieve.return_value = self.tools

        self.statConfiguration = self.patch(CUT, StatConfiguration.__name__, autospec=True)
        configuration = self.statConfiguration.return_value
        type(configuration).defaultProduct = PropertyMock(return_value=DEFAULT_PRODUCT)
        type(configuration).products = PropertyMock(return_value=MANY_PRODUCTS)
        configuration.isStale.return_value = True

    def _patchArgumentParser(self, targetProducts, userMakefiles, processes=0):
        self.statArgumentParser = self.patch(CUT, StatArgumentParser.__name__, autospec=True)
        parser = self.statArgumentParser.return_value
        type(parser).targetProducts = PropertyMock(return_value=targetProducts)
        type(parser).makeFiles = PropertyMock(return_value=userMakefiles)
        type(parser).processes = PropertyMock(return_value=processes)
        self.redundantArguments = PropertyMock(return_value=None)
        type(parser).redundant = self.redundantArguments
        return parser

    def _mockParserResults(self, ide=None, shallExecute=True, shallBeVerbose=True, cleaningLevel=0):
        parser = self.statArgumentParser.return_value
        parser.ide = ide
        shallCompile = ide is None
        parser.shallBuild.return_value = shallCompile
        parser.shallRun.return_value = shallCompile and shallExecute
        parser.shallBeVerbose.return_value = shallCompile and shallBeVerbose
        parser.getRequestedCleaningLevel.return_value = cleaningLevel


class TestStatMain(TestStatMainBase):

    def setUp(self):
        self.setupCommon()
        self.runTestPackage = self.patch(CUT, runTestPackage.__name__, side_effect=FAKE_SUCCESSFUL_RUNS)

    def test_run_withNoArgumentsForSingleTarget(self):
        self._patchArgumentParser(targetProducts=[DEFAULT_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()

        StatMain.run()

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(None)])
        self.assertCalls(self.remove, [call(attributes.LOGS_DIRECTORY)])
        self.assertCalls(self.mkdir, [call('logs'), call('output', exist_ok=True)])
        self.assertCalls(self.open, [])

        expected = [call(ALL_PRODUCT_FILES[DEFAULT_PRODUCT]), call().generate()]
        self.assertCalls(self.statMakefileGenerator, expected)

        expected = [call(makeFile, COMPILATION_COMMAND, True, True) for makeFile in MANY_MAKE_FILES]
        self.assertCalls(self.runTestPackage, expected)

        expected = {makeFile: {"Status": "PASSED", "Info": ""} for makeFile in MANY_MAKE_FILES}
        self.assertCalls(self.writeJsonFile, [call(attributes.REPORT_FILENAME, {DEFAULT_PRODUCT: expected})])

    def test_run_withNoArgumentsForManyTargets(self):
        self._patchArgumentParser(targetProducts=MANY_PRODUCTS, userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()

        StatMain.run()

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(None)])

        expected = \
            [item for product in MANY_PRODUCTS for item in [call(ALL_PRODUCT_FILES[product]), call().generate()]]
        self.assertCalls(self.statMakefileGenerator, expected)

        expected = \
            [call(makeFile, COMPILATION_COMMAND, True, True) for makeFile in MANY_MAKE_FILES] * len(MANY_PRODUCT_FILES)
        self.assertCalls(self.runTestPackage, expected)

        expected = {makeFile: {"Status": "PASSED", "Info": ""} for makeFile in MANY_MAKE_FILES}
        expected = {product: expected for product in MANY_PRODUCTS}
        self.assertCalls(self.writeJsonFile, [call(attributes.REPORT_FILENAME, expected)])

    def test_run_withAllTargets(self):
        self._patchArgumentParser(targetProducts=MANY_PRODUCTS, userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()
        self.statConfiguration.return_value.isStale.return_value = False

        StatMain.run(['-a'])

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(['-a'])])

        expected = [item for product in MANY_PRODUCTS for item in [call(ALL_PRODUCT_FILES[product]), call().generate()]]
        self.assertCalls(self.statMakefileGenerator, expected)

        expected = \
            [call(makeFile, COMPILATION_COMMAND, True, True) for makeFile in MANY_MAKE_FILES] * len(MANY_PRODUCT_FILES)
        self.assertCalls(self.runTestPackage, expected)

    def test_run_withCompileOnlyArguments(self):
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults(shallExecute=False)

        StatMain.run(['-b'])

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(['-b'])])
        expected = [call(makeFile, COMPILATION_COMMAND, False, True) for makeFile in MANY_MAKE_FILES]
        self.assertCalls(self.runTestPackage, expected)

    def test_run_withSingleLevelOfCleaning(self):
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults(shallExecute=False, cleaningLevel=1)

        StatMain.run(['-b', '-c'])

        expectedCommandLine = COMPILATION_COMMAND + ' ' + attributes.REBUILD_TARGET
        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(['-b', '-c'])])
        expected = [call(makeFile, expectedCommandLine, False, True) for makeFile in MANY_MAKE_FILES]
        self.assertCalls(self.runTestPackage, expected)

    def test_run_withDoubleLevelOfCleaning(self):
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults(shallExecute=False, cleaningLevel=2)

        StatMain.run(['-b', '-cc'])

        expectedCommandLine = COMPILATION_COMMAND + ' clean' + ' ' + attributes.REBUILD_TARGET
        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(['-b', '-cc'])])
        expected = [call(makeFile, expectedCommandLine, False, True) for makeFile in MANY_MAKE_FILES]
        self.assertCalls(self.runTestPackage, expected)

    def test_run_withSilentArguments(self):
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults(shallBeVerbose=False)
        printMock = self.patchBuiltinObject('print')

        StatMain.run(['-s'])

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(['-s'])])
        expected = [call(makeFile, COMPILATION_COMMAND, True, False) for makeFile in MANY_MAKE_FILES]
        self.assertCalls(self.runTestPackage, expected)
        count = len(MANY_MAKE_FILES)
        expected = [call(STAT_SILENT_OUTPUT.format(makeFile, 'PASSED')) for makeFile in MANY_MAKE_FILES] + \
                   [call(STAT_OUTPUT_DELIMITER), call(STAT_SUMMARY.format(total=count, passed=count, failed=0))]
        self.assertCalls(printMock, expected)

    def test_run_withRedundantArguments(self):
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults(shallExecute=False)
        self.redundantArguments.return_value = ['-run', '--redundant']

        try:
            StatMain.run(['-b'])
        except StatWarning:
            pass
        else:
            self.fail("The framework shall fire a STAT Warning.")

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(['-b'])])
        expected = [call(makeFile, COMPILATION_COMMAND, False, True) for makeFile in MANY_MAKE_FILES]
        self.assertCalls(self.runTestPackage, expected)

    def test_run_withException(self):
        self.runTestPackage.side_effect = FAKE_FAILED_RUNS
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()
        printMock = self.patchBuiltinObject('print')

        try:
            StatMain.run()
        except StatException:
            pass
        else:
            self.fail("The framework shall fire a STAT Exception.")

        expected = [call(makeFile, COMPILATION_COMMAND, True, True) for makeFile in MANY_MAKE_FILES]
        self.assertCalls(self.runTestPackage, expected)

        self.assertCalls(self.remove, [call(attributes.LOGS_DIRECTORY)])
        self.assertCalls(self.mkdir,
                         [call(attributes.LOGS_DIRECTORY), call(attributes.OUTPUT_DIRECTORY, exist_ok=True)])

        expected = {makeFile: {"Status": "FAILED", "Info": FAKE_EXCEPTION_MESSAGE} for makeFile in MANY_MAKE_FILES}
        self.assertCalls(self.writeJsonFile, [call(attributes.REPORT_FILENAME, {TARGET_PRODUCT: expected})])

        count = len(MANY_MAKE_FILES)
        expected = [call(STAT_OUTPUT_DELIMITER), call(STAT_SUMMARY.format(total=count, passed=0, failed=count))]
        self.assertCalls(printMock, expected)

    def test_run_withNonStaleConfigurationSameProduct(self):
        self.statConfiguration.return_value.isStale.return_value = False
        self._patchArgumentParser(targetProducts=[DEFAULT_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()

        StatMain.run()

        self.assertCalls(self.statMakefileGenerator, [])
        expected = [call(makeFile, COMPILATION_COMMAND, True, True) for makeFile in MANY_MAKE_FILES]
        self.assertCalls(self.runTestPackage, expected)

    def test_run_withNonStaleConfigurationAnotherProduct(self):
        self.statConfiguration.return_value.isStale.return_value = False
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()
        arguments = ['-p', DEFAULT_PRODUCT]

        StatMain.run(arguments)

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(arguments)])
        self.assertCalls(self.statMakefileGenerator, [call(ALL_PRODUCT_FILES[TARGET_PRODUCT]), call().generate()])
        expected = [call(makeFile, COMPILATION_COMMAND, True, True) for makeFile in MANY_MAKE_FILES]
        self.assertCalls(self.runTestPackage, expected)

    def test_run_uponVisualStudioRequest(self):
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=[SINGLE_MAKE_FILE])
        self._mockParserResults(MsvsWriter.IDE)

        StatMain.run(['-vs'])

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(['-vs'])])
        self.assertCalls(self.statMakefileGenerator, [call(ALL_PRODUCT_FILES[TARGET_PRODUCT]), call().generate()])
        self.assertCalls(self.runTestPackage, [])
        self.assertCalls(self.ideWorkspaceWriter, [call(MsvsWriter.IDE, SINGLE_MAKE_FILE), call().write()])


TEST_INFO_FORMAT = 'cmd:"{0}"; run:"{1}"; verbose:"{2}"'


def runFake(makefile, commandToCompile, shallRun, shallBeVerbose):
    sleep(0.5)
    return makefile, 'PASSED', TEST_INFO_FORMAT.format(commandToCompile, shallRun, shallBeVerbose)


class TestStatMainGear(TestStatMainBase):

    def setUp(self):
        self.setupCommon()
        self.runTestPackage = self.patch(CUT, runTestPackage.__name__, new=runFake)

        # Workaround to patch a bug in forking system of multiprocessing module in Python < 3
        self.old_main = sys.modules["__main__"]
        self.old_main_file = sys.modules["__main__"].__file__
        sys.modules["__main__"] = sys.modules[__name__]
        sys.modules["__main__"].__file__ = sys.modules[__name__].__file__

    def tearDown(self):

        sys.modules["__main__"] = self.old_main
        sys.modules["__main__"].__file__ = self.old_main_file

    def test_run_uponGearBoost(self):
        if sys.version_info >= (3, 0):
            self.skipTest("Multiprocessing can't work in an interactive environment under Python 3+.")
        expectedCores = 8
        receivedCores = []

        def spyPool(cores, *args, **kwargs):
            receivedCores.append(cores)
            return Pool(cores, *args, **kwargs)

        self._patchArgumentParser(targetProducts=MANY_PRODUCTS, userMakefiles=MANY_MAKE_FILES, processes=expectedCores)
        self._mockParserResults(shallBeVerbose=False)
        self.patch(CUT, Pool.__name__, new=spyPool)

        StatMain.run(['-g'])

        self.assertEqual([expectedCores]*len(MANY_PRODUCTS), receivedCores)

        expected = {makeFile: {"Status": "PASSED", "Info": TEST_INFO_FORMAT.format(COMPILATION_COMMAND, True, False)}
                    for makeFile in MANY_MAKE_FILES}
        expected = {product: expected for product in MANY_PRODUCTS}
        self.assertCalls(self.writeJsonFile, [call(attributes.REPORT_FILENAME, expected)])


class TestRunTestPackage(AdvancedTestCase):

    def setUp(self):
        self.testsRunner = self.patch(CUT, TestsRunner.__name__, autospec=True)

    def test_runTestPackage_fullTestRun(self):
        results = runTestPackage(SINGLE_MAKE_FILE, COMPILATION_COMMAND, shallRun=True, shallBeVerbose=True)

        expected = [call(SINGLE_MAKE_FILE, COMPILATION_COMMAND, True), call().compile(), call().run()]
        self.assertCalls(self.testsRunner, expected)
        self.assertEqual((SINGLE_MAKE_FILE, 'PASSED', ''), results)

    def test_runTestPackage_compileOnly(self):
        results = runTestPackage(SINGLE_MAKE_FILE, COMPILATION_COMMAND, shallRun=False, shallBeVerbose=True)

        expected = [call(SINGLE_MAKE_FILE, COMPILATION_COMMAND, True), call().compile()]
        self.assertCalls(self.testsRunner, expected)
        self.assertEqual((SINGLE_MAKE_FILE, 'PASSED', ''), results)

    def test_runTestPackage_withSilentArguments(self):
        results = runTestPackage(SINGLE_MAKE_FILE, COMPILATION_COMMAND, shallRun=True, shallBeVerbose=False)

        expected = [call(SINGLE_MAKE_FILE, COMPILATION_COMMAND, False), call().compile(), call().run()]
        self.assertCalls(self.testsRunner, expected)
        self.assertEqual((SINGLE_MAKE_FILE, 'PASSED', ''), results)

    def test_runTestPackage_withTestException(self):
        exception = "Fake exception to test error-handling"

        def fakeRunMethod():
            raise TestsRunnerException(exception)

        self.testsRunner.return_value.run.side_effect = fakeRunMethod

        results = runTestPackage(SINGLE_MAKE_FILE, COMPILATION_COMMAND, shallRun=True, shallBeVerbose=True)

        expected = [call(SINGLE_MAKE_FILE, COMPILATION_COMMAND, True),
                    call().compile(), call().run(), call().writeLog(exception)]
        self.assertCalls(self.testsRunner, expected)
        self.assertEqual((SINGLE_MAKE_FILE, 'FAILED', exception), results)

    def test_runTestPackage_withAbnormalTestException(self):
        exception = "This is abnormal exception emulation"

        def fakeRunMethod():
            raise Exception(exception)

        self.testsRunner.return_value.run.side_effect = fakeRunMethod

        results = runTestPackage(SINGLE_MAKE_FILE, COMPILATION_COMMAND, shallRun=True, shallBeVerbose=True)

        expected = [call(SINGLE_MAKE_FILE, COMPILATION_COMMAND, True),
                    call().compile(), call().run(), call().writeLog(exception)]
        self.assertCalls(self.testsRunner, expected)
        self.assertEqual((SINGLE_MAKE_FILE, 'CRASHED', exception), results)

    def test_runTestPackage_withExceptionUponInitialization(self):
        exception = Exception("This is an emulation of exception upon makefile processing")

        def initFakeRunner(*args, **kwargs):
            raise exception

        self.testsRunner.side_effect = initFakeRunner

        results = runTestPackage(SINGLE_MAKE_FILE, COMPILATION_COMMAND, shallRun=True, shallBeVerbose=True)

        expected = [call(SINGLE_MAKE_FILE, COMPILATION_COMMAND, True)]
        self.assertCalls(self.testsRunner, expected)
        self.assertEqual((SINGLE_MAKE_FILE, 'CRASHED',
                          MAKEFILE_CORRUPTION.format(filename=SINGLE_MAKE_FILE, exception=str(exception))), results)


if __name__ == '__main__':
    freeze_support()
