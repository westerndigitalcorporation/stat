import os
import shutil

from stat_makfile_generator import StatMakefileGenerator, StatMakefileGeneratorException
from services import toPosixPath, vsTools, config, isWindows
from stat_makefile import StatMakefile
from testing_tools import FileBasedTestCase


class TestStatMakfileGenerator(FileBasedTestCase):

    def setUp(self):
        directory = os.path.dirname(StatMakefileGenerator.AUTO_GENERATED_MAKEFILE)
        if os.path.isdir(directory):
            shutil.rmtree(directory)

    def tearDown(self):
        directory = os.path.dirname(StatMakefileGenerator.AUTO_GENERATED_MAKEFILE)
        if os.path.isdir(directory):
            shutil.rmtree(directory)

    def test__init__uponWrongFilename(self):
        try:
            StatMakefileGenerator(productMakefile="wrong_name.mak")
        except StatMakefileGeneratorException:
            pass
        else:
            self.fail('The operation should have raised an exception')

    def test_generate(self):
        makFile = StatMakefileGenerator.AUTO_GENERATED_MAKEFILE
        generator = StatMakefileGenerator(productMakefile="product.mak")
        generator.generate()
        self.assertTrue(os.path.isfile(makFile))

        self.parser = StatMakefile(makFile)

        self.assertEqual(config.VERSION, self.parser['TOOL_VERSION'])
        self.assertEqual("product", self.parser['NAME'])
        self.assertEqual(toPosixPath(config.getToolDirectory()), self.parser['TOOL_DIR'])
        self.assertEqual(config.DUMMIES_DIRECTORY, self.parser['DUMMIES_DIR'])
        self.assertEqual(config.OUTPUT_DIRECTORY, self.parser['OUTPUT_DIR'])
        if not isWindows():
            self.assertEqual('', self.parser['VS_TOOL'])
        else:
            self.assertEqual(toPosixPath(vsTools.getToolChainPath()), self.parser['VS_TOOL'])

        self.__verifyProductMakfileIsIncluded()
        self.__verifyToolsMakfileIsIncluded()
        os.remove(makFile)

    def test_generateWhenOutputDirectoryExists(self):
        makFile = StatMakefileGenerator.AUTO_GENERATED_MAKEFILE
        directory = os.path.dirname(makFile)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        generator = StatMakefileGenerator(productMakefile="product.mak")
        generator.generate()
        self.assertTrue(os.path.isfile(makFile))

    def __verifyProductMakfileIsIncluded(self):
        self.assertIn('product.h', self.parser[StatMakefile.INTERFACES].split())
        self.assertIn('product.c', self.parser[StatMakefile.SOURCES].split())
        self.assertIn('PRODUCT_EXTRA', self.parser[StatMakefile.DEFINES].split())

    def __verifyToolsMakfileIsIncluded(self):
        self.assertIn('UNITY_INCLUDE_CONFIG_H', self.parser[StatMakefile.DEFINES].split())

