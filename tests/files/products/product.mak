# Internal makefile for a project
#
# PRODUCT_SOURCES - list of all source files
# PRODUCT_INCLUDES - list of all include directories
# PRODUCT_DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# PRODUCT_DEFINES - list of definitions to be invoked via command-line

# Source files
PRODUCT_SOURCES=product.c

# Include directories
PRODUCT_INCLUDES=./products

# Dummy interfaces
PRODUCT_DUMMY_INTERFACES=product.h

# Preprocessor definitions
PRODUCT_DEFINES=PRODUCT PRODUCT_EXTRA