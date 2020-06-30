#!/usr/bin/env python
from services import executeForOutput
from vs_tools import VsToolsException, MsvsTools, NMAKE_ARGUMENTS
from tests.testing_tools import *  # pylint: disable=unused-wildcard-import

CUT = MsvsTools.__module__

USER_MAKE_FILE = "simple.mak"
EXPECTED_TOOL = '/c/vs/best/tools'
EXPECTED_PATH = 'tool-chain-path'
EMULATED_OS_ENVIRON = \
    {'VS90COMNTOOLS': '/c/vs/oldest/tools', 'VS130COMNTOOLS': EXPECTED_TOOL, 'VS120COMNTOOLS': '/c/vs/medium/tools', }

VSWHERE_BASE_PATH = os.path.join(attributes.TOOL_PATH, attributes.RESOURCES_DIRECTORY)
VSWHERE_COMMAND_LINE = VSWHERE_BASE_PATH + "\\vswhere.exe -legacy {0} -property installationPath -latest"
TOOLS_BASE_PATH_MOCK = "./test/tools/path"
TOOLS_FULL_PATH_MOCK = os.path.join(TOOLS_BASE_PATH_MOCK, "Common7", "Tools")
VS_DEV_BATCH_MOCK = os.path.join(TOOLS_FULL_PATH_MOCK, "VsDevCmd.bat")
VS_DEV_BATCH_MOCK_OLDER = os.path.join(TOOLS_FULL_PATH_MOCK, "vsvars32.bat")
DUMMY_ENVIRONMENT = {'VS{0}0COMNTOOLS'.format(version): TOOLS_FULL_PATH_MOCK
                     for version in (8, 9, 10, 11, 12, 14, 15, 16)}


