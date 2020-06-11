from mock import call
from psutil import cpu_count

from si_ide_writer import SourceInsightWriter
from msvs_ide_writer import MsvsWriter
from stat_argument_parser import StatArgumentParser, STAT_MINIMAL_PARALLELISM
from testing_tools import AdvancedTestCase

CUT = 'stat_argument_parser'
SINGLE_PRODUCT = 'single_product'
MANY_PRODUCTS = ['one_product', SINGLE_PRODUCT, 'next_one']
SINGLE_MAKEFILE = 'single_make_file.mak'
MANY_MAKEFILES = 'first_one.mak second_one.mak next_in_line.mak following.mak the-last-one.mak'.split(' ')
TEST_MAXIMAL_PARALLELISM = len(MANY_MAKEFILES) * 2

class TestStatArgumentParser(AdvancedTestCase):
    def setupCommon(self):
        self.listMakefiles = self.patch(CUT, 'listMakefiles')
        self.cpuCount = self.patch(CUT, cpu_count.__name__, return_value=TEST_MAXIMAL_PARALLELISM)

    def verifyCanonicalCompilationOutcomes(self, parser):
        self.assertTrue(parser.shallCompile())
        self.assertTrue(parser.shallBeVerbose())
        self.assertIsNone(parser.ide)

