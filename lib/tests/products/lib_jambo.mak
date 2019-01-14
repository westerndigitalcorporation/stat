# Internal makefile for a project
#
# PRODUCT_SOURCES - list of all source files
# PRODUCT_INCLUDES - list of all include directories
# PRODUCT_DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# PRODUCT_DEFINES - list of definitions to be invoked via command-line

!INCLUDE ./products/common.mak

# Source files
PRODUCT_SOURCES=$(PRODUCT_SOURCES) \


# Include directories
PRODUCT_INCLUDES=$(PRODUCT_INCLUDES) \

# Dummy interfaces
PRODUCT_DUMMY_INTERFACES=$(PRODUCT_DUMMY_INTERFACES) \

# Preprocessor definitions
PRODUCT_DEFINES=$(PRODUCT_DEFINES) STAT_MOCK=9216
	