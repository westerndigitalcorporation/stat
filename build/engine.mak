# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

# Build inputs
SOURCES:=$(wildcard $(strip $(SOURCES)))
INCLUDES:=$(addsuffix /,$(strip $(INCLUDES)))
INCLUDES:=$(INCLUDES://=/)
DUMMY_INTERFACES:=$(wildcard $(addprefix $(DUMMIES_DIR)/,$(DUMMY_INTERFACES)))
DEFINES:=$(addprefix -D,$(strip $(DEFINES)))
SOURCE_DIRS:=$(sort $(dir $(SOURCES)))

# Build outputs
ALL_OUTPUT_DIRS:=$(HEADERS_DIR) $(OBJECTS_DIR) $(BINARY_DIR)
OBJECTS:=$(addprefix $(OBJECTS_DIR)/,$(subst .c,.$(TOOLS.OBJEXT),$(notdir $(SOURCES))))
DEPENDENCIES:=$(subst .$(TOOLS.OBJEXT),.d,$(OBJECTS)))
EXECUTABLE:=$(BINARY_DIR)/$(OUTPUT_EXEC)
TIMESTAMP_FILE:=$(basename $(EXECUTABLE)).txt

# Break-line variable for multiline output of iterative processes
define NEW_LINE_BREAK


endef

# Operation definitions
RECOMPILE_COMMAND=$(eval OBJECT_FILE=$(OBJECTS_DIR)/$(notdir $(SOURCE_FILE:.c=.$(TOOLS.OBJEXT)))) $(TOOLS.COMPILE)
COPY_METHOD_FLAGS:=$(if $(INSTALL_BY_COPY),-p,-p -s)

# Cleanup prerequisite according to make commandline targets
PRECEDING_CLEANUP:=$(filter clean, $(MAKECMDGOALS))
ifneq ($(filter rebuild, $(MAKECMDGOALS)),)
PRECEDING_CLEANUP:=$(if $(PRECEDING_CLEANUP),$(PRECEDING_CLEANUP),cleanup_headers)
endif


$(info  )
$(info Building '$(firstword $(MAKEFILE_LIST))' for '$(PRODUCT_FLAVOR)')
$(info $(if $(TOOLS.NAME),with <tools="$(TOOLS.NAME)">,)...)


.PHONY: build rebuild cleanup_headers


build: $(EXECUTABLE) | $(PRECEDING_CLEANUP) $(ALL_OUTPUT_DIRS)
	@echo $(if $(LINKING_DONE),Done.,Up-to-date already.)


rebuild: $(PRECEDING_CLEANUP) $(ALL_OUTPUT_DIRS)
	@echo Installing dependencies...
	$(call OS.COPY,-n $(COPY_METHOD_FLAGS),$(DUMMY_INTERFACES),$(HEADERS_DIR))
	$(call OS.COPY,-n $(COPY_METHOD_FLAGS),$(foreach _dir_,$(INCLUDES),$(_dir_)*.h),$(HEADERS_DIR))
	@echo Compiling all...
	$(foreach SOURCE_FILE,$(SOURCES),$(RECOMPILE_COMMAND) $(NEW_LINE_BREAK))
	@echo Linking...
	$(TOOLS.LINK)
	@echo Done.


$(ALL_OUTPUT_DIRS): | $(PRECEDING_CLEANUP)
	$(call OS.MAKE_DIR,$@)


# Set incremental build targets, if not a rebuild target was sepcified explicitely
ifeq ($(filter rebuild, $(MAKECMDGOALS)),)

# Organize headers according to requested order to take proper test-double headers to replace the production files
ORIGINAL_HEADERS:=$(DUMMY_INTERFACES)
define addIncludePath
ORIGINAL_HEADERS+=$$(filter-out $$(addprefix $(1),$$(notdir $$(ORIGINAL_HEADERS))), $$(wildcard $(1)*.h))
endef
$(foreach includeDir,$(INCLUDES),$(eval $(call addIncludePath,$(includeDir))))
INCLUDE_DIRS:=$(sort $(dir $(ORIGINAL_HEADERS)))
TARGET_HEADERS:=$(addprefix $(HEADERS_DIR)/,$(notdir $(ORIGINAL_HEADERS)))

$(EXECUTABLE) : $(OBJECTS) | $(ALL_OUTPUT_DIRS) $(TIMESTAMP_FILE)
	@echo Linking...
	$(TOOLS.LINK)
	$(file >$(TIMESTAMP_FILE),$?)
	$(eval LINKING_DONE="TRUE")

$(OBJECTS): | $(ALL_OUTPUT_DIRS) $(TIMESTAMP_FILE)

#$(TIMESTAMP_FILE): $(ORIGINAL_HEADERS) | $(ALL_OUTPUT_DIRS)
#	@echo Updating outdated headers...
#	$(eval CHANGED_HEADERS=$?)
#	$(foreach headerFile,$(CHANGED_HEADERS),$(call OS.COPY,$(COPY_METHOD_FLAGS),$(headerFile),$(HEADERS_DIR)) $(NEW_LINE_BREAK))

# Header installation macro
define installHeaders
$(eval FILES_TO_COPY=$(filter $(1)%.h,$(CHANGED_HEADERS)))
$(foreach headerFile,$(FILES_TO_COPY),$(call OS.COPY,$(COPY_METHOD_FLAGS),$(headerFile),$(HEADERS_DIR)) $(NEW_LINE_BREAK))
endef

$(TIMESTAMP_FILE): $(ORIGINAL_HEADERS) | $(ALL_OUTPUT_DIRS)
	@echo Updating outdated headers...
	$(eval CHANGED_HEADERS=$?)
	$(eval CHANGED_INCLUDES:=$(sort $(dir $(CHANGED_HEADERS))))
	$(foreach includeDir,$(CHANGED_INCLUDES),$(call installHeaders,$(includeDir)) $(NEW_LINE_BREAK))

$(OBJECTS_DIR)/%.d:
	@echo $@>$(OS.NULL_OUTPUT)

# Compilation macro for dynamic creation of compilation targets per source folder
define composeCompilationRule
$(OBJECTS_DIR)/%.$(TOOLS.OBJEXT): $(1)%.c $(OBJECTS_DIR)/%.d | $(ALL_OUTPUT_DIRS)
	$$(eval SOURCE_FILE=$$<)
	$$(eval OBJECT_FILE=$$@)
	$$(eval DEP_FILE=$$(subst .$$(TOOLS.OBJEXT),.d,$$@))
	$$(TOOLS.COMPILE)
endef
$(foreach sourceDir,$(SOURCE_DIRS),$(eval $(call composeCompilationRule,$(sourceDir))))

# Include dependency files (if ready)
include $(wildcard $(DEPENDENCIES))

endif

cleanup_headers:
	$(call OS.REMOVE_DIR, $(HEADERS_DIR))

.PRECIOUS: $(OBJECTS_DIR)/%.d | $(BINARY_DIR) $(OBJECTS_DIR) $(HEADERS_DIR)
