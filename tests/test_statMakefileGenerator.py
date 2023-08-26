import os
import platform

import stat_attributes as attributes
from build_tools_crawler import BuildToolsCrawler
from stat_makefile_generator import StatMakefileGenerator, StatMakefileGeneratorException
from services import isWindows, remove, nameExecutable
from stat_configuration import StatConfiguration
from stat_makefile import StatMakefile
from tests.test_services import FileBasedTestCase, Mock

TEST_PRODUCT_NAME = "product"
TEST_PRODUCT_FILE = TEST_PRODUCT_NAME + ".mak"
TEST_PRODUCT_EXEC = nameExecutable(TEST_PRODUCT_NAME)
TEST_TOOL_ATTRIBUTES = {"SOME_PATH": "some/path/to/the/tool", "SOME_VERSION": "1.3.0.7"}

CUT = StatMakefileGenerator.__module__


class TestStatMakefileGenerator(FileBasedTestCase):

    def setUp(self):
        directory = os.path.dirname(attributes.AUTO_GENERATED_MAKEFILE)
        remove(directory)
        self.buildToolsCrawler = self.patch(CUT, BuildToolsCrawler.__name__, autospec=True)
        self.buildToolsCrawler.return_value.getBuildAttributes.return_value = TEST_TOOL_ATTRIBUTES

    def tearDown(self):
        directory = os.path.dirname(attributes.AUTO_GENERATED_MAKEFILE)
        remove(directory)

    def test__init__uponWrongFilename(self):
        try:
            StatMakefileGenerator(productMakefile="wrong_name.mak")
        except StatMakefileGeneratorException:
            pass
        else:
            self.fail('The operation should have raised an exception')

    def test_generate(self):
        config = StatConfiguration()
        makFile = attributes.AUTO_GENERATED_MAKEFILE
        generator = StatMakefileGenerator(productMakefile=TEST_PRODUCT_FILE)
        generator.generate()
        self.assertTrue(os.path.isfile(makFile))

        self.parser = StatMakefile(makFile)

        for parameter in iter(config):
            self.assertEqual(config[parameter], self.parser[parameter])
        self.assertEqual(TEST_PRODUCT_NAME, self.parser[StatMakefile.NAME])
        self.assertEqual(TEST_PRODUCT_EXEC, self.parser[StatMakefile.EXEC])
        self.assertEqual(platform.system(), self.parser[StatMakefile.OS])

        self.__verifyProductMakefileIsIncluded()
        self.__verifyToolsMakefileIsIncluded()
        os.remove(makFile)

    def test_generateWhenOutputDirectoryExists(self):
        makFile = attributes.AUTO_GENERATED_MAKEFILE
        directory = os.path.dirname(makFile)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        generator = StatMakefileGenerator(productMakefile=TEST_PRODUCT_FILE)
        generator.generate()
        self.assertTrue(os.path.isfile(makFile))

    def __verifyProductMakefileIsIncluded(self):
        self.assertIn('product.h', self.parser[StatMakefile.INTERFACES].split())
        self.assertIn('./products/product.c', self.parser[StatMakefile.SOURCES].split())
        self.assertIn('PRODUCT_EXTRA', self.parser[StatMakefile.DEFINES].split())

    def __verifyToolsMakefileIsIncluded(self):
        self.assertIn('UNITY_INCLUDE_CONFIG_H', self.parser[StatMakefile.DEFINES].split())
