# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

# Override compiler macros
CFLAGS=/FD /WX /W3 /Zi /c /nologo

# Sanity check
!IF "$(PRIVATE_NAME)" == ""
!ERROR "PRIVATE_NAME variable has to be defined!"
!ENDIF

# Intermediate output directories
OUTPUT_DIR = $(OUTPUT_DIR)/$(OUTPUT_NAME)/$(PRIVATE_NAME)
INCLUDES_DIR = $(OUTPUT_DIR)/inc
OBJECTS_DIR = $(OUTPUT_DIR)/obj
BINARY_DIR = $(OUTPUT_DIR)/bin

EXECUTABLE="$(BINARY_DIR)/$(OUTPUT_EXEC)"

# Main file that includes all dependency files
DEP_INCLUSIONS=$(OBJECTS_DIR)/all_dependencies.dep

# CLI build target (set by command-line)
cli_build : include_by_copy accomplish_build

# CLI rebuild target (set by command-line)
cli_rebuild : include_by_copy configure_full_rebuild accomplish_build

# Build target set within IDE
build : include_by_link accomplish_build

# Rebuild target set within IDE
rebuild : include_by_link configure_full_rebuild accomplish_build

# Clean-up target
clean :
	echo Cleaning...
	:: # Delete files within output directories
	set OUTPUT_DIRS=$(INCLUDES_DIR:/=\) $(OBJECTS_DIR:/=\) $(BINARY_DIR:/=\) $(OUTPUT_DIR:/=\)
	FOR %%D in ( %%OUTPUT_DIRS%% ) DO @IF EXIST %%D @DEL /Q /F %%D\*.* >nul


### Internal helper targets

include_by_copy:
	echo:
	echo "Building ""$(PRIVATE_NAME)"" for ""$(OUTPUT_NAME)"" ..."
	set STAT_INCLUDE_METHOD=copy_headers

include_by_link:
	set STAT_INCLUDE_METHOD=link_headers

configure_full_rebuild:
	set STAT_MAKE_TARGETS=/A clean %STAT_INCLUDE_METHOD% full_rebuild


### Call MSVS main makefile
accomplish_build :
	IF NOT EXIST $(OUTPUT_DIR:/=\) MD $(OUTPUT_DIR:/=\) >nul
	call <<$(OUTPUT_DIR)/stat_msvs.bat <<$(OUTPUT_DIR)/make_arguments.mak
	@echo off
	::
	:: # Remember name of argument files
	set STAT_MAKE_ARGUMENTS_FILE=%1
	set STAT_CC_ARGUMENTS_FILE=$(OBJECTS_DIR)/cc_arguments.txt
	IF EXIST %STAT_CC_ARGUMENTS_FILE% del /Q /F %STAT_CC_ARGUMENTS_FILE:/=\% >nul
	::
	:: # Configure build, if rebuild was not configured yet
	IF "%STAT_MAKE_TARGETS%"=="" (
		IF EXIST $(OBJECTS_DIR:/=\) (
			set STAT_MAKE_TARGETS=update %STAT_INCLUDE_METHOD% incremental_build
		) ELSE (
			set STAT_MAKE_TARGETS=/A clean %STAT_INCLUDE_METHOD% full_rebuild
		)
	)
	::
	:: # Create output directories if do not exist
	set OUTPUT_PATHS=$(INCLUDES_DIR:/=\) $(OBJECTS_DIR:/=\) $(BINARY_DIR:/=\)
	FOR %%D in ( %OUTPUT_PATHS% ) DO @IF NOT EXIST %%D MD %%D >nul
	::
	:: # Initialize MSVS build-command shell
	IF "%VSINSTALLDIR%"=="" call "$(VS_DEV:/=\)" >nul
	echo (tools: %VSINSTALLDIR%)
	::
	:: # Prepare convenience list-variables for all build-targets
	setlocal EnableDelayedExpansion
	call :format_list_of_values DEFINES "$(DEFINES)" "-D" ""
	call :format_list_of_values DEPENDENT_DUMMIES "$(DUMMY_INTERFACES)" "$(DUMMIES_DIR)/" ""
	call :format_list_of_values DEPENDENT_INCLUDES "$(INCLUDES)" "" "/*.h"
	set OBJ_FILES=& FOR %%G IN ( $(SOURCES) ) DO set OBJ_FILES=!OBJ_FILES! $(OBJECTS_DIR)/%%~nG.obj
	::
	:: # Invoke execution of the main NMAKE-based makefile-script
	$(MAKE) /F"$(TOOL_DIR)/msvs_main.mak" @%1 %STAT_MAKE_TARGETS%& endlocal& GOTO :eof
	::
	:: ### Helper subroutine for list expansion and formatting
	:format_list_of_values # arguments: target_name source_list prefix suffix
	setlocal EnableDelayedExpansion
	set TEMP_TARGET_LIST=
	set TEMP_SOURCE_ITEMS=%~2
	FOR %%G IN ("%TEMP_SOURCE_ITEMS: =" "%") DO (IF NOT "%%~G" == "" set TEMP_TARGET_LIST=!TEMP_TARGET_LIST! %~3%%~G%~4)
	endlocal& set %~1=%TEMP_TARGET_LIST%& EXIT /B
	::
<<NOKEEP
	/nologo /$(MAKEFLAGS) \
	CFLAGS="$(CFLAGS)" \
	TOOL_DIR="$(TOOL_DIR)" \
	SOURCES="$(SOURCES)" \
	INCLUDES_DIR="$(INCLUDES_DIR)" \
	OBJECTS_DIR="$(OBJECTS_DIR)" \
	BINARY_DIR="$(BINARY_DIR)" \
	OUTPUT_DIR="$(OUTPUT_DIR)" \
	OUTPUT_EXEC="$(OUTPUT_EXEC)" \
	DEP_INCLUSIONS="$(DEP_INCLUSIONS)" \
<<NOKEEP
