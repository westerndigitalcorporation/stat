# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

export SHELL=cmd.exe

# MSVS tools
OBJEXT:=obj
CFLAGS=-FD -WX -W3 -Zi -c -nologo
CC=cl
LINK=link

# MSVS Command-lines
TOOLS_NAME=$(VSINSTALLDIR)
REMOVE.directory = @if exist $(DIRECTORY) @rmdir /Q /S $(subst /,\,$(DIRECTORY)/) >nul
CREATE.directory = @md $(subst /,\,$(NEW_DIRECTORY)) >nul
HEADER_COPY_COMMAND_LINE = @copy /Y "$(subst /,\,$(SOURCE_HEADER))" "$(subst /,\,$(TARGET_HEADER))" >nul
HEADER_LINK_COMMAND_LINE = @cmd /c mklink "$(subst /,\,$(TARGET_HEADER))" "$(subst /,\,$(abspath $(SOURCE_HEADER)))" >nul
DEP_COMMAND_LINE = $(file >$(abspath $(DEP_FILE)), $(subst .d,.$(OBJEXT),$(DEP_FILE)) : $(HEADERS))
COMPILE_COMMAND_LINE = @$(CC) $(CFLAGS) $(DEFINES) -Fd$(OBJECTS_DIR)/ -I$(HEADERS_DIR)/ -Fo$(OBJECTS_DIR)/ "$(subst /,\,$(abspath $(SOURCE_FILE)))"
LINK_COMMAND_LINE = @$(LINK) -NOLOGO -DEBUG -out:$(subst /,\,$(EXECUTABLE)) $(OBJECTS)

# Setup MSVS tools, and retry make -------------------------------------------------------------------------------------
ifeq ("$(VSINSTALLDIR)", "")
export STAT_ROOT
export MSVS_DEV

build rebuild:
	@call "%STAT_ROOT:/=\%\build\msvs\setup.cmd" $(MAKE) --no-print-directory -f $(firstword $(MAKEFILE_LIST)) $@

# Disable build targets, since makefile was already called above
STAT_BUILD_MAKEFILE=

# Exit if failed to setup MSVS environment -----------------------------------------------------------------------------
else ifeq ("$(STAT_MSVS_IN_LOOP)", "YES")
$(error  Failed to setup MSVS tools)

endif