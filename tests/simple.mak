# Makefile for a Standalone Test (STAT)
#
# SOURCES - list of all source files
# INCLUDES - list of all include directories
# DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# DEFINES - list of definitions to be invoked via command-line

NAME = simplified
OUTPUT_EXEC = simple_product.exe

# Source files
SOURCES = \
    ../unity/unity.c \
    ../lib/src/stat.c \
    ../lib/src/stat_rng.c \
    ./stat_test_example.c \

# Include directories
INCLUDES = \
    ./ \
    ../unity \
    ../lib/inc

# Dummy interfaces used to replace real ones
DUMMY_INTERFACES = first_dummy.h second_dummy.h duplicated.h

# Preprocessor definitions
DEFINES = PROJECT_EXAMPLE

# Include the STAT build rules
!INCLUDE ./../stat_core.mak