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
OBJECTS := $(addprefix $(OBJECTS_DIR)/,$(subst .c,.$(OBJEXT),$(notdir $(SOURCES))))
DEPENDENCIES := $(subst .$(OBJEXT),.d,$(OBJECTS)))
EXECUTABLE := $(BINARY_DIR)/$(OUTPUT_EXEC)

define NEW_LINE_BREAK


endef


.PHONY: build rebuild link recompile


build: $(EXECUTABLE)


rebuild: recompile | link


%/ :
	$(eval NEW_DIRECTORY=$@)
	$(CREATE.directory)


link: $(BINARY_DIR)/
	@echo Linking...
	$(LINK_COMMAND_LINE)


$(EXECUTABLE) : $(OBJECTS) | link


RECOMPILE_COMMAND=$(eval OBJECT_FILE=$(OBJECTS_DIR)/$(notdir $(SOURCE_FILE:.c=.$(OBJEXT)))) $(COMPILE_COMMAND_LINE)
recompile: $(HEADERS) | $(OBJECTS_DIR)/
	@echo Compiling all...
	$(foreach SOURCE_FILE, $(SOURCES), $(RECOMPILE_COMMAND) $(NEW_LINE_BREAK))


define composeIncludesRule
$(HEADERS_DIR)/%.h : | $(filter clean, $(MAKECMDGOALS)) $(1)/%.h $(HEADERS_DIR)/
	$$(eval SOURCE_HEADER=$(1)/$$(@F))
	$$(eval TARGET_HEADER=$$@)
	@echo $$(SOURCE_HEADER) == $$(TARGET_HEADER)
	$(if $(COPY_HEADERS), $$(HEADER_COPY_COMMAND_LINE), $$(HEADER_LINK_COMMAND_LINE))
endef
$(foreach includeDir, $(INCLUDE_DIRS), $(eval $(call composeIncludesRule, $(includeDir))))


define composeCompilationRule
$(OBJECTS_DIR)/%.d : $(1)%.c $(HEADERS) | $(OBJECTS_DIR)/
	$$(eval SOURCE_FILE=$$<)
	$$(eval DEP_FILE=$$@)
	$$(DEP_COMMAND_LINE)

$(OBJECTS_DIR)/%.$(OBJEXT) : $(1)%.c $(STAT_AUTO_MAKEFILE)
	@echo $$(<F)
	$$(eval SOURCE_FILE=$$<)
	$$(eval OBJECT_FILE=$$@)
	$$(COMPILE_COMMAND_LINE)
endef
$(foreach sourceDir, $(SOURCE_DIRS), $(eval $(call composeCompilationRule, $(sourceDir))))

ifeq ("$(filter rebuild, $(MAKECMDGOALS))", "")
-include $(DEPENDENCIES)
endif

.PRECIOUS: $(OBJECTS_DIR)/%.d | $(BINARY_DIR)/ $(OBJECTS_DIR)/ $(HEADERS_DIR)/
