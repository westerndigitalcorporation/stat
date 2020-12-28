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

# Declare path to auto-generated STAT makefile
STAT_AUTO_MAKEFILE := $(OUTPUT_DIR)/stat.mak

# Declare output directories
OUTPUT_DIR := $(OUTPUT_DIR)/$(PRODUCT_FLAVOR)/$(STAT_NAMESPACE)
HEADERS_DIR := $(OUTPUT_DIR)/inc
OBJECTS_DIR := $(OUTPUT_DIR)/obj
BINARY_DIR := $(OUTPUT_DIR)/bin

include $(STAT_ROOT)/build/$(OS_NAME).mak
include $(STAT_ROOT)/build/$(OS.DEFAULT_TOOLS)/config.mak

.PHONY: clean
clean:
	$(info  )
	@echo Cleaning...
	$(call OS.REMOVE_DIR, $(OUTPUT_DIR))
	@echo Done.

