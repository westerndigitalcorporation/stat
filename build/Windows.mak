# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT
WIN.COMMA=,
WIN.COPY_SCRIPT:=$(subst /,\,$(STAT_ROOT))\build\copy.cmd

OS.REMOVE_DIR=@if exist $(1) @rmdir /Q /S $(subst /,\,$(1)/) >nul
OS.MAKE_DIR=@md $(subst /,\,$(1)) >nul
OS.COPY=@$(WIN.COPY_SCRIPT) $(1) $(2) $(3) >nul
OS.TOUCH=@copy /B $(1)+$(WIN.COMMA)$(WIN.COMMA) $(1)
OS.DEFAULT_TOOLS=msvs
OS.NULL_OUTPUT=nul