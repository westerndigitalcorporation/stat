from mock import PropertyMock, call, Mock

import stat_attributes as attributes
from ide_writer import IdeWorkspaceWriter
from msvs_ide_writer import MsvsWriter
from stat_main import StatMain, STAT_RESULT_SUMMARY, STAT_RESULT_DELIMITER, STAT_SILENT_OUTPUT, StatException
from stat_makefile_generator import StatMakefileGenerator
from testing_tools import AdvancedTestCase
from stat_configuration import StatConfiguration
from stat_argument_parser import StatArgumentParser
from tests_runner import TestsRunner, TestsRunnerException
from vs_tools import MsvsTools
from services import writeJsonFile, remove, mkdir

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

LOG_LINES = ['First line', 'second line', '3rd line']

FAKE_MSVS_TOOLS = Mock(spec=MsvsTools)


class TestStatMain(AdvancedTestCase):

    def setUp(self):
        self.statMakefileGenerator = self.patch(CUT, StatMakefileGenerator.__name__)
        self.remove = self.patch(CUT, remove.__name__)
        self.mkdir = self.patch(CUT, mkdir.__name__)
        self.testsRunner = self.patch(CUT, TestsRunner.__name__, autospec=True)
        self.testsRunner.return_value.getLog.return_value = LOG_LINES
        self.open = self.patchOpen()
        self.writeJsonFile = self.patch(CUT, writeJsonFile.__name__)
        self.ideWorkspaceWriter = self.patch(CUT, IdeWorkspaceWriter.__name__, autospec=True)

        self.statConfiguration = self.patch(CUT, StatConfiguration.__name__, autospec=True)
        configuration = self.statConfiguration.return_value
        type(configuration).defaultProduct = PropertyMock(return_value=DEFAULT_PRODUCT)
        type(configuration).products = PropertyMock(return_value=MANY_PRODUCTS)
        configuration.isStale.return_value = True


    def _patchArgumentParser(self, targetProducts, userMakefiles):
        self.statArgumentParser = self.patch(CUT, StatArgumentParser.__name__, autospec=True)
        parser = self.statArgumentParser.return_value
        type(parser).targetProducts = PropertyMock(return_value=targetProducts)
        type(parser).makeFiles = PropertyMock(return_value=userMakefiles)
        return parser

    def _mockParserResults(self, ide=None, shallExecute=True, shallBeVerbose=True):
        parser = self.statArgumentParser.return_value
        parser.ide = ide
        shallCompile = ide is None
        parser.shallCompile.return_value = shallCompile
        parser.shallRun.return_value = shallCompile and shallExecute
        parser.shallBeVerbose.return_value = shallCompile and shallBeVerbose

    def test_run_withNoArgumentsForSingleTarget(self):
        self._patchArgumentParser(targetProducts=[DEFAULT_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()

        StatMain.run()

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(None)])
        self.assertCalls(self.remove, [call(attributes.LOGS_DIRECTORY)])
        self.assertCalls(self.mkdir, [])
        self.assertCalls(self.open, [])

        expected = [call(ALL_PRODUCT_FILES[DEFAULT_PRODUCT]), call().generate()]
        self.assertCalls(self.statMakefileGenerator, expected)

        expected = [item for makeFile in MANY_MAKE_FILES for item in
                    [call(makeFile, True), call().compile(), call().run()]
                    ]
        self.assertCalls(self.testsRunner, expected)

        expected = {makeFile: {"Status": "PASSED", "Info": ""} for makeFile in MANY_MAKE_FILES}
        self.assertCalls(self.writeJsonFile, [call(attributes.REPORT_FILENAME, {DEFAULT_PRODUCT: expected})])

    def test_run_withNoArgumentsForManyTargets(self):
        self._patchArgumentParser(targetProducts=MANY_PRODUCTS, userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()

        StatMain.run()

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(None)])

        expected = [item for product in MANY_PRODUCTS for item in  [call(ALL_PRODUCT_FILES[product]), call().generate()]]
        self.assertCalls(self.statMakefileGenerator, expected)

        expected = [item for makeFile in MANY_MAKE_FILES for item in
                    [call(makeFile, True), call().compile(), call().run()]
                    ] * len(MANY_PRODUCT_FILES)
        self.assertCalls(self.testsRunner, expected)

        expected = {makeFile: {"Status": "PASSED", "Info": ""} for makeFile in MANY_MAKE_FILES}
        expected = {product: expected for product in MANY_PRODUCTS}
        self.assertCalls(self.writeJsonFile, [call(attributes.REPORT_FILENAME, expected)])

    def test_run_withAllTargets(self):
        self._patchArgumentParser(targetProducts=MANY_PRODUCTS, userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()
        self.statConfiguration.return_value.isStale.return_value = False

        StatMain.run(['-a'])

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(['-a'])])

        expected = [item for product in MANY_PRODUCTS for item in  [call(ALL_PRODUCT_FILES[product]), call().generate()]]
        self.assertCalls(self.statMakefileGenerator, expected)

        expected = [item for makeFile in MANY_MAKE_FILES for item in
                    [call(makeFile, True), call().compile(), call().run()]
                    ] * len(MANY_PRODUCT_FILES)
        self.assertCalls(self.testsRunner, expected)


    def test_run_withCompileOnlyArguments(self):
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults(shallExecute=False)

        StatMain.run(['-c'])

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(['-c'])])
        expected = [item for makeFile in MANY_MAKE_FILES for item in
                    [call(makeFile, True), call().compile()]
                    ]
        self.assertCalls(self.testsRunner, expected)

    def test_run_withSilentArguments(self):
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults(shallBeVerbose=False)
        printMock = self.patchBuiltinObject('print')

        StatMain.run(['-s'])

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(['-s'])])
        expected = [item for makeFile in MANY_MAKE_FILES for item in
                    [call(makeFile, False), call().compile(), call().run()]
                    ]
        self.assertCalls(self.testsRunner, expected)
        count = len(MANY_MAKE_FILES)
        expected = [call(STAT_SILENT_OUTPUT.format(makeFile, 'PASSED')) for makeFile in MANY_MAKE_FILES] + \
                   [call(STAT_RESULT_DELIMITER), call(STAT_RESULT_SUMMARY.format(total=count, passed=count, failed=0))]
        self.assertCalls(printMock, expected)

    def test_run_withTestException(self):
        ERROR_MESSAGE = "Fake exception to test error-handling"
        def fakeRunMethod():
            raise TestsRunnerException(ERROR_MESSAGE)
        self.testsRunner.return_value.run.side_effect = fakeRunMethod
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()
        printMock = self.patchBuiltinObject('print')

        try:
            StatMain.run()
        except StatException as e:
            pass
        else:
            self.fail("The framework shall fire system error.")

        count = len(MANY_MAKE_FILES)
        self.assertCalls(self.remove, [call(attributes.LOGS_DIRECTORY)])
        self.assertCalls(self.mkdir, [call(attributes.LOGS_DIRECTORY, exist_ok=True)]*count)

        expected = [item for logFile in MANY_LOG_FILES for item in
                    [call('/'.join([attributes.LOGS_DIRECTORY, logFile]), 'w'),
                     call().__enter__(),
                     call().writelines(LOG_LINES),
                     call().__exit__(None, None, None)]]
        self.assertCalls(self.open, expected)

        expected = {makeFile: {"Status": "FAILED", "Info": ERROR_MESSAGE} for makeFile in MANY_MAKE_FILES}
        self.assertCalls(self.writeJsonFile, [call(attributes.REPORT_FILENAME, {TARGET_PRODUCT: expected})])

        expected = [call(STAT_RESULT_DELIMITER), call(STAT_RESULT_SUMMARY.format(total=count, passed=0, failed=count))]
        self.assertCalls(printMock, expected)

    def test_run_withAbnormalTestException(self):
        exception = Exception("This is abnormal exception emulation")
        def fakeRunMethod():
            raise exception
        self.testsRunner.return_value.run.side_effect = fakeRunMethod
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()
        printMock = self.patchBuiltinObject('print')

        try:
            StatMain.run()
        except StatException as e:
            pass
        else:
            self.fail("The framework shall fire system error.")

        count = len(MANY_MAKE_FILES)
        self.assertCalls(self.remove, [call(attributes.LOGS_DIRECTORY)])
        self.assertCalls(self.mkdir, [])
        self.assertCalls(self.open, [])

        expected = {makeFile: {"Status": "CRASHED", "Info": str(exception)} for makeFile in MANY_MAKE_FILES}
        self.assertCalls(self.writeJsonFile, [call(attributes.REPORT_FILENAME, {TARGET_PRODUCT: expected})])

        expected = [call(STAT_RESULT_DELIMITER), call(STAT_RESULT_SUMMARY.format(total=count, passed=0, failed=count))]
        self.assertCalls(printMock, expected)

    def test_run_withNonStaleConfigurationSameProduct(self):
        self.statConfiguration.return_value.isStale.return_value = False
        self._patchArgumentParser(targetProducts=[DEFAULT_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()

        StatMain.run()

        self.assertCalls(self.statMakefileGenerator, [])

        expected = [item for makeFile in MANY_MAKE_FILES for item in
                    [call(makeFile, True), call().compile(), call().run()]
                    ]
        self.assertCalls(self.testsRunner, expected)

    def test_run_withNonStaleConfigurationAnotherProduct(self):
        self.statConfiguration.return_value.isStale.return_value = False
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=MANY_MAKE_FILES)
        self._mockParserResults()

        arguments = ['-p', DEFAULT_PRODUCT]
        StatMain.run(arguments)

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(arguments)])
        self.assertCalls(self.statMakefileGenerator, [call(ALL_PRODUCT_FILES[TARGET_PRODUCT]), call().generate()])

        expected = [item for makeFile in MANY_MAKE_FILES for item in
                    [call(makeFile, True), call().compile(), call().run()]
                    ]
        self.assertCalls(self.testsRunner, expected)

    def test_run_uponVisualStudioRequest(self):
        self._patchArgumentParser(targetProducts=[TARGET_PRODUCT], userMakefiles=[SINGLE_MAKE_FILE])
        self._mockParserResults(MsvsWriter.IDE)

        StatMain.run(['-vs'])

        self.statArgumentParser.assert_has_calls([call(MANY_PRODUCTS, DEFAULT_PRODUCT), call().parse(['-vs'])])
        self.assertCalls(self.statMakefileGenerator, [call(ALL_PRODUCT_FILES[TARGET_PRODUCT]), call().generate()])
        self.assertCalls(self.testsRunner, [])
        self.assertCalls(self.ideWorkspaceWriter, [call(MsvsWriter.IDE, SINGLE_MAKE_FILE), call().write()])