# Internal makefile for a project
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: CC0-1.0

# PRODUCT_SOURCES - list of all source files
# PRODUCT_INCLUDES - list of all include directories
# PRODUCT_DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# PRODUCT_DEFINES - list of definitions to be invoked via command-line

# Source files
PRODUCT_SOURCES=\
	./products/product.c

# Include directories
PRODUCT_INCLUDES=\

# Dummy interfaces
PRODUCT_DUMMY_INTERFACES=

# Preprocessor definitions
PRODUCT_DEFINES=STAT_PRODUCT_SETUP STAT_PRODUCT_TEARDOWN