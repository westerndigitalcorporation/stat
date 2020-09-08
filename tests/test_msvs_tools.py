#!/usr/bin/env python
from services import executeForOutput, Configuration, toPosixPath
from msvs_tools import VsToolsException, MsvsTools, NMAKE_ARGUMENTS
from tests.testing_tools import *  # pylint: disable=unused-wildcard-import

CUT = MsvsTools.__module__

USER_MAKE_FILE = "simple.mak"
EXPECTED_TOOL = '/c/vs/best/tools'
EXPECTED_PATH = 'tool-chain-path'
EMULATED_OS_ENVIRON = \
    {'VS90COMNTOOLS': '/c/vs/oldest/tools', 'VS130COMNTOOLS': EXPECTED_TOOL, 'VS120COMNTOOLS': '/c/vs/medium/tools', }

VSWHERE_BASE_PATH = os.path.join(attributes.TOOL_PATH, attributes.RESOURCES_DIRECTORY)
VSWHERE_VERSION_COMMAND_LINE = VSWHERE_BASE_PATH + "\\vswhere.exe -legacy -property installationVersion -latest"
VSWHERE_PATH_COMMAND_LINE = VSWHERE_BASE_PATH + "\\vswhere.exe -legacy {0} -property installationPath -latest"
TOOLS_BASE_PATH_MOCK = "./test/tools/path"
TOOLS_FULL_PATH_MOCK = os.path.join(TOOLS_BASE_PATH_MOCK, "Common7", "Tools")
MSVS_DEV_BATCH_MOCK = os.path.join(TOOLS_FULL_PATH_MOCK, "VsDevCmd.bat")
MSVS_DEV_BATCH_MOCK_OLDER = os.path.join(TOOLS_FULL_PATH_MOCK, "vsvars32.bat")
DUMMY_ENVIRONMENT = {'VS{0}0COMNTOOLS'.format(version): TOOLS_FULL_PATH_MOCK
                     for version in (8, 9, 10, 11, 12, 14, 15, 16)}