class TestStatArgumentParser_UponSingleProduct(TestStatArgumentParser):

    def setUp(self):
        self.setupCommon()
        self.parser = StatArgumentParser([SINGLE_PRODUCT])

    def __verifyCanonicalExecutionOutcomes(self):
        parser = self.parser
        self.assertTrue(parser.shallRun())
        self.__verifyCanonicalCompilationOutcomes()

    def __verifyCanonicalCompilationOutcomes(self):
        parser = self.parser
        self.assertEqual([SINGLE_PRODUCT], parser.targetProducts)
        self.verifyCanonicalCompilationOutcomes(parser)

    def test_parse_emptyArgumentList(self):
        self.listMakefiles.return_value = MANY_MAKEFILES
        parser = self.parser

        parser.parse([])

        self.assertEqual(MANY_MAKEFILES, parser.makeFiles)
        self.assertCalls(self.listMakefiles, [call('.')])
        self.__verifyCanonicalExecutionOutcomes()

    def test_parse_uponAllProducts(self):
        self.listMakefiles.return_value = MANY_MAKEFILES
        parser = self.parser

        parser.parse(['-a'])

        self.assertEqual(['-a/--all-products'], parser.redundant)
        self.__verifyCanonicalExecutionOutcomes()

    def test_parse_uponExplicitProduct(self):
        self.listMakefiles.return_value = MANY_MAKEFILES
        parser = self.parser

        parser.parse(['-p', SINGLE_PRODUCT])

        self.assertEqual(['-p/--product'], parser.redundant)
        self.assertEqual(MANY_MAKEFILES, parser.makeFiles)
        self.assertCalls(self.listMakefiles, [call('.')])
        self.__verifyCanonicalExecutionOutcomes()

    def test_parse_singlePackage(self):
        fakeWildcard = '*single*'
        self.listMakefiles.return_value = [SINGLE_MAKEFILE]
        parser = self.parser

        parser.parse([fakeWildcard])

        self.assertEqual([SINGLE_MAKEFILE], parser.makeFiles)
        self.assertCalls(self.listMakefiles, [call('.', fakeWildcard)])
        self.__verifyCanonicalExecutionOutcomes()

    def test_parse_manyPackageWildcards(self):
        fakeWildcard = ['*one*', SINGLE_MAKEFILE, '*last.*']
        self.listMakefiles.return_value = MANY_MAKEFILES
        parser = self.parser

        parser.parse(fakeWildcard)

        self.assertEqual(MANY_MAKEFILES, parser.makeFiles)
        self.assertCalls(self.listMakefiles, [call('.', *fakeWildcard)])
        self.__verifyCanonicalExecutionOutcomes()

    def test_parse_compileOnly(self):
        self.listMakefiles.return_value = MANY_MAKEFILES
        parser = self.parser

        parser.parse(['-c'])

        self.assertFalse(parser.shallRun())
        self.assertEqual(MANY_MAKEFILES, parser.makeFiles)
        self.assertCalls(self.listMakefiles, [call('.')])
        self.__verifyCanonicalCompilationOutcomes()

    def test_parse_overSpecifiedPackagesWithCompileOnly(self):
        fakeWildcard = MANY_MAKEFILES
        arguments = ['-c'] + fakeWildcard
        self.listMakefiles.return_value = MANY_MAKEFILES
        parser = self.parser

        parser.parse(arguments)

        self.assertFalse(parser.shallRun())
        self.assertEqual(MANY_MAKEFILES, parser.makeFiles)
        self.assertCalls(self.listMakefiles, [call('.', *fakeWildcard)])
        self.__verifyCanonicalCompilationOutcomes()

    def test_parse_withSilentMode(self):
        fakeWildcard = MANY_MAKEFILES
        arguments = ['-c', '-s'] + fakeWildcard
        self.listMakefiles.return_value = MANY_MAKEFILES
        parser = self.parser

        parser.parse(arguments)

        self.assertFalse(parser.shallBeVerbose())
        self.assertFalse(parser.shallRun())
        self.assertTrue(parser.shallCompile())
        self.assertEqual(MANY_MAKEFILES, parser.makeFiles)
        self.assertCalls(self.listMakefiles, [call('.', *fakeWildcard)])

    def _verifyCanonicalIdeCreationOutcomes(self):
        parser = self.parser
        self.assertEqual([SINGLE_PRODUCT], parser.targetProducts)
        self.assertEqual([SINGLE_MAKEFILE], parser.makeFiles)
        self.assertFalse(parser.shallCompile())
        self.assertFalse(parser.shallRun())
        self.assertIsNotNone(parser.ide)

    def test_parse_visualStudioOverSinglePackage(self):
        fakeWildcard = ['*single*']
        arguments = ['-vs'] + fakeWildcard
        self.listMakefiles.return_value = [SINGLE_MAKEFILE]
        parser = self.parser

        parser.parse(arguments)

        self.assertEqual(MsvsWriter.IDE, parser.ide)
        self._verifyCanonicalIdeCreationOutcomes()

    def test_parse_visualStudioOverManyPackages(self):
        self.listMakefiles.return_value = MANY_MAKEFILES
        try:
            self.parser.parse(['-vs'])
        except SystemExit:
            pass
        else:
            self.fail("Upon many packages '-vs' option is invalid")

    def test_parse_sourceInsightOverSinglePackage(self):
        fakeWildcard = ['*single*']
        arguments = ['-si'] + fakeWildcard
        self.listMakefiles.return_value = [SINGLE_MAKEFILE]
        parser = self.parser

        parser.parse(arguments)

        self.assertEqual(SourceInsightWriter.IDE, parser.ide)
        self._verifyCanonicalIdeCreationOutcomes()

    def test_parse_sourceInsightOverManyPackages(self):
        self.listMakefiles.return_value = MANY_MAKEFILES
        try:
            self.parser.parse(['-si'])
        except SystemExit:
            pass
        else:
            self.fail("Upon many packages '-si' option is invalid")

    def test_productsUponSpecifiedDefault(self):
        parser = StatArgumentParser([SINGLE_PRODUCT], defaultProduct=SINGLE_PRODUCT)

        parser.parse([])
        self.verifyCanonicalCompilationOutcomes(parser)
        self.assertEqual([SINGLE_PRODUCT], parser.targetProducts)

    def test_parse_withRedundantArgument(self):
        fakeWildcard = '*single*'
        self.listMakefiles.return_value = [SINGLE_MAKEFILE]
        parser = self.parser

        parser.parse([fakeWildcard, '-run', '-a'])

        self.assertEqual(['-run', '-a/--all-products'], parser.redundant)
        self.assertEqual([SINGLE_MAKEFILE], parser.makeFiles)
        self.__verifyCanonicalExecutionOutcomes()

    def test_processesUponNoGear(self):
        self.listMakefiles.return_value = SINGLE_PRODUCT * (TEST_MAXIMAL_PARALLELISM + 1)
        parser = self.parser

        parser.parse([])

        self.assertEqual(0, parser.processes)

    def test_processesGearImplicitValue(self):
        self.listMakefiles.return_value = SINGLE_PRODUCT * (TEST_MAXIMAL_PARALLELISM + 1)
        parser = self.parser

        parser.parse(['-g'])

        self.assertEqual(TEST_MAXIMAL_PARALLELISM - 1, parser.processes)
        self.assertFalse(parser.shallBeVerbose())

    def test_processesGearExplicitValue(self):
        self.listMakefiles.return_value = SINGLE_PRODUCT * (TEST_MAXIMAL_PARALLELISM + 1)
        parser = self.parser
        expected = TEST_MAXIMAL_PARALLELISM/2

        parser.parse(['-g', str(expected)])

        self.assertEqual(expected, parser.processes)
        self.assertFalse(parser.shallBeVerbose())

    def test_runOnSmallCpuCount(self):
        self.cpuCount.return_value = STAT_MINIMAL_PARALLELISM - 1
        parser = StatArgumentParser([SINGLE_PRODUCT])
        self.listMakefiles.return_value = SINGLE_PRODUCT * (TEST_MAXIMAL_PARALLELISM + 1)

        parser.parse([])

        self.assertEqual(0, parser.processes)

    def test_processesGearWithTooSmallCpuCount(self):
        self.cpuCount.return_value = STAT_MINIMAL_PARALLELISM - 1
        parser = StatArgumentParser([SINGLE_PRODUCT])
        self.listMakefiles.return_value = SINGLE_PRODUCT * (TEST_MAXIMAL_PARALLELISM + 1)

        parser.parse(['-g'])

        self.assertEqual(['-g/--gear'], parser.redundant)
        self.assertEqual(0, parser.processes)

    def test_processesGearWithMinimalCpuCount(self):
        self.listMakefiles.return_value = SINGLE_PRODUCT * (TEST_MAXIMAL_PARALLELISM + 1)
        self.cpuCount.return_value = STAT_MINIMAL_PARALLELISM
        parser = StatArgumentParser([SINGLE_PRODUCT])

        parser.parse(['-g'])

        self.assertEqual(STAT_MINIMAL_PARALLELISM, parser.processes)

    def test_processesGearWithSmallMakefileCount(self):
        self.listMakefiles.return_value = MANY_MAKEFILES

        self.parser.parse(['-g'])

        self.assertEqual(len(MANY_MAKEFILES), self.parser.processes)

    def test_processesGearAboveMaximalCpuCount(self):
        self.listMakefiles.return_value = SINGLE_PRODUCT * (TEST_MAXIMAL_PARALLELISM + 1)
        parser = self.parser

        parser.parse(['-g', str(TEST_MAXIMAL_PARALLELISM + 1)])

        self.assertEqual(TEST_MAXIMAL_PARALLELISM, parser.processes)
        self.assertFalse(parser.shallBeVerbose())

    def test_processesGearBelowMinimalCpuCount(self):
        self.listMakefiles.return_value = SINGLE_PRODUCT * (TEST_MAXIMAL_PARALLELISM + 1)
        parser = self.parser

        try:
            parser.parse(['-g', str(STAT_MINIMAL_PARALLELISM - 1)])
        except SystemExit:
            pass
        else:
            self.fail("Minimal acceptable gear below minimum shall fail")


