# Internal makefile for STAT tools
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

# SOURCES - list of all source files
# INCLUDES - list of all include directories
# DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# DEFINES - list of definitions to be invoked via command-line
    
# Source files
SOURCES:=$(SOURCES) $(PRODUCT_SOURCES) \
    $(STAT_ROOT)/unity/unity.c \
    $(STAT_ROOT)/lib/src/stat.c \
    $(STAT_ROOT)/lib/src/stat_rng.c \
    $(STAT_ROOT)/lib/src/stat_mock.c \

# Include directories
INCLUDES:=$(INCLUDES) $(PRODUCT_INCLUDES) \
    $(STAT_ROOT)/unity \
    $(STAT_ROOT)/lib/inc \

# Dummy interfaces
DUMMY_INTERFACES:=$(DUMMY_INTERFACES) $(PRODUCT_DUMMY_INTERFACES)

# Preprocessor definitions
DEFINES:=$(DEFINES) $(PRODUCT_DEFINES) UNITY_INCLUDE_CONFIG_H STAT