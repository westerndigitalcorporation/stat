#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

from argparse import ArgumentParser

from services import listMakefiles


class CommandLineParser(object):
    def __init__(self, products = (), isProductMandatory = False, toolName ="STAT"):
        self._parser = ArgumentParser(prog = toolName, description ='(STAT) Standalone unit-test framework for TDD-based designs')
        executionGroup = self._parser.add_mutually_exclusive_group()
        executionGroup.add_argument('-c', '--compile-only', action = 'store_true', help = "only compile, don't run the executables")
        executionGroup.add_argument('-run', action = 'store_true', help = "a deprecated method, is equal to not using it explicitly")
        executionGroup.add_argument('--pack-executables', action ='store_true', help ="packs all executables into a single directory")
        executionGroup.add_argument('-vs', '--visual-studio', action ='store_true', help ="creates visual studio solution for the makfile")
        executionGroup.add_argument('-si', '--source-insight', action='store_true', help="creates source-insight project for the makfile")
        self._parser.add_argument('-s', '-silent', '--silent', action ='store_true', help ="suppresses detailed output on the display")
        self.__silentlyChosenProducts = products if isProductMandatory else None
        if len(products) == 0:
            if isProductMandatory:
                raise CommandLineParserException(CommandLineParserException.NO_PRODUCT_TO_RUN)
        elif len(products) > 1:
            productGroup = self._parser.add_mutually_exclusive_group()
            productGroup.add_argument('-p', '--product', metavar='<product>', type=str, choices=products, help="run specific product configuration")
            productGroup.add_argument('-a', '--all-products', action = 'store_true', help ="run all product configurations")
        self._parser.add_argument('mak_files', metavar ='<mak file>', type = str, nargs ='*', help ="a list/wildcard of mak-files to process")

    def parse(self, commandLine):
        args = self._parser.parse_args(commandLine)
        modifiable = vars(args)
        if self.__silentlyChosenProducts is not None:
            if len(self.__silentlyChosenProducts) == 1:
                modifiable['product'] = self.__silentlyChosenProducts[0]
            elif modifiable['product'] is None:
                modifiable['all_products'] = True
        elif 'product' not in modifiable:
            modifiable['product'] = None
        if 'all_products' not in modifiable:
            modifiable['all_products'] = False
        if not args.mak_files:
            modifiable['mak_files'] = listMakefiles('.')
        else:
            foundMakfiles = listMakefiles('.', *args.mak_files)
            if foundMakfiles:
                modifiable['mak_files'] = foundMakfiles
        if args.visual_studio or args.source_insight:
            argument = '--visual-studio' if args.visual_studio else '--source-insight'
            if args.all_products:
                self.error("'--all-products' and '{0}' are incompatible command-line arguments".format(argument))
            if len(args.mak_files) != 1:
                self.error("'{0}' can be invoked for a single makfile only".format(argument))
        return args

    def error(self, message):
       self._parser.error(message)

class CommandLineParserException(Exception):
    """
    Custom exception for Command-Line parser
    """
    NO_PRODUCT_TO_RUN = "At least one product must be supplied."

if __name__ == '__main__':
    class CommandLineParserFooFooTester(CommandLineParser):
        def __init__(self):
           CommandLineParser.__init__(self)
        def test(self):
            self._parser.print_help()
            args = self._parser.parse_args()
            print("\n")
            print(args)
    handler = CommandLineParserFooFooTester()
    handler.test()