#!/usr/bin/env python
from unittest import skip

from services import VsTools, ServicesException, vsTools
from testing_tools import *

CUT = 'services'
EXPECTED_TOOL = '/c/vs/best/tools'
EXPECTED_PATH = 'tool-chain-path'
EMULATED_OS_ENVIRON = \
    {'VS90COMNTOOLS': '/c/vs/oldest/tools', 'VS130COMNTOOLS': EXPECTED_TOOL, 'VS120COMNTOOLS': '/c/vs/medium/tools',}

class TestVsTools(AdvancedTestCase):

    def setUp(self):
        self.patch(CUT, 'os.environ', EMULATED_OS_ENVIRON)
        self.patch(CUT, 'findSubFolderOnPath', side_effect=[EXPECTED_PATH])
        self.patch(CUT, 'os.path.isfile', return_value=False)
        vsTools._toolChainPathCache = None

    def tearDown(self):
        vsTools._toolChainPathCache = None

    def test__new__isSingleton(self):
        firstInstance = VsTools()
        secondInstance = VsTools()
        self.assertEqual(firstInstance, secondInstance)

    def test_findInstallationPathWithSingleToolChainAvailable(self):
        expected = '/c/vs_tools'
        self.patch(CUT, 'os.environ', {'VS90COMNTOOLS': expected})
        self.assertEqual(expected, VsTools()._findInstallationPath())

    def test_findInstallationPathUponMultipleToolChains(self):
        self.assertEqual(EXPECTED_TOOL, VsTools()._findInstallationPath())

    def test_findInstallationPathUponPredefinedToolChain(self):
        os_environ = EMULATED_OS_ENVIRON.copy()
        os_environ[VsTools.PREDEFINED_TOOL_ENVIRON] ='/c/vs/predefined/tools'
        self.patch(CUT, 'os.environ', os_environ)
        self.patch(CUT, 'os.path.isfile', return_value=True)
        self.assertEqual(os_environ[VsTools.PREDEFINED_TOOL_ENVIRON], VsTools()._findInstallationPath())

    def test_findInstallationPathBasedOnNewVersion(self):
        self.skipTest("Due to VS2017 incompatibility")
        expected = '/c/new/vs/tools'
        os_environ = EMULATED_OS_ENVIRON.copy()
        os_environ[VsTools._FINDER_PATH_ENVIRON] = '/c/vs/finder'
        finderPath = os_environ[VsTools._FINDER_PATH_ENVIRON] + VsTools._FINDER_TOOL
        self.patch(CUT, 'os.environ', os_environ)
        isFilePatcher = self.patch(CUT, 'os.path.isfile', return_value=True)
        executeForOutputPatcher = self.patch(CUT, 'executeForOutput', side_effect=[expected])
        self.assertEqual(expected, VsTools()._findInstallationPath())
        self.assertCalls(isFilePatcher, [call(finderPath)])
        self.assertCalls(executeForOutputPatcher, [call(finderPath + VsTools._FINDER_ARGS)])

    def test_findInstallationPathUponNoToolChain(self):
        self.patch(CUT, 'os.environ', {})
        try:
            print(VsTools()._findInstallationPath())
        except ServicesException as e:
            self.assertEqual(ServicesException.NO_VS_TOOLS_FOUND, str(e))
        else:
            self.fail("The call should have failed, but passed.")

    def test_getToolChainPath(self):
        expected = 'expected-tool-chain-path'
        patcher = self.patch(CUT, 'findSubFolderOnPath', return_value=expected)
        self.assertEqual(expected, VsTools().getToolChainPath())
        self.assertCalls(patcher, [call('VC', EXPECTED_TOOL)])

    def test_getToolChainPathWithCaching(self):
        expected = VsTools().getToolChainPath()
        self.assertEqual(expected, VsTools().getToolChainPath())

    def test_getMakeToolLocation(self):
        expected = os.path.join(EXPECTED_PATH, VsTools._MAKE_TOOL)
        self.assertEqual(expected, VsTools().getMakeToolLocation())

