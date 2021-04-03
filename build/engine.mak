# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

# Format build inputs
SOURCES:=$(wildcard $(strip $(SOURCES)))
INCLUDES:=$(strip $(INCLUDES))
DUMMY_INTERFACES:=$(strip $(DUMMY_INTERFACES))
DEFINES:=$(addprefix -D,$(strip $(DEFINES)))
DEPENDENT_DUMMY_HEADERS:=$(addprefix $(DUMMIES_DIR)/,$(DUMMY_INTERFACES))
DEPENDENT_PRODUCT_HEADERS:=$(wildcard $(addsuffix /*.h,$(INCLUDES)))
SOURCE_DIRS:=$(sort $(dir $(SOURCES)))


# Declare build outputs
DUMMY_HEADERS := $(addprefix $(HEADERS_DIR)/, $(notdir $(DEPENDENT_DUMMY_HEADERS)))
PRODUCT_HEADERS := $(addprefix $(HEADERS_DIR)/,$(notdir $(DEPENDENT_PRODUCT_HEADERS)))
HEADERS := $(DUMMY_HEADERS) $(PRODUCT_HEADERS)
OBJECTS := $(addprefix $(OBJECTS_DIR)/,$(subst .c,.$(TOOLS.OBJEXT),$(notdir $(SOURCES))))
DEPENDENCIES := $(subst .$(TOOLS.OBJEXT),.d,$(OBJECTS)))
EXECUTABLE := $(BINARY_DIR)/$(OUTPUT_EXEC)

$(info  )
$(info Building '$(firstword $(MAKEFILE_LIST))' for '$(PRODUCT_FLAVOR)')
$(info $(if $(TOOLS.NAME),with <tools="$(TOOLS.NAME)">,)...)

define NEW_LINE_BREAK


endef

RECOMPILE_COMMAND=$(eval OBJECT_FILE=$(OBJECTS_DIR)/$(notdir $(SOURCE_FILE:.c=.$(TOOLS.OBJEXT)))) $(TOOLS.COMPILE)

ifdef COPY_HEADERS
TRANSFER_HEADER=$(OS.COPY)
else
TRANSFER_HEADER=$(OS.LINK)
endif

.PHONY: build rebuild link recompile


build: $(EXECUTABLE)
	@echo $(if $(LINKING_DONE),Done.,Up-to-date already.)


%/ :
	$(call OS.MAKE_DIR,$@)


$(EXECUTABLE) : $(OBJECTS) | $(BINARY_DIR)/
	@echo Linking...
	$(TOOLS.LINK)
	$(eval LINKING_DONE="TRUE")


rebuild: $(HEADERS) | $(OBJECTS_DIR)/ $(BINARY_DIR)/
	@echo Compiling all...
	$(shell FOR %f in ($(SOURCES)) DO @echo File: %f)
	$(foreach SOURCE_FILE,$(SOURCES),$(RECOMPILE_COMMAND) $(NEW_LINE_BREAK))
	@echo Linking...
	$(TOOLS.LINK)
	@echo Done.

$(DUMMY_HEADERS) : | $(filter clean, $(MAKECMDGOALS)) $(DEPENDENT_DUMMY_HEADERS) $(HEADERS_DIR)/
	$(call TRANSFER_HEADER,$(DUMMIES_DIR)/$(@F),$@)

define composeIncludesRule
$(HEADERS_DIR)/%.h : | $(filter clean, $(MAKECMDGOALS)) $(1)/%.h $(HEADERS_DIR)/
	$$(call TRANSFER_HEADER,$(1)/$$(@F),$$@)
endef
$(foreach includeDir,$(INCLUDES),$(eval $(call composeIncludesRule,$(includeDir))))

ifeq ("$(filter rebuild, $(MAKECMDGOALS))", "")

$(OBJECTS_DIR)/%.d : $(HEADERS)
	@echo $(subst .d,.c,$(@F))

define composeCompilationRule
$(OBJECTS_DIR)/%.$(TOOLS.OBJEXT) : $(1)%.c $(OBJECTS_DIR)/%.d $(STAT_AUTO_MAKEFILE) | $(OBJECTS_DIR)/
	$$(eval SOURCE_FILE=$$<)
	$$(eval OBJECT_FILE=$$@)
	$$(eval DEP_FILE=$$(subst .$$(TOOLS.OBJEXT),.d,$$@))
	$$(TOOLS.COMPILE)
endef
$(foreach sourceDir,$(SOURCE_DIRS),$(eval $(call composeCompilationRule,$(sourceDir))))

include $(wildcard $(DEPENDENCIES))

endif

.PRECIOUS: $(OBJECTS_DIR)/%.d | $(BINARY_DIR)/ $(OBJECTS_DIR)/ $(HEADERS_DIR)/
