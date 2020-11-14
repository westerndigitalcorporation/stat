#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

import sys
from argparse import ArgumentParser, SUPPRESS as ARG_SUPPRESS, RawTextHelpFormatter

import stat_attributes as attributes
from si_ide_writer import SourceInsightWriter
from msvs_ide_writer import MsvsWriter
from services import listMakefiles, countCpuCores
from vscode_writer import VsCodeWriter

STAT_MINIMAL_PARALLELISM = 2
STAT_PROG_NAME = 'makestat.py'


class StatArgumentParser(object):

    def __init__(self, products, defaultProduct=None):
        self.__products = products
        self.__defaultProduct = defaultProduct
        self.__makeFiles = []
        self.__processes = 0
        self.__shallBeVerbose = True
        self.__shallRun = False
        self.__cleaningLevel = 0
        self.__instructions = None
        self.__constructUserInterface()
        self.__redundant = None

    @property
    def targetProducts(self):
        return self.__determineTargetProducts()

    @property
    def makeFiles(self):
        return self.__makeFiles

    @property
    def ide(self):
        return getattr(self.__instructions, 'ide', None)

    @property
    def processes(self):
        return self.__processes

    @property
    def redundant(self):
        return getattr(self.__instructions, 'redundant', None)

    def parse(self, arguments):
        self.__instructions = self.__parser.parse_args(arguments)
        self.__makeFiles = listMakefiles('.', *self.__instructions.mak_files)
        self.__processes = min(getattr(self.__instructions, 'processes', 0), len(self.__makeFiles))
        self.__shallBeVerbose = self.__instructions.shallBeVerbose and self.__processes < STAT_MINIMAL_PARALLELISM
        self.__shallRun = self.shallBuild() and not self.__instructions.build_only
        self.__cleaningLevel = self.__instructions.cleaningLevel if self.__processes < STAT_MINIMAL_PARALLELISM else 1
        if self.ide is not None:
            pureArguments = arguments if arguments else sys.argv[1:]
            pureArguments = ' '.join([item for item in pureArguments if item not in self.__instructions.mak_files])
            if len(self.makeFiles) != 1:
                self.__parser.error("'{0}' can be invoked for a single makefile only".format(pureArguments))
            elif len(self.targetProducts) != 1:
                self.__parser.error("'{0}' can be invoked for a single product only".format(pureArguments))

    def shallBuild(self):
        return self.ide is None

    def shallRun(self):
        return self.__shallRun

    def shallBeVerbose(self):
        return self.__shallBeVerbose

    def getRequestedCleaningLevel(self):
        return self.__cleaningLevel

    def __constructUserInterface(self):
        # noinspection PyTypeChecker
        self.__parser = ArgumentParser(prog=STAT_PROG_NAME, formatter_class=RawTextHelpFormatter,
                                       description='(STAT) Standalone unit-test framework with emphasis '
                                                   'on Test-Driven Development for embedded firmware projects '
                                                   'developed in C language',
                                       epilog='Visit "{url}" for more details on how to use the framework.'
                                              ''.format(url=attributes.WEB_URL))
        self.__parser.add_argument('-V', '--version', action='version',
                                   version='%(prog)s {version}'.format(version=attributes.VERSION))
        self.__parser.add_argument('mak_files', metavar='<mak file>', type=str, nargs='*',
                                   help='a list of makefile names/wildcards to process')
        self.__parser.add_argument('--debug', action='append', type=str, help=ARG_SUPPRESS)
        self.__addTargetActionArguments()
        self.__addBehavioralArguments()
        self.__addProductArguments()

    def __addTargetActionArguments(self):
        parser = self.__parser
        targetGroup = parser.add_mutually_exclusive_group()
        targetGroup.add_argument('-r', '--run', action='store_false', dest="build_only", default=ARG_SUPPRESS,
                                 help='(default) compile and execute test-packages; '
                                      '\nimplicitly assumed upon no other user-choice')
        targetGroup.add_argument('-b', '--build-only', action='store_true',
                                 help='only compile, don not run the test-package executables')
        targetGroup.add_argument('-vc', '--vs-code', action='store_const', dest='ide',
                                 const=VsCodeWriter.IDE, help='creates VS-Code Workspace for the makefile')
        targetGroup.add_argument('-vs', '--visual-studio', action='store_const', dest='ide',
                                 const=MsvsWriter.IDE, help='creates MS Visual Studio Solution for the makefile')
        targetGroup.add_argument('-si', '--source-insight', action='store_const', dest="ide",
                                 const=SourceInsightWriter.IDE, help='creates Source-Insight project for the makefile;'
                                                                     '\ncurrently only version 4.0 is supported')
        targetGroup.add_argument('-run', dest='redundant', action='append_const', const='-run', help=ARG_SUPPRESS)

    def __addBehavioralArguments(self):
        parser = self.__parser
        parser.add_argument('-c', '--clean-build', action='count', default=0, dest='cleaningLevel',
                            help='increase level of cleaning efforts preceding the build:'
                                 '\n- [not specified] = incremental build, i.e. no preceding cleaning'
                                 '\n- -c = rebuild the target by just overwriting the artifact of previous build'
                                 '\n- -cc = clear the artifacts of previous build and rebuild the target from scratch')
        behavioralGroup = parser.add_mutually_exclusive_group()
        behavioralGroup.add_argument('-s', '--silent', action='store_false', dest='shallBeVerbose',
                                     help='set "silent-mode" on, suppresses detailed output on the display')
        self.__addGearArgument(behavioralGroup)

    def __addGearArgument(self, behavioralGroup):
        if countCpuCores() > 1:
            maxCpuCount = countCpuCores()

            def parseGearValue(value):
                amount = int(value)
                if amount < STAT_MINIMAL_PARALLELISM:
                    self.__parser.error("Minimal gear is {0})".format(STAT_MINIMAL_PARALLELISM))
                return amount if amount < maxCpuCount else maxCpuCount

            implicitCpuCount = maxCpuCount - 1 if maxCpuCount > STAT_MINIMAL_PARALLELISM else STAT_MINIMAL_PARALLELISM
            meta = "{{{0}-{1}}}".format(STAT_MINIMAL_PARALLELISM, maxCpuCount)
            helpText = 'speed up with multiprocessing; default=(MAX-1)={0}, for MAX=|CPU Cores|={1}; ' \
                       '\n"silent-mode" is set implicitly for better performance;' \
                       '\nimplicitly overrides "clean-build" request for a clean, but faster build;' \
                       ''.format(implicitCpuCount, maxCpuCount)
            behavioralGroup.add_argument('-g', '--gear', dest='processes', type=parseGearValue,
                                         nargs='?', const=implicitCpuCount, default=0, metavar=meta, help=helpText)
        else:
            behavioralGroup.add_argument('-g', '--gear', dest='redundant', nargs='?', type=lambda x: '-g/--gear',
                                         action='append', const='', help=ARG_SUPPRESS)

    def __addProductArguments(self):
        productGroup = self.__parser.add_mutually_exclusive_group()
        if len(self.__products) > 1:
            products = self.__products
            productGroup.add_argument('-p', '--product', metavar='<product>', type=str, choices=products,
                                      help='run one of the product configurations: {0}'.format(', '.join(products)))
            productGroup.add_argument('-a', '--all-products', action='store_true',
                                      help='run all product configurations')
        else:
            productGroup.add_argument('-p', '--product', dest='redundant', type=lambda x: '-p/--product',
                                      action='append', help=ARG_SUPPRESS)
            productGroup.add_argument('-a', '--all-products', dest='redundant',
                                      action='append_const', const='-a/--all-products', help=ARG_SUPPRESS)

    def __determineTargetProducts(self):
        if self.__instructions and len(self.__products) > 1:
            if self.__instructions.product:
                return [self.__instructions.product]
            elif self.__instructions.all_products:
                return self.__products
        return [self.__defaultProduct] if self.__defaultProduct is not None else self.__products


class StatArgumentParserException(Exception):
    """
    Custom exception for STAT Argument parser
    """
