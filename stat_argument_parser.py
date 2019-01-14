import sys
from argparse import ArgumentParser

from si_ide_writer import SourceInsightWriter
from msvs_ide_writer import MsvsWriter
from services import listMakefiles


class StatArgumentParser(object):
    def __init__(self, products, defaultProduct=None):
        self.__products = products
        self.__defaultProduct = defaultProduct
        parser = ArgumentParser(prog="STAT", description='(STAT) Standalone unit-test framework for TDD-based designs')
        executionGroup = parser.add_mutually_exclusive_group()
        executionGroup.add_argument('-c', '--compile-only', action='store_true',
                                    help="only compile, don't run the executables")
        executionGroup.add_argument('-run', action='store_true', help="a deprecated method, has no impact")
        executionGroup.add_argument('-vs', '--visual-studio', action='store_true',
                                    help="creates visual studio solution for the makefile")
        executionGroup.add_argument('-si', '--source-insight', action='store_true',
                                    help="creates source-insight project for the makefile")
        parser.add_argument('-s', '-silent', '--silent', action='store_true',
                            help="suppresses detailed output on the display")
        if len(products) > 1:
            productGroup = parser.add_mutually_exclusive_group()
            productGroup.add_argument('-p', '--product', metavar='<product>', type=str, choices=products,
                                      help="run one of product configurations: {0}".format(', '.join(products)))
            productGroup.add_argument('-a', '--all-products', action='store_true',
                                      help="run all product configurations")
        parser.add_argument('mak_files', metavar='<mak file>', type=str, nargs='*',
                            help="a list/wildcard of makefiles to process")
        self.__parser = parser
        self.__instructions = None
        self.__makeFiles = []
        self.__ide = None

    def parse(self, arguments):
        self.__instructions = self.__parser.parse_args(arguments)
        self.__makeFiles = listMakefiles('.', *self.__instructions.mak_files)
        self.__ide = self.__determineIdeRequest()
        if not self.__ide is None:
            pureArguments = arguments if arguments else sys.argv[1:]
            pureArguments = ' '.join([item for item in pureArguments if item not in self.__instructions.mak_files])
            if not len(self.makeFiles) is 1:
                self.__parser.error("'{0}' can be invoked for a single makefile only".format(pureArguments))
            elif not len(self.targetProducts) is 1:
                self.__parser.error("'{0}' can be invoked for a single product only".format(pureArguments))

    def __determineIdeRequest(self):
        return \
            MsvsWriter.IDE if self.__instructions.visual_studio else \
            SourceInsightWriter.IDE if self.__instructions.source_insight else \
            None

    @property
    def targetProducts(self):
        if self.__instructions and len(self.__products) > 1:
            if self.__instructions.product:
                return [self.__instructions.product]
            elif self.__instructions.all_products:
                return self.__products
        return [self.__defaultProduct] if self.__defaultProduct is not None else self.__products

    @property
    def makeFiles(self):
        return self.__makeFiles

    @property
    def ide(self):
        return self.__ide

    def shallCompile(self):
        return self.__ide is None

    def shallRun(self):
        return self.shallCompile() and not self.__instructions.compile_only

    def shallBeVerbose(self):
        return not self.__instructions.silent if self.__instructions else True

class StatArgumentParserException(Exception):
    """
    Custom exception for STAT Argument parser
    """