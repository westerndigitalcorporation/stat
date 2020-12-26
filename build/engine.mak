# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

# Format build inputs
DEFINES := $(addprefix -D, $(DEFINES))
INCLUDE_DIRS := $(DUMMIES_DIR) $(INCLUDES)
DEPENDENT_HEADERS := $(addprefix $(DUMMIES_DIR)/,$(DUMMY_INTERFACES)) $(wildcard $(addsuffix /*.h,$(INCLUDES)))
SOURCE_DIRS := $(sort $(dir $(SOURCES)))
SOURCES := $(wildcard $(SOURCES))

# Declare build outputs
HEADERS := $(addprefix $(HEADERS_DIR)/,$(notdir $(DEPENDENT_HEADERS)))
OBJECTS := $(addprefix $(OBJECTS_DIR)/,$(subst .c,.$(TOOLS.OBJEXT),$(notdir $(SOURCES))))
DEPENDENCIES := $(subst .$(TOOLS.OBJEXT),.d,$(OBJECTS)))
EXECUTABLE := $(BINARY_DIR)/$(OUTPUT_EXEC)

ifneq ("$(TOOLS.NAME)", "")
$(info <tools="$(TOOLS.NAME)">)
endif

define NEW_LINE_BREAK


endef


.PHONY: build rebuild link recompile


build: $(EXECUTABLE)


rebuild: recompile | link


%/ :
	$(call OS.MAKE_DIR, $@)


link: $(BINARY_DIR)/
	@echo Linking...
	$(TOOLS.LINK)


$(EXECUTABLE) : $(OBJECTS) | link


RECOMPILE_COMMAND=$(eval OBJECT_FILE=$(OBJECTS_DIR)/$(notdir $(SOURCE_FILE:.c=.$(TOOLS.OBJEXT)))) $(TOOLS.COMPILE)
recompile: $(HEADERS) | $(OBJECTS_DIR)/
	@echo Compiling all...
	$(foreach SOURCE_FILE, $(SOURCES), $(RECOMPILE_COMMAND) $(NEW_LINE_BREAK))


define composeIncludesRule
$(HEADERS_DIR)/%.h : | $(filter clean, $(MAKECMDGOALS)) $(1)/%.h $(HEADERS_DIR)/
	$(if $(COPY_HEADERS), $$(call OS.COPY, $(1)/$$(@F), $$@), $$(call OS.LINK, $(1)/$$(@F), $$@))
endef
$(foreach includeDir, $(INCLUDE_DIRS), $(eval $(call composeIncludesRule, $(includeDir))))

$(OBJECTS_DIR)/%.d : $(HEADERS)
	@echo $(subst .d,.c, $(@F))

define composeCompilationRule
$(OBJECTS_DIR)/%.$(TOOLS.OBJEXT) : $(1)%.c $(OBJECTS_DIR)/%.d $(STAT_AUTO_MAKEFILE) | $(OBJECTS_DIR)/
	$$(eval SOURCE_FILE=$$<)
	$$(eval OBJECT_FILE=$$@)
	$$(eval DEP_FILE=$$(subst .$$(TOOLS.OBJEXT),.d, $$@))
	$$(TOOLS.COMPILE)
endef
$(foreach sourceDir, $(SOURCE_DIRS), $(eval $(call composeCompilationRule, $(sourceDir))))

ifeq ("$(filter rebuild, $(MAKECMDGOALS))", "")
include $(wildcard $(DEPENDENCIES))
endif

.PRECIOUS: $(OBJECTS_DIR)/%.d | $(BINARY_DIR)/ $(OBJECTS_DIR)/ $(HEADERS_DIR)/
