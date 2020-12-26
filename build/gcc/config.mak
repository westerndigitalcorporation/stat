# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

# GCC tool-chain local definitions
GFLAGS=-g -Wall -Wno-pointer-to-int-cast -Wno-int-to-pointer-cast -Werror
CFLAGS=$(GFLAGS) -c -I $(HEADERS_DIR) $(DEFINES) -o $(OBJECT_FILE)
DEPFLAGS=-MT $(OBJECT_FILE) -MMD -MP -MF $(DEP_FILE).tmp
LFLAGS=$(GFLAGS)
CC=gcc
LINK=gcc
COMPILE_WITH_DEPS=\
	@$(CC) $(DEPFLAGS) $(CFLAGS) "$(abspath $(SOURCE_FILE))"\
	$(NEW_LINE_BREAK) $(call OS.COPY, $(DEP_FILE).tmp, $(DEP_FILE))\
	$(NEW_LINE_BREAK) $(call OS.TOUCH, $(OBJECT_FILE))

# GCC tool-chain global definitions
TOOLS.OBJEXT:=o
TOOLS.NAME=$(shell $(CC) --version | grep $(CC))

# MSVS command-lines
TOOLS.COMPILE = $(if $(DEP_FILE), $(COMPILE_WITH_DEPS), @$(CC) $(CFLAGS) "$(abspath $(SOURCE_FILE))")
TOOLS.LINK = @$(LINK) $(LFLAGS) -o $(EXECUTABLE) $(OBJECTS)

include $(STAT_ROOT)/build/engine.mak