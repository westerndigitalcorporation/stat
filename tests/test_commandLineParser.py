from command_line_parser import CommandLineParser, CommandLineParserException
from services import listMakefiles
from testing_tools import FileBasedTestCase, StdOutputSubstitution


class TestCommandLineParser(FileBasedTestCase):
    def test_parseBasicArgumentDefaults(self):
        parser = CommandLineParser(['full_example.mak', 'simplified_example.mak'])
        args = parser.parse([])
        self.assertFalse(args.compile_only)
        self.assertFalse(args.run)
        self.assertFalse(args.silent)
        self.assertFalse(args.pack_executables)
        self.assertFalse(args.visual_studio)
        self.assertFalse(args.source_insight)
        self.assertFalse(args.all_products)
        self.assertIsNone(args.product)
        self.assertEqual(listMakefiles('.'), args.mak_files)

    def test_parseBasicArgumentSet(self):
        parser = CommandLineParser()
        args = parser.parse(['-c', '-s'])
        self.assertTrue(args.compile_only)
        self.assertTrue(args.silent)
        self.assertFalse(args.pack_executables)

    def test_parseContradictoryCompileOnlyAndRun(self):
        parser = CommandLineParser()
        stdOutput = StdOutputSubstitution()
        try:
            parser.parse(['-c', '-run'])
        except SystemExit:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("Arguments '-c' and '-run' shall be mutually exclusive")

    def test_parseContradictoryCompileOnlyAndPack(self):
        parser = CommandLineParser()
        stdOutput = StdOutputSubstitution()
        try:
            parser.parse(['-c', '--pack-executables'])
        except SystemExit:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("Arguments '-c' and '--pack-executables' shall be mutually exclusive")

    def test_parseContradictoryCompileOnlyAndVisualStudio(self):
        parser = CommandLineParser(products=['product'])
        stdOutput = StdOutputSubstitution()
        try:
            parser.parse(['-c', '-vs', 'simplified_example.mak'])
        except SystemExit:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("Arguments '-c' and '-vs' shall be mutually exclusive")

    def test_parseContradictoryCompileOnlyAndSourceInsight(self):
        parser = CommandLineParser(products=['product'])
        stdOutput = StdOutputSubstitution()
        try:
            parser.parse(['-c', '-si', 'simplified_example.mak'])
        except SystemExit:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("Arguments '-c' and '-si' shall be mutually exclusive")

    def test_parseMakfile(self):
        parser = CommandLineParser()
        args = parser.parse(['simplified_example.mak'])
        self.assertEqual(['simplified_example.mak'], args.mak_files)

    def test_parseMakfileList(self):
        expected = ['full_example.mak', 'simplified_example.mak']
        parser = CommandLineParser()
        args = parser.parse(expected)
        self.assertSameItems(expected, args.mak_files)

    def test_parseNoMakfileSpecified(self):
        expected = listMakefiles('.')
        parser = CommandLineParser()
        args = parser.parse([])
        self.assertSameItems(expected, args.mak_files)

    def test_parseMakfilesByWildcards(self):
        patterns = ['*example*.*']
        expected = listMakefiles('.', *patterns)
        parser = CommandLineParser()
        args = parser.parse(patterns)
        self.assertSameItems(expected, args.mak_files)

    def test_parseNonExistingUserMakfile(self):
        patterns = ['*non_existing*.*']
        expected = ['*non_existing*.*']
        parser = CommandLineParser()
        args = parser.parse(patterns)
        self.assertSameItems(expected, args.mak_files)

    def test_parseSpecificProduct(self):
        parser = CommandLineParser(products=['product','product_a'])
        args = parser.parse(['-p', 'product'])
        self.assertEqual('product', args.product)

    def test_parseAllProducts(self):
        parser = CommandLineParser(products=['product','product_a'])
        args = parser.parse(['--all-products'])
        self.assertTrue(args.all_products)
        args = parser.parse([''])
        self.assertFalse(args.all_products)

    def test_parseContradictoryProductAndAllProducts(self):
        parser = CommandLineParser(products=['product','product_a'])
        stdOutput = StdOutputSubstitution()
        try:
            parser.parse(['-p', 'product', '--all-products'])
        except SystemExit:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("Arguments '-p' and '--all-products' shall be mutually exclusive")

    def test_parseInvalidProductChoice(self):
        parser = CommandLineParser(products=['product_x','product_a'])
        stdOutput = StdOutputSubstitution()
        try:
            parser.parse(['-p', 'product'])
        except SystemExit:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("Invalid product shall fail the parsing")

    def test_parseProductUponSingleProductChoice(self):
        parser = CommandLineParser(products=['product'])
        stdOutput = StdOutputSubstitution()
        try:
            parser.parse(['-p', 'product'])
        except SystemExit:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("Choice with single product shall bring no '-p' option.")

    def test_parseAllProductsUponSingleProductChoice(self):
        parser = CommandLineParser(products=['product'])
        stdOutput = StdOutputSubstitution()
        try:
            parser.parse(['--all-products'])
        except SystemExit:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("Choice with single product shall bring no '--all-products' option.")

    def test_parseUponSingleProductChoice(self):
        parser = CommandLineParser(products=['product'], isProductMandatory=True)
        args = parser.parse([])
        self.assertEqual('product', args.product)

    def test_parseUponSingleProductWhenOneIsNotRequired(self):
        parser = CommandLineParser(products=['product'])
        args = parser.parse([])
        self.assertIsNone(args.product)
        self.assertFalse(args.all_products)

    def test_parseEmptyProductListIsRejectedWhenOneRequired(self):
        stdOutput = StdOutputSubstitution()
        try:
            CommandLineParser(products=[], isProductMandatory=True)
        except CommandLineParserException:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("At least one product shall be provided when one is required.")

    def test_parseWhenProductIsRequired(self):
        parser = CommandLineParser(products=['product_x', 'product_a'], isProductMandatory=True)
        args = parser.parse([''])
        self.assertTrue(args.all_products)
        #parser = CommandLineParser(products=['product_x','product_a'], isProductMandatory=True)
        #stdOutput = StdOutputSubstitution()
        #try:
        #    parser.parse([''])
        #except SystemExit:
        #    stdOutput.restoreStdOutputs()
        #else:
        #    stdOutput.restoreStdOutputs()
        #    self.fail("Product shall be demanded by the parser.")

    def test_parseVisualStudioCommandLineAndAllProducts(self):
        parser = CommandLineParser(products=['product_x', 'product_a'], isProductMandatory=True)
        stdOutput = StdOutputSubstitution()
        try:
            parser.parse(['-vs','--all-products', 'simplified_example.mak'])
        except SystemExit:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("All-products argument is incompatible with visual-studio argument.")

    def test_parseVisualStudioCommandLineOverSeveralMakfiles(self):
        parser = CommandLineParser(products=['product_x', 'product_a'], isProductMandatory=True)
        stdOutput = StdOutputSubstitution()
        try:
            parser.parse(['-vs', '-p', 'product_x'])
        except SystemExit:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("Only one makfile is allowed with visual-studio argument.")

    def test_parseSourceInsightCommandLineAndAllProducts(self):
        parser = CommandLineParser(products=['product_x', 'product_a'], isProductMandatory=True)
        stdOutput = StdOutputSubstitution()
        try:
            parser.parse(['-si', '--all-products', 'simplified_example.mak'])
        except SystemExit:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("All-products argument is incompatible with source-insight argument.")

    def test_parseSourceInsightCommandLineOverSeveralMakfiles(self):
        parser = CommandLineParser(products=['product_x', 'product_a'], isProductMandatory=True)
        stdOutput = StdOutputSubstitution()
        try:
            parser.parse(['-si', '-p', 'product_x'])
        except SystemExit:
            stdOutput.restoreStdOutputs()
        else:
            stdOutput.restoreStdOutputs()
            self.fail("Only one makfile is allowed with source-insight argument.")

