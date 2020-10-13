# Internal makefile for a project
#
# PRODUCT_SOURCES - list of all source files
# PRODUCT_INCLUDES - list of all include directories
# PRODUCT_DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# PRODUCT_DEFINES - list of definitions to be invoked via command-line

include ./products/product.mak

# Preprocessor definitions
PRODUCT_DEFINES = $(PRODUCT_DEFINES) PRODUCT_DERIVED PRODUCT_DERIVED_EXTRA