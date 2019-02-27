# Makefile for a Standalone Test (STAT)
#
# SOURCES - list of all source files
# INCLUDES - list of all include directories
# DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# DEFINES - list of definitions to be invoked via command-line

# Source files

# Include directories

# Dummy interfaces used to replace real ones

# Preprocessor definitions
DEFINES = STAT_MOCK=9216 $(DEFINES)

# Include the STAT build rules
!INCLUDE ./stat_mock_base.mak