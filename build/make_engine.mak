# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

# Format build inputs
DEFINES := $(addprefix -D, $(DEFINES))
INCLUDE_DIRS := $(sort $(DUMMIES_DIR) $(INCLUDES))
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


.PHONY: build rebuild


build: $(EXECUTABLE)
	@echo ...complete.


rebuild: $(HEADERS) | $(BINARY_DIR)/ $(HEADERS_DIR)/ $(OBJECTS_DIR)/
	@echo Re-compile...
	$(foreach SOURCE_FILE, $(SOURCES), $(COMPILE_COMMAND_LINE) $(NEW_LINE_BREAK))
	@echo Re-link...
	$(LINK_COMMAND_LINE)


%/ :
	$(eval NEW_DIRECTORY=$@)
	$(MKDIR_COMMAND_LINE)


$(EXECUTABLE) : $(HEADERS) $(SOURCES) $(OBJECTS) $(STAT_AUTO_MAKEFILE) | $(BINARY_DIR)/
	@echo Linking...
	$(LINK_COMMAND_LINE)


define composeIncludesRule
$(HEADERS_DIR)/%.h : $(1)/%.h | $(HEADERS_DIR)/
	$$(eval SOURCE_HEADER=$$<)
	$$(eval TARGET_HEADER=$$@)
	$(if $(COPY_HEADERS), $$(HEADER_COPY_COMMAND_LINE), $$(HEADER_LINK_COMMAND_LINE))
endef
$(foreach includeDir, $(INCLUDE_DIRS), $(eval $(call composeIncludesRule, $(includeDir))))


define composeCompilationRule
$(OBJECTS_DIR)/%.d : $(1)%.c $(STAT_AUTO_MAKEFILE) | $(OBJECTS_DIR)/
	$$(eval SOURCE_FILE=$$<)
	$$(eval DEP_FILE=$$@)
	$$(DEP_COMMAND_LINE)

$(OBJECTS_DIR)/%.$(OBJEXT) : $(1)%.c $(OBJECTS_DIR)/%.d $(STAT_AUTO_MAKEFILE)
	$$(eval SOURCE_FILE=$$<)
	$$(COMPILE_COMMAND_LINE)
endef
$(foreach sourceDir, $(SOURCE_DIRS), $(eval $(call composeCompilationRule, $(sourceDir))))

-include $(DEPENDENCIES)

.PRECIOUS: $(OBJECTS_DIR)/%.d | $(BINARY_DIR)/ $(OBJECTS_DIR)/ $(HEADERS_DIR)/
