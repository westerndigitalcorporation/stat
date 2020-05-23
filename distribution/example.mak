# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: CC0-1.0

# Makefile for a Standalone Test (STAT)
#
# SOURCES - list of all source files
# INCLUDES - list of all include directories
# DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# DEFINES - list of definitions to be invoked via command-line

# Source files
SOURCES = \
    ./stat_test_example.c \

# Include directories
INCLUDES = \
    ./ \

# Dummy interfaces used to replace real ones
DUMMY_INTERFACES = dummy_header.h

# Preprocessor definitions
DEFINES = D_TEST_EXAMPLE

# Include the STAT build rules
!INCLUDE ./output/stat.mak