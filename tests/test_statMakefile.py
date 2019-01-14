import os
import re

from stat_makefile import StatMakefile, StatMakFileException, _REG_EXP_INCLUDE
from testing_tools import AdvancedTestCase


class TestStatMakFile(AdvancedTestCase):
    SIMPLE_MAKEFILE = './mak_examples/simple.mak'
    DYNAMIC_MAKEFILE = './mak_examples/dynamic.mak'
    COMPOUND_MAKEFILE = './mak_examples/compound.mak'

    def test_initializationUponNoneExistingMakefile(self):
        nonExistingFile = './non_existing_file.mak'
        try:
            StatMakefile(nonExistingFile)
        except StatMakFileException as e:
            self.assertEqual("Makefile '{fileName}' doesn't exist!".format(fileName = nonExistingFile), str(e))
        else:
            self.fail('The operation should have raised an exception')

    def test_initializationUponSimpleMakefile(self):
        expected = {
            StatMakefile.SOURCES: ['tests/src/sys_checksum.c', 'tests/src/ut_fletcher_tests.c'],
            StatMakefile.INCLUDES: ['tests/inc'],
            StatMakefile.INTERFACES: [],
            StatMakefile.DEFINES: ['SIMPLE_DEFINE', 'ANOTHER_DEFINE', 'ADDITIONAL_DEFINE', 'EXTRA_DEFINE', 'SPARE_DEFINE', 'LAST_DEFINE', 'DEFINITION_VALUED=7', 'DEFINITION_SIMPLE'],
            StatMakefile.INCLUDE: [] if os.getenv('INCLUDE') is None else [os.getenv('INCLUDE')]
        }
        parser = StatMakefile(self.SIMPLE_MAKEFILE)
        self.assertEqual(parser.name, os.path.basename(self.SIMPLE_MAKEFILE).split('.')[0])
        for variable in expected:
            self.assertEqual(expected[variable], parser[variable].split())
        self.assertEqual('simple', parser['NAME'])

    def test_parsingOfDynamicallyDefinedValues(self):
        expected = {
            StatMakefile.SOURCES: ['test_main.c', 'code/src/sys_checksum.c', 'code/src/fletcher.c', 'tests/src/ut_fletcher_tests.c', 'tests/src/ut_checksum_tests.c', 'shared/fa/src/ut_fa_stub.c'],
            StatMakefile.INCLUDES: ['code/inc', 'tests/inc']
        }

        parser = StatMakefile(self.DYNAMIC_MAKEFILE)

        for variable in expected:
            self.assertEqual(expected[variable], parser[variable].split())

    def test_parsingOfCompoundMakefileWithInclude(self):
        expected = {
            StatMakefile.SOURCES: ['test_main.c', 'code/src/sys_checksum.c', 'code/src/tools.c', 'code/src/logs.c',
                        'code/src/fletcher.c', 'tests/src/ut_fletcher_tests.c', 'tests/src/ut_checksum_tests.c', 'shared/fa/src/ut_fa_stub.c'],
            StatMakefile.INCLUDES: ['code/inc', 'tests/inc'],
            StatMakefile.DEFINES: ['SIMPLE_DEFINE', 'ANOTHER_DEFINE', 'ADDITIONAL_DEFINE', 'EXTRA_DEFINE', 'SPARE_DEFINE', 'LAST_DEFINE', 'SYSTEM_DEFINE_EXTRA'],
        }

        parser = StatMakefile(self.COMPOUND_MAKEFILE)

        for variable in expected:
            self.assertEqual(expected[variable], parser[variable].split())

    def test_regexForInclude(self):
        pattern = _REG_EXP_INCLUDE
        strings = ["", "   ", "!INCLUDE ", "!INCLUDETRASH", "!INCLUDE <bad url", "!INCLUDE bad url>",
                   "!INCLUDE good/url/to/catch", "!INCLUDE <another/very/good/url/to/catch>"]
        matches = [re.search(pattern, text) for text in strings]
        results = [item.group('path') for item in matches if item is not None]
        self.assertEqual([None]*(len(matches)-2), matches[:-2])
        self.assertEqual(["good/url/to/catch", "another/very/good/url/to/catch"], results)

    def test_regexForSubstitution(self):
        pattern = '\$\((?P<variable>[^\(\)\$]+)\)'
        text = "$(correct) value (param1) param2) $(data1 $(valid1) $(good)"
        expected = "substituted value (param1) param2) $(data1 substituted substituted"
        received = re.sub(pattern, 'substituted', text)
        self.assertEqual(expected, received)