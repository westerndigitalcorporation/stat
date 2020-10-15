# Makefile for a Standalone Test (STAT)
#
# SOURCES - list of all source files
# INCLUDES - list of all include directories
# DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# DEFINES - list of definitions to be invoked via command-line

NAME = simplified
PRODUCT_FLAVOR = simplified_output

# Source files
SOURCES = \
    ../unity/unity.c \
    ../lib/src/stat.c \
    ../lib/src/stat_rng.c \
    ./tests/example/stat_test_example.c \

# Include directories
INCLUDES = \
    ./ \
    ../unity \
    ../lib/inc

# Dummy interfaces used to replace real ones
DUMMY_INTERFACES = first_dummy.h second_dummy.h duplicated.h

# Preprocessor definitions
DEFINES = PROJECT_EXAMPLE DEFINITION_VALUED=7 DEFINITION_SIMPLE

# Include the STAT build rules
include ./../build/stat_executive.mak