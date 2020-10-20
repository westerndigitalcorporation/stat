import platform

from build_tools_crawler import BuildToolsCrawler
from msvs_tools import MsvsTools
from services import Configuration
from stat_configuration import StatConfiguration
from tests.testing_tools import AdvancedTestCase, call

CUT = BuildToolsCrawler.__module__
TEST_MSVS_ATTRIBUTES = dict(MSVS_ATTRIBUTE1="test/value/1", MSVS_ATTRIBUTE2="test/value/2")


class TestBuildToolsCrawler(AdvancedTestCase):

    def setUp(self):
        BuildToolsCrawler.clear()
        self.configuration = Configuration()
        self.patch(CUT, StatConfiguration.__name__, return_value=self.configuration)
        self.msvsTools = self.patch(CUT, MsvsTools.__name__)
        self.msvsTools.return_value.getAttributes.return_value = TEST_MSVS_ATTRIBUTES

    def tearDown(self):
        BuildToolsCrawler.clear()

    def test_retrieveMsvsOnWindows(self):
        self.patchObject(platform, platform.system.__name__, return_value="Windows")

        crawler = BuildToolsCrawler()

        self.assertEqual(self.msvsTools.return_value, crawler.retrieveMsvs())
        self.msvsTools.assert_has_calls([call(self.configuration)])

    def test_retrieveMsvsOnLinux(self):
        self.patchObject(platform, platform.system.__name__, return_value="Linux")

        crawler = BuildToolsCrawler()

        self.assertEqual(None, crawler.retrieveMsvs())
        self.assertCalls(self.msvsTools, [])

    def test_getAttributesOnWindowsWithMsvs(self):
        self.patchObject(platform, platform.system.__name__, return_value="Windows")

        crawler = BuildToolsCrawler()

        self.assertSameItems(TEST_MSVS_ATTRIBUTES, crawler.getBuildAttributes())

    def test_getAttributesOnLinux(self):
        self.patchObject(platform, platform.system.__name__, return_value="Linux")

        crawler = BuildToolsCrawler()

        self.assertSameItems({}, crawler.getBuildAttributes())
