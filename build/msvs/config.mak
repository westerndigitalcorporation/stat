# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

export SHELL=cmd.exe

# Set up MSVS-environment, and retry make ------------------------------------------------------------------------------
ifeq ("$(VSINSTALLDIR)", "")
export STAT_ROOT
export MSVS_DEV

ifeq ("$(STAT_MSVS_IN_LOOP)", "YES")
$(error  Failed to setup MSVS tools)
endif

build rebuild:
	@call "%STAT_ROOT:/=\%\build\msvs\setup.cmd" $(MAKE) --no-print-directory -f $(firstword $(MAKEFILE_LIST)) $@

# After MSVS-environment got set, run make -----------------------------------------------------------------------------
else

# MSVS tool-chain local definitions
CFLAGS=-FD -WX -W3 -Zi -c -nologo $(DEFINES) -Fd$(OBJECTS_DIR)/ -I$(HEADERS_DIR)/ -Fo$(OBJECTS_DIR)/
CC=cl
LINK=link
COMPILE_WITH_DEPS=\
	$(file >$(abspath $(DEP_FILE)), $(subst .d,.$(TOOLS.OBJEXT),$(DEP_FILE)) : $(HEADERS))\
	$(NEW_LINE_BREAK)  @$(CC) $(CFLAGS) "$(subst /,\,$(abspath $(SOURCE_FILE)))" >nul

# MSVS tool-chain global definitions
TOOLS.OBJEXT:=obj
TOOLS.NAME=$(VSINSTALLDIR)

# MSVS command-lines
TOOLS.COMPILE = $(if $(DEP_FILE), $(COMPILE_WITH_DEPS), @$(CC) $(CFLAGS) "$(subst /,\,$(abspath $(SOURCE_FILE)))")
TOOLS.LINK = @$(LINK) -NOLOGO -DEBUG -out:$(subst /,\,$(EXECUTABLE)) $(OBJECTS)

include $(STAT_ROOT)/build/engine.mak

endif