class TestMsvsTools(AdvancedTestCase):

    def tearDown(self):
        MsvsTools.reset()

    def test_find_byEnvironment(self):
        expected = '/c/vs_tools'
        expectedOther = '/c/vs_tools_other'
        self.patch(CUT, 'os.environ', {'VS90COMNTOOLS': expected, 'VS110COMNTOOLS': expectedOther})
        tools = MsvsTools.find(2008)
        self.assertEqual(expected, tools.path)
        tools = MsvsTools.find(2012)
        self.assertEqual(expectedOther, tools.path)
        self.assertEqual(expectedOther, tools.path)

    def test_find_byVsWhere(self):
        expected = '/c/vs_tools/VsWhere'
        expectedOther = '/c/vs_tools/other/VsWhere'
        executeForOutputPatcher = self.patch(CUT, executeForOutput.__name__, side_effect=[expected, expectedOther])
        self.patch(CUT, 'os.environ', {})

        tools = MsvsTools.find(2017)
        expectedCalls = [call(VSWHERE_COMMAND_LINE.format("-version [15.0,16.0)"))]
        self.assertEqual(os.path.join(expected, "Common7", "Tools"), tools.path)
        self.assertCalls(executeForOutputPatcher, expectedCalls)

        tools = MsvsTools.find(2019)
        expectedCalls.append(call(VSWHERE_COMMAND_LINE.format("-version [16.0,17.0)")))
        self.assertEqual(os.path.join(expectedOther, "Common7", "Tools"), tools.path)
        self.assertCalls(executeForOutputPatcher, expectedCalls)

    def test_find_latestByVsWhere(self):
        expected = '/c/vs_tools/latest'
        self.patch(CUT, 'os.environ', {'VS90COMNTOOLS': './incorrect/version/of/tools/'})
        executeForOutputPatcher = self.patch(CUT, executeForOutput.__name__, return_value=expected)

        tools = MsvsTools.find()
        expectedCalls = [call(VSWHERE_COMMAND_LINE.format(""))]
        self.assertEqual(os.path.join(expected, "Common7", "Tools"), tools.path)
        self.assertCalls(executeForOutputPatcher, expectedCalls)

        tools = MsvsTools.find()
        self.assertEqual(os.path.join(expected, "Common7", "Tools"), tools.path)

    def test_find_latestByEnvironmentName(self):
        environment = {'VS{0}COMNTOOLS'.format(version): '/c/vs_tools/{0}-version'.format(version) for version in
                       ('90', '110', '120', '150')}
        self.patch(CUT, 'os.environ', environment)
        self.patch(CUT, executeForOutput.__name__, return_value='')

        tools = MsvsTools.find()
        expected = '/c/vs_tools/{0}-version'.format('150')
        self.assertEqual(expected, tools.path)

    def test_find_withNoToolsInstalled(self):
        self.patch(CUT, 'os.environ', {})
        self.patch(CUT, executeForOutput.__name__, return_value='')
        try:
            MsvsTools.find()
        except VsToolsException as e:
            self.assertEqual(VsToolsException.NO_TOOLS_FOUND, str(e))
        else:
            self.fail("Exception should have been raised!")

    def test_find_withUnsupportedTools(self):
        unsupported = 1900
        try:
            MsvsTools.find(unsupported)
        except VsToolsException as e:
            self.assertEqual(VsToolsException.UNSUPPORTED_TOOLS.format(unsupported), str(e))
        else:
            self.fail("Exception should have been raised!")

    def test_devBatchFile_withOlderFilename(self):
        expected = VS_DEV_BATCH_MOCK_OLDER
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        isfilePatcher = self.patch(CUT, 'os.path.isfile', side_effect=[False, True])

        tools = MsvsTools.find(2008)
        self.assertEqual(expected, tools.devBatchFile)
        self.assertCalls(isfilePatcher, [call(VS_DEV_BATCH_MOCK), call(expected)])

    def test_devBatchFile_withNewerFilename(self):
        expected = VS_DEV_BATCH_MOCK
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        isfilePatcher = self.patch(CUT, 'os.path.isfile', return_value=True)

        tools = MsvsTools.find(2013)
        self.assertEqual(expected, tools.devBatchFile)
        self.assertCalls(isfilePatcher, [call(expected)])

    def test_devBatchFile_withMissingToolsBatchFile(self):
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        self.patch(CUT, 'os.path.isfile', return_value=False)
        tools = MsvsTools.find(2015)
        try:
            _dummyFilePath = tools.devBatchFile
        except VsToolsException as e:
            self.assertEqual(VsToolsException.INCOMPATIBLE_TOOLS, str(e))
        else:
            self.fail("Exception should have been raised!")

    def test_nmakeFilePath(self):
        expectedFilePath = "./tools/by_year/nmake.exe"
        expectedCommandLine = '"{0}" && where nmake'.format(VS_DEV_BATCH_MOCK)
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        self.patch(CUT, 'os.path.isfile', return_value=True)
        outputMock = "redundant\n\rredundant\n\r{0}".format(expectedFilePath)
        executePatcher = self.patch(CUT, executeForOutput.__name__, return_value=outputMock)

        tools = MsvsTools.find(2015)
        self.assertEqual(expectedFilePath, tools.nmakeFilePath)
        self.assertCalls(executePatcher, [call(expectedCommandLine)])

    def test_nmakeFilePath_withIncompatibleTools(self):
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        self.patch(CUT, 'os.path.isfile', return_value=True)
        self.patch(CUT, executeForOutput.__name__, return_value='')

        tools = MsvsTools.find(2015)
        try:
            _dummyFilePath = tools.nmakeFilePath
        except VsToolsException as e:
            self.assertEqual(VsToolsException.INCOMPATIBLE_TOOLS, str(e))
            pass
        else:
            self.fail("Exception should have been raised!")

    def test_versionId_forSpecifiedTools(self):
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        for expected, tools in \
                ((9.0, MsvsTools.find(2008)), (14.0, MsvsTools.find(2015)), (16.0, MsvsTools.find(2019))):
            self.assertEqual(expected, tools.versionId)

    def test_versionId_forLatestDeterminedTools(self):
        expectedValue = 17.0
        expectedCommandLine = '"{0}" && set VisualStudioVersion'.format(VS_DEV_BATCH_MOCK)
        self.patch(CUT, 'os.environ', {})
        self.patch(CUT, 'os.path.isfile', return_value=True)
        outputMock = [TOOLS_BASE_PATH_MOCK, "redundant\n\rredundant\n\rVisualStudioVersion={0}".format(expectedValue)]
        executePatcher = self.patch(CUT, executeForOutput.__name__, side_effect=outputMock)

        tools = MsvsTools.find()
        self.assertEqual(expectedValue, tools.versionId)
        self.assertCalls(executePatcher, [call(VSWHERE_COMMAND_LINE.format("")), call(expectedCommandLine)])

    def test_versionId_withIncompatibleTools(self):
        self.patch(CUT, 'os.environ', {})
        self.patch(CUT, 'os.path.isfile', return_value=True)
        self.patch(CUT, executeForOutput.__name__, return_value=TOOLS_BASE_PATH_MOCK)

        tools = MsvsTools.find()
        try:
            _dummyValue = tools.versionId
        except VsToolsException as e:
            self.assertEqual(VsToolsException.INCOMPATIBLE_TOOLS, str(e))
            pass
        else:
            self.fail("Exception should have been raised!")

    def test_year(self):
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        years = (2005, 2008, 2010, 2012, 2013, 2015, 2017, 2019)
        for year in years:
            tools = MsvsTools.find(year)
            self.assertEqual(year, tools.year)

    def test_solutionFormat(self):
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        formats = {9.0: (2005,), 10.0: (2008,), 11.0: (2010, 2012), 12.0: (2013, 2015, 2017, 2019)}
        for _format in formats:
            for year in formats[_format]:
                tools = MsvsTools.find(year)
                self.assertEqual(_format, tools.solutionFormat)

    def test_getCommandToCompile(self):
        makeExecutor = "./tools/common/nmake.exe"
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        self.patch(CUT, 'os.path.isfile', return_value=True)
        self.patch(CUT, executeForOutput.__name__, return_value=makeExecutor)

        tools = MsvsTools.find()

        receivedCommand = tools.getCommandToCompile()
        expectedCommand = '"{0}" {1} {{0}}'.format(makeExecutor, NMAKE_ARGUMENTS)
        self.assertEqual(expectedCommand, receivedCommand)
