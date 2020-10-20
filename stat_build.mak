# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

# Sanity check
ifeq ("$(STAT_NAMESPACE)", "")
$(error Target namesapce is not properly configured!)
endif

# Execution makefiles
ifeq ("$(OS_NAME)", "Windows")
TOOLS_CONFIG_MAKEFILE = $(STAT_ROOT)/build/msvs/config.mak
else
TOOLS_CONFIG_MAKEFILE = $(STAT_ROOT)/build/gcc/config.mak
endif
STAT_BUILD_MAKEFILE = $(STAT_ROOT)/build/engine.mak
STAT_AUTO_MAKEFILE := $(OUTPUT_DIR)/stat.mak

# Declare output directories
OUTPUT_DIR := $(OUTPUT_DIR)/$(PRODUCT_FLAVOR)/$(STAT_NAMESPACE)
HEADERS_DIR := $(OUTPUT_DIR)/inc
OBJECTS_DIR := $(OUTPUT_DIR)/obj
BINARY_DIR := $(OUTPUT_DIR)/bin

-include $(TOOLS_CONFIG_MAKEFILE)
-include $(STAT_BUILD_MAKEFILE)

ifneq ("$(TOOLS_NAME)", "")
$(info <tools="$(TOOLS_NAME)">)
endif

.PHONY: clean
clean:
	@echo Cleaning...
	$(eval DIRECTORY=$(OUTPUT_DIR))
	$(REMOVE.directory)
	@echo complete.

