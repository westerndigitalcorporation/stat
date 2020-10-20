# Makefile for a Standalone Test (STAT)
#
# SOURCES - list of all source files
# INCLUDES - list of all include directories
# DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# DEFINES - list of definitions to be invoked via command-line

NAME = simple

# Source files
SOURCES = \
    tests/src/sys_checksum.c \
    tests/src/ut_fletcher_tests.c

# Include directories
INCLUDES = \
    tests/inc

# Dummy interfaces used to replace real ones
DUMMY_INTERFACES = 

# Preprocessor definitions
DEFINES = SIMPLE_DEFINE ANOTHER_DEFINE ADDITIONAL_DEFINE \
	EXTRA_DEFINE SPARE_DEFINE \
	LAST_DEFINE DEFINITION_VALUED=7 DEFINITION_SIMPLE

# Include the STAT build rules
include ./core/stat_build.mak

