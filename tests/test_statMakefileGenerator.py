import os
import platform

import stat_attributes as attributes
from build_tools import BuildTools
from build_tools_crawler import BuildToolsCrawler
from stat_makefile_generator import StatMakefileGenerator, StatMakefileGeneratorException
from services import isWindows, remove
from stat_configuration import StatConfiguration
from stat_makefile import StatMakefile
from tests.test_services import FileBasedTestCase, Mock

TEST_PRODUCT_NAME = "product"
TEST_PRODUCT_FILE = TEST_PRODUCT_NAME + ".mak"
TEST_PRODUCT_EXEC = TEST_PRODUCT_NAME + (".exe" if isWindows() else "")
TEST_TOOL_ATTRIBUTES = {"SOME_PATH": "some/path/to/the/tool", "SOME_VERSION": "1.3.0.7"}

CUT = StatMakefileGenerator.__module__


class TestStatMakefileGenerator(FileBasedTestCase):

    def setUp(self):
        directory = os.path.dirname(attributes.AUTO_GENERATED_MAKEFILE)
        remove(directory)
        self.buildToolsCrawler = self.patch(CUT, BuildToolsCrawler.__name__, auto_spec=True)
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

        parserDictionary = {k: self.parser[k] for k in self.parser}
        configDictionary = {k: config[k] for k in iter(config)}
        self.assertDictContainsSubset(configDictionary, parserDictionary)
        self.assertDictContainsSubset(TEST_TOOL_ATTRIBUTES, parserDictionary)
        self.assertEqual(TEST_PRODUCT_NAME, self.parser[StatMakefile.NAME])
        self.assertEqual(TEST_PRODUCT_EXEC, self.parser[StatMakefile.EXEC])
        self.assertEqual(platform.system(), self.parser[StatMakefile.OS])

        self.__verifyProductMakfileIsIncluded()
        self.__verifyToolsMakfileIsIncluded()
        os.remove(makFile)

    def test_generateWhenOutputDirectoryExists(self):
        makFile = attributes.AUTO_GENERATED_MAKEFILE
        directory = os.path.dirname(makFile)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        generator = StatMakefileGenerator(productMakefile=TEST_PRODUCT_FILE)
        generator.generate()
        self.assertTrue(os.path.isfile(makFile))

    def __verifyProductMakfileIsIncluded(self):
        self.assertIn('product.h', self.parser[StatMakefile.INTERFACES].split())
        self.assertIn('./products/product.c', self.parser[StatMakefile.SOURCES].split())
        self.assertIn('PRODUCT_EXTRA', self.parser[StatMakefile.DEFINES].split())

    def __verifyToolsMakfileIsIncluded(self):
        self.assertIn('UNITY_INCLUDE_CONFIG_H', self.parser[StatMakefile.DEFINES].split())
