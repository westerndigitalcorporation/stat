# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

OS.REMOVE_DIR = @rm -f -r -d $(1)
OS.MAKE_DIR = @mkdir -p $(1)
OS.COPY = @cp -p $(1) $(2)
OS.LINK = @ln -s -f $(abspath $(1)) $(abspath $(2))
OS.TOUCH = @touch $(1)
OS.DEFAULT_TOOLS = gcc