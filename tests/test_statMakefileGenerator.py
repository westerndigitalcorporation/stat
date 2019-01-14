import os
import shutil

import stat_attributes as attributes
from stat_makefile_generator import StatMakefileGenerator, StatMakefileGeneratorException
from services import toPosixPath, isWindows, remove
from stat_configuration import StatConfiguration
from stat_makefile import StatMakefile
from testing_tools import FileBasedTestCase

TEST_PRODUCT_NAME = "product"
TEST_PRODUCT_FILE = TEST_PRODUCT_NAME + ".mak"
TEST_PRODUCT_EXEC = TEST_PRODUCT_NAME + (".exe" if isWindows() else "")

class TestStatMakefileGenerator(FileBasedTestCase):

    def setUp(self):
        directory = os.path.dirname(attributes.AUTO_GENERATED_MAKEFILE)
        remove(directory)

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
        tools = config.getMsvsTools()
        makFile = attributes.AUTO_GENERATED_MAKEFILE
        generator = StatMakefileGenerator(productMakefile=TEST_PRODUCT_FILE)
        generator.generate()
        self.assertTrue(os.path.isfile(makFile))

        self.parser = StatMakefile(makFile)

        self.assertEqual(config['TOOL_VERSION'], self.parser['TOOL_VERSION'])
        self.assertEqual(config['TOOL_DIR'], self.parser['TOOL_DIR'])
        self.assertEqual(config['DUMMIES_DIR'], self.parser['DUMMIES_DIR'])
        self.assertEqual(config['OUTPUT_DIR'], self.parser['OUTPUT_DIR'])
        self.assertEqual(TEST_PRODUCT_NAME, self.parser[StatMakefile.NAME])
        self.assertEqual(TEST_PRODUCT_EXEC, self.parser[StatMakefile.EXEC])
        if not isWindows():
            self.assertEqual('', self.parser['VS_DEV'])

        else:
            self.assertEqual(toPosixPath(tools.devBatchFile), self.parser['VS_DEV'])

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

