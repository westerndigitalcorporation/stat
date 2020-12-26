# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

OS.REMOVE_DIR = @if exist $(1) @rmdir /Q /S $(subst /,\,$(1)/) >nul
OS.MAKE_DIR = @md $(subst /,\,$(1)) >nul
OS.COPY = @copy /Y "$(subst /,\,$(1))" "$(subst /,\,$(2))" >nul
OS.LINK = @cmd /c mklink "$(subst /,\,$(2))" "$(subst /,\,$(abspath $(1)))" >nul
OS.TOUCH = @type nul >$(1)
OS.DEFAULT_TOOLS = msvs