class TestStatArgumentParser_UponManyProducts(TestStatArgumentParser):

    def setUp(self):
        self.setupCommon()
        self.parser = StatArgumentParser(MANY_PRODUCTS)

    def __verifyCanonicalCompilationOutcomes(self):
        parser = self.parser
        self.verifyCanonicalCompilationOutcomes(parser)

    def __verifyCanonicalExecutionOutcomes(self):
        parser = self.parser
        self.assertTrue(parser.shallRun())
        self.__verifyCanonicalCompilationOutcomes()

    def test_parse_simpleAllProductsOnly(self):
        self.listMakefiles.return_value = MANY_MAKEFILES
        parser = self.parser

        parser.parse(['-a'])

        self.assertEqual(MANY_PRODUCTS, parser.targetProducts)
        self.assertEqual(MANY_MAKEFILES, parser.makeFiles)
        self.assertCalls(self.listMakefiles, [call('.')])
        self.__verifyCanonicalExecutionOutcomes()

    def test_parse_uponExplicitProduct(self):
        self.listMakefiles.return_value = MANY_MAKEFILES
        parser = self.parser

        parser.parse(['-p', SINGLE_PRODUCT])

        self.assertEqual([SINGLE_PRODUCT], parser.targetProducts)
        self.assertEqual(MANY_MAKEFILES, parser.makeFiles)
        self.assertCalls(self.listMakefiles, [call('.')])
        self.__verifyCanonicalExecutionOutcomes()

    def test_parse_uponWrongExplicitProduct(self):
        try:
            self.parser.parse(['-p', 'bad_product_name'])
        except SystemExit:
            pass
        else:
            self.fail("Wrong product name in option '-p <product>' is invalid")

    def test_parse_visualStudioOverSinglePackageAndProduct(self):
        fakeWildcard = ['*single*']
        arguments = ['-vs', '-p', SINGLE_PRODUCT] + fakeWildcard
        self.listMakefiles.return_value = [SINGLE_MAKEFILE]
        parser = self.parser

        parser.parse(arguments)

        self.assertEqual(MsvsWriter.IDE, parser.ide)

    def test_parse_visualStudioOverManyProducts(self):
        fakeWildcard = ['*single*']
        arguments = ['-vs'] + fakeWildcard
        self.listMakefiles.return_value = [SINGLE_MAKEFILE]
        parser = self.parser

        try:
            parser.parse(arguments)
        except SystemExit:
            pass
        else:
            self.fail("'-vs' argument cannot be called on many products")

    def test_parse_emptyArgumentsListWithNoPrecondition(self):
        self.listMakefiles.return_value = MANY_MAKEFILES
        parser = self.parser

        parser.parse([])

        self.assertEqual(MANY_PRODUCTS, parser.targetProducts)
        self.assertEqual(MANY_MAKEFILES, parser.makeFiles)
        self.assertCalls(self.listMakefiles, [call('.')])
        self.__verifyCanonicalExecutionOutcomes()

    def test_parse_emptyArgumentsListUponDefaultProduct(self):
        self.parser = StatArgumentParser(MANY_PRODUCTS, SINGLE_PRODUCT)
        self.listMakefiles.return_value = MANY_MAKEFILES
        parser = self.parser

        parser.parse([])

        self.assertEqual([SINGLE_PRODUCT], parser.targetProducts)
        self.assertEqual(MANY_MAKEFILES, parser.makeFiles)
        self.assertCalls(self.listMakefiles, [call('.')])
        self.__verifyCanonicalExecutionOutcomes()
