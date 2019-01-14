# Makefile for a Standalone Test (STAT)
#
# SOURCES - list of all source files
# INCLUDES - list of all include directories
# DUMMY_INTERFACES - list of all dummy header-files to be used instead FW-version
# DEFINES - list of definitions to be invoked via command-line

# Changing the environment variable
INCLUDE=./;./extra

# Source files
EXTERNAL_SOURCES = code/src/tools.c \
    code/src/logs.c

# Include the STAT build rules
!INCLUDE ./dynamic.mak
!INCLUDE ./products/product_derived.mak
!INCLUDE <system.mak>