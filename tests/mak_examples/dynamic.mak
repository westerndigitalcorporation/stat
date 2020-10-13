# Makefile for a Standalone Test (STAT)
#
# SOURCES - list of all source files
# INCLUDES - list of all include directories
# DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# DEFINES - list of definitions to be invoked via command-line

# Source files
SOURCES = tests/src/wrong_file.c \
    tests/src/bad_file.c

TEST_SOURCES = tests/src/ut_fletcher_tests.c \
    tests/src/ut_checksum_tests.c

NO_SOURCES =

SOURCES = \
    code/src/sys_checksum.c \
    $(EXTERNAL_SOURCES) \
    $(NO_SOURCES) \
    code/src/fletcher.c

SOURCES := test_main.c $(SOURCES) $(TEST_SOURCES) \
    shared/fa/src/ut_fa_stub.c

# Include directories
INCLUDES = code/inc

INCLUDES += \
    tests/inc

# Dummy interfaces used to replace real ones
DUMMY_INTERFACES =

# Preprocessor definitions
DEFINES = SIMPLE_DEFINE ANOTHER_DEFINE ADDITIONAL_DEFINE \
	EXTRA_DEFINE SPARE_DEFINE \
	LAST_DEFINE

