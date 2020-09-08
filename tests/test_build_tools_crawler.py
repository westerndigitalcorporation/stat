from build_tools_crawler import BuildToolsCrawler
from msvs_tools import MsvsTools
from services import Configuration
from stat_configuration import StatConfiguration
from tests.testing_tools import AdvancedTestCase, call

CUT = BuildToolsCrawler.__module__


class TestBuildToolsCrawler(AdvancedTestCase):

    def setUp(self):
        BuildToolsCrawler.clear()
        self.configuration = Configuration()
        self.patch(CUT, StatConfiguration.__name__, return_value=self.configuration)

    def tearDown(self):
        BuildToolsCrawler.clear()

    def test_retrieve_msvs(self):
        msvsTools = self.patch(CUT, MsvsTools.__name__)

        crawler = BuildToolsCrawler()
        self.assertEqual(crawler.retrieve(), msvsTools.return_value)
        self.assertEqual(crawler.retrieve(), msvsTools.return_value)
        self.assertCalls(msvsTools, [call(self.configuration)])
