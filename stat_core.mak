# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

# The path to the engine file
ENGINE_MAKEFILE="$(TOOL_DIR)/engine.mak"

# Combine all the variables together
SOURCES=$(SOURCES:  = )
INCLUDES=$(INCLUDES: = )
DEFINES=$(DEFINES: = )

# Parameters for packing lists meant to be formatted later on
PREFIX=[
SUFFIX=] 
DELIMITER=,

# The following lines invoke NMAKE to run the $(ENGINE_MAKEFILE) and passes to
# it all the variables via command line. Along with the variables these lines
# also pass a temporary makefile that helps to pack the lists meant to be 
# formatted later on using the prefix and the suffix above. This trick 
# is the only way that NMAKE allows pre-padding of items in a list. 
clean build:
    @$(MAKE) /nologo /C /$(MAKEFLAGS) /F$(ENGINE_MAKEFILE) \
      DUMMIES_DIR="$(DUMMIES_DIR)" \
      OUTPUT_DIR="$(OUTPUT_DIR)" \
      OUTPUT_EXEC="$(OUTPUT_EXEC)" \
      VS_DEV="$(VS_DEV)" \
      OUTPUT_NAME="$(OUTPUT_NAME)" \
      DUMMIES="$(DUMMY_INTERFACES)" \
      SOURCES="$(SOURCES)" \
      INCLUDES="$(INCLUDES)" \
      DEFINES="$(DEFINES)" \
      TEMPFILE=<< $@   
LIST_DEFINES = $(PREFIX)$$(LIST_DEFINES: =$(SUFFIX)$(DELIMITER)$(PREFIX))$(SUFFIX)
LIST_DEFINES = $$(LIST_DEFINES:$(PREFIX)$(SUFFIX)$(DELIMITER)=)
LIST_DEFINES = $$(LIST_DEFINES:$(DELIMITER)= )
<<NOKEEP

