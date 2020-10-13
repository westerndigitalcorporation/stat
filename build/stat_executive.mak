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
TOOLS_CONFIG_MAKEFILE = $(STAT_ROOT)/build/msvs/config.mak
STAT_BUILD_MAKEFILE = $(STAT_ROOT)/build/make_engine.mak
STAT_AUTO_MAKEFILE := $(OUTPUT_DIR)/stat.mak

# Declare output directories
OUTPUT_DIR := $(OUTPUT_DIR)/$(PRODUCT_FLAVOR)/$(STAT_NAMESPACE)
HEADERS_DIR := $(OUTPUT_DIR)/inc
OBJECTS_DIR := $(OUTPUT_DIR)/obj
BINARY_DIR := $(OUTPUT_DIR)/bin

-include $(TOOLS_CONFIG_MAKEFILE)
-include $(STAT_BUILD_MAKEFILE)

.PHONY: clean
clean:
	$(info Clean...)
	$(eval DIRECTORY=$(OUTPUT_DIR))
	$(RMDIR_COMMAND_LINE)
