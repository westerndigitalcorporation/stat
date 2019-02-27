import os
from stat_makefile import StatMakefile, StatMakFileException
from testing_tools import AdvancedTestCase


class TestStatMakFile(AdvancedTestCase):
    SIMPLE_MAKEFILE = './simple.mak'
    DYNAMIC_MAKEFILE = './dynamic.mak'
    COMPOUND_MAKEFILE = './compound.mak'

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
        self.assertEqual(parser.fileName, os.path.basename(self.SIMPLE_MAKEFILE).split('.')[0])
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

