# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

# GCC tools
OBJEXT:=o
GFLAGS=-g -Wall -Wno-pointer-to-int-cast -Wno-int-to-pointer-cast -Werror
CFLAGS=$(GFLAGS) -c
CC=gcc
LFLAGS=$(GFLAGS)
LINK=gcc

# MSVS Command-lines
TOOLS_NAME=$(shell $(CC) --version | grep $(CC))
REMOVE.directory = @rm -f -r -d $(DIRECTORY)
CREATE.directory = @mkdir -p $(NEW_DIRECTORY)
HEADER_COPY_COMMAND_LINE = @cp -p $(SOURCE_HEADER) $(TARGET_HEADER)
HEADER_LINK_COMMAND_LINE = @ln -s -f $(abspath $(SOURCE_HEADER)) $(abspath $(TARGET_HEADER))
DEP_COMMAND_LINE = @$(CC) $(CFLAGS) -I $(HEADERS_DIR) $(DEFINES) -MM -MT $(subst .d,.o, $(DEP_FILE)) $(SOURCE_FILE) -MF $(DEP_FILE)
COMPILE_COMMAND_LINE = @$(CC) $(CFLAGS) -I $(HEADERS_DIR) $(DEFINES) -o $(OBJECT_FILE) "$(abspath $(SOURCE_FILE))"
LINK_COMMAND_LINE = @$(LINK) $(LFLAGS) -o $(EXECUTABLE) $(OBJECTS)
