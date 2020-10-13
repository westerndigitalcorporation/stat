#!/usr/bin/env python
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

VERSION = '1.2.4'


# ----------------------------------------------------------------------------------------------------------------------
def __getToolPath():
    import os  # Prevent porting by those which import this file
    return os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
# ----------------------------------------------------------------------------------------------------------------------


TOOL_PATH = __getToolPath()
WEB_URL = "https://github.com/westerndigitalcorporation/stat#3-usage"
RESOURCES_DIRECTORY = 'resources'
DUMMIES_DIRECTORY = 'dummies'
PRODUCT_DIRECTORY = 'products'
LOGS_DIRECTORY = 'logs'
IDE_DIRECTORY = 'ide'
OUTPUT_DIRECTORY = 'output'
REPORT_FILENAME = 'report.json'
IGNORE_FILENAME = '.statignore'
CONFIG_FILENAME = '.statconfig'
AUTO_GENERATED_MAKEFILE = '/'.join([OUTPUT_DIRECTORY, "stat.mak"])
REBUILD_TARGET = 'rebuild'
CLEAN_TARGET = 'clean'
MAKE_TOOL = {"Windows32": "gmake\\gnumake32.exe", "Windows64": "gmake\\gnumake.exe"}

OUTPUT_SUB_DIRECTORIES = ['inc', 'obj', 'bin']
ALL_OUTPUT_DIRECTORIES = [OUTPUT_DIRECTORY, IDE_DIRECTORY, LOGS_DIRECTORY]