class TestMsvsTools(AdvancedTestCase):

    def setUp(self):
        self.skipWindowsTest()
        self.isfile = self.patch(CUT, 'os.path.isfile', side_effect=lambda pathName: True)

    def test_find_byEnvironmentOlder(self):
        expected = TOOLS_BASE_PATH_MOCK
        other = '/c/vs_tools_other'
        self.patch(CUT, 'os.environ', {'VS90COMNTOOLS': expected, 'VS110COMNTOOLS': other})
        self.isfile.side_effect = lambda pathName: pathName.find("vsvars32.bat") > -1
        config = Configuration(MSVS_VERSION=2008)

        tools = MsvsTools(config)
        self.assertEqual(expected, tools.path)
        self.assertEqual(expected + "/vsvars32.bat", config['MSVS_DEV'])

    def test_find_byEnvironmentNewer(self):
        expected = TOOLS_BASE_PATH_MOCK
        expectedOther = '/c/vs_tools_other'
        self.patch(CUT, 'os.environ', {'VS90COMNTOOLS': expectedOther, 'VS110COMNTOOLS': expected})
        config = Configuration(MSVS_VERSION=2012)

        tools = MsvsTools(config)
        self.assertEqual(expected, tools.path)
        self.assertEqual(expected + "/VsDevCmd.bat", config['MSVS_DEV'])

    def test_find_byVsWhere(self):
        expected = '/c/vs_tools/VsWhere'
        expectedOther = '/c/vs_tools/other/VsWhere'
        executeForOutputPatcher = self.patch(CUT, executeForOutput.__name__, side_effect=[expected, expectedOther])
        self.patch(CUT, 'os.environ', {})

        config = Configuration(MSVS_VERSION=2017)
        tools = MsvsTools(config)
        expectedCalls = [call(VSWHERE_PATH_COMMAND_LINE.format("-version [15.0,16.0)"))]
        self.assertEqual(os.path.join(expected, "Common7", "Tools"), tools.path)
        self.assertEqual("/".join([expected, "Common7", "Tools", "VsDevCmd.bat"]), config['MSVS_DEV'])
        self.assertCalls(executeForOutputPatcher, expectedCalls)

        config = Configuration(MSVS_VERSION=2019)
        tools = MsvsTools(config)
        expectedCalls.append(call(VSWHERE_PATH_COMMAND_LINE.format("-version [16.0,17.0)")))
        self.assertEqual(os.path.join(expectedOther, "Common7", "Tools"), tools.path)
        self.assertCalls(executeForOutputPatcher, expectedCalls)

    def test_find_latestByVsWhere(self):
        expected = '/c/vs_tools/latest'
        self.patch(CUT, 'os.environ', {'VS90COMNTOOLS': './incorrect/version/of/tools/'})

        def emulateVsWhere(commandLine):
            if VSWHERE_PATH_COMMAND_LINE.format("-version [15.0,16.0)") == commandLine:
                return expected
            if VSWHERE_VERSION_COMMAND_LINE == commandLine:
                return "15.9.287.12"
            self.fail("Unexpected command line {0}.".format(commandLine))
        self.patch(CUT, executeForOutput.__name__, side_effect=emulateVsWhere)

        tools = MsvsTools(Configuration())
        self.assertEqual(os.path.join(expected, "Common7", "Tools"), tools.path)

    def test_find_latestByEnvironmentName(self):
        environment = {'VS{0}COMNTOOLS'.format(version): '/c/vs_tools/{0}-version'.format(version) for version in
                       ('90', '110', '120', '150')}
        self.patch(CUT, 'os.environ', environment)
        self.patch(CUT, executeForOutput.__name__, return_value='')

        tools = MsvsTools(Configuration())
        expected = '/c/vs_tools/{0}-version'.format('150')
        self.assertEqual(expected, tools.path)

    def test_find_withNoToolsInstalled(self):
        self.patch(CUT, 'os.environ', {})
        self.patch(CUT, executeForOutput.__name__, return_value='')
        try:
            MsvsTools(Configuration())
        except VsToolsException as e:
            self.assertEqual(VsToolsException.NO_TOOLS_FOUND, str(e))
        else:
            self.fail("Exception should have been raised!")

    def test_find_withUnsupportedTools(self):
        unsupported = 1900
        try:
            MsvsTools(Configuration(MSVS_VERSION=unsupported))
        except VsToolsException as e:
            self.assertEqual(VsToolsException.UNSUPPORTED_TOOLS.format(unsupported), str(e))
        else:
            self.fail("Exception should have been raised!")

    def test_devBatchFile_withMissingToolsBatchFile(self):
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        self.isfile.side_effect = lambda pathName: False
        try:
            tools = MsvsTools(Configuration(MSVS_VERSION=2015))
            _ = tools.devBatchFile
        except VsToolsException as e:
            self.assertEqual(VsToolsException.INCOMPATIBLE_TOOLS, str(e))
        else:
            self.fail("Exception should have been raised!")

    def test_nmakeFilePath(self):
        expectedFilePath = "./tools/by_year/nmake.exe"
        expectedCommandLine = '"{0}" && where nmake'.format(MSVS_DEV_BATCH_MOCK)
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        outputMock = "redundant\n\rredundant\n\r{0}".format(expectedFilePath)
        executePatcher = self.patch(CUT, executeForOutput.__name__, return_value=outputMock)

        tools = MsvsTools(Configuration(MSVS_VERSION=2015))
        self.assertEqual(expectedFilePath, tools.nmakeFilePath)
        self.assertCalls(executePatcher, [call(expectedCommandLine)])

    def test_nmakeFilePath_withIncompatibleTools(self):
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        self.patch(CUT, executeForOutput.__name__, return_value='')

        tools = MsvsTools(Configuration(MSVS_VERSION=2015))
        try:
            _dummyFilePath = tools.nmakeFilePath
        except VsToolsException as e:
            self.assertEqual(VsToolsException.INCOMPATIBLE_TOOLS, str(e))
            pass
        else:
            self.fail("Exception should have been raised!")

    def test_versionId_forSpecifiedTools(self):
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        for expected, tools in (
                (9.0, MsvsTools(Configuration(MSVS_VERSION=2008))),
                (14.0, MsvsTools(Configuration(MSVS_VERSION=2015))),
                (16.0, MsvsTools(Configuration(MSVS_VERSION=2019)))):
            self.assertEqual(expected, tools.versionId)

    def test_versionId_forLatestDeterminedTools(self):
        expectedValue = 17.0
        self.patch(CUT, 'os.environ', {})
        outputMock = [str(expectedValue), TOOLS_BASE_PATH_MOCK,
                      "redundant\n\rredundant\n\rVisualStudioVersion={0}".format(expectedValue)]
        executePatcher = self.patch(CUT, executeForOutput.__name__, side_effect=outputMock)

        tools = MsvsTools(Configuration())
        self.assertEqual(expectedValue, tools.versionId)
        self.assertCalls(executePatcher, [
            call(VSWHERE_VERSION_COMMAND_LINE),
            call(VSWHERE_PATH_COMMAND_LINE.format("-version [17.0,18.0)"))])

    def test_year(self):
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        years = (2005, 2008, 2010, 2012, 2013, 2015, 2017, 2019)
        for year in years:
            tools = MsvsTools(Configuration(MSVS_VERSION=year))
            self.assertEqual(year, tools.year)

    def test_solutionFormat(self):
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)
        formats = {9.0: (2005,), 10.0: (2008,), 11.0: (2010, 2012), 12.0: (2013, 2015, 2017, 2019)}
        for _format in formats:
            for year in formats[_format]:
                tools = MsvsTools(Configuration(MSVS_VERSION=year))
                self.assertEqual(_format, tools.solutionFormat)

    def test_getCommandToCompile(self):
        makeExecutor = "./tools/common/nmake.exe"
        self.patch(CUT, 'os.environ', DUMMY_ENVIRONMENT)

        def emulateVsWhere(commandLine):
            if VSWHERE_VERSION_COMMAND_LINE == commandLine:
                return "12.79.8712"
            return makeExecutor

        self.patch(CUT, executeForOutput.__name__, side_effect=emulateVsWhere)

        tools = MsvsTools(Configuration())

        receivedCommand = tools.getCommandToCompile()
        expectedCommand = '"{0}" {1} {{0}}'.format(makeExecutor, NMAKE_ARGUMENTS)
        self.assertEqual(expectedCommand, receivedCommand)
