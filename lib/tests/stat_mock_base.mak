# Makefile for a Standalone Test (STAT)
#
# SOURCES - list of all source files
# INCLUDES - list of all include directories
# DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# DEFINES - list of definitions to be invoked via command-line

# Source files
SOURCES = \
    ./modules/stat_mock/tests.c \
    ./modules/stat_mock/user_like_tests.c \

# Include directories
INCLUDES = \
    ./modules/stat_mock/inc

# Dummy interfaces used to replace real ones
DUMMY_INTERFACES = \
	user_like_dummy.h

# Preprocessor definitions
DEFINES := $(DEFINES) \

# Include the STAT build rules
include ./output/stat.mak