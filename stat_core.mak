# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

# Override compiler macros
CFLAGS=/c /WX /W3 /Zi /nologo

# Sanity check
!IF "$(PRIVATE_NAME)" == ""
!ERROR "PRIVATE_NAME variable has to be defined!"
!ENDIF

# Intermediate output directories
OUTPUT_DIR = $(OUTPUT_DIR)/$(OUTPUT_NAME)/$(PRIVATE_NAME)
INCLUDES_DIR = $(OUTPUT_DIR)/inc
OBJECTS_DIR = $(OUTPUT_DIR)/obj
BINARY_DIR = $(OUTPUT_DIR)/bin

# Main file that includes all dependency files
DEP_INCLUSIONS=$(OBJECTS_DIR)/all_dependencies.dep

# Default build target set by command-line
default_build : set_default_build all

# Default rebuild target set by command-line
default_rebuild : set_default_rebuild all

# Build target set within IDE
build : set_build all

# Rebuild target set within IDE
rebuild : set_rebuild all

# Clean-up target
clean :
	echo Cleaning...
	:: # Delete files within output directories
	set OUTPUT_DIRS=$(INCLUDES_DIR:/=\) $(OBJECTS_DIR:/=\) $(BINARY_DIR:/=\) $(OUTPUT_DIR:/=\)
	FOR %%D in ( %%OUTPUT_DIRS%% ) DO @IF EXIST %%D @DEL /Q /F %%D\*.* >nul


### Internal helper targets

set_default_build:
	echo:
	echo "Building ""$(PRIVATE_NAME)"" for ""$(OUTPUT_NAME)"" ..."
	set STAT_METHOD_INCLUDE=copy_headers
	set STAT_METHOD_BUILD=incremental_build

set_default_rebuild :
	echo:
	echo "Rebuilding ""$(PRIVATE_NAME)"" for ""$(OUTPUT_NAME)""..."
	set STAT_METHOD_INCLUDE=copy_headers
	set STAT_METHOD_BUILD=full_build

set_build :
	set STAT_METHOD_INCLUDE=link_headers
	set STAT_METHOD_BUILD=incremental_build

set_rebuild :
	set STAT_METHOD_INCLUDE=link_headers
	set STAT_METHOD_BUILD=full_build


### Call MSVS main makefile
all :
	IF NOT EXIST $(OUTPUT_DIR:/=\) MD $(OUTPUT_DIR:/=\) >nul
	call <<$(OUTPUT_DIR)/stat_msvs.bat <<$(OUTPUT_DIR)/arguments.mak
	@echo off
	IF NOT EXIST $(OBJECTS_DIR:/=\) (IF "%STAT_METHOD_BUILD%"=="incremental_build" (set STAT_METHOD_BUILD=full_build))
	IF "%STAT_METHOD_BUILD%"=="incremental_build" (
		set STAT_MAKE_ARGUMENTS=update %STAT_METHOD_INCLUDE% incremental_build
	) ELSE (
		set STAT_MAKE_ARGUMENTS=/A clean_headers %STAT_METHOD_INCLUDE% full_build
	)
	:: # Create output directories
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
	set DEPENDENT_HEADERS=%DEPENDENT_DUMMIES% %DEPENDENT_INCLUDES%
	set OBJ_FILES=& FOR %%G IN ( $(SOURCES) ) DO set OBJ_FILES=!OBJ_FILES! $(OBJECTS_DIR)/%%~nG.obj
	::
	:: # Add convenience list-variables to the file with NMAKE command-line arguments
	FOR %%G IN (DEFINES DEPENDENT_HEADERS OBJ_FILES) DO call :add_to_arguments_file %%G %1
	::
	:: # Invoke execution of the main NMAKE-based makefile-script
	::
	$(MAKE) /F"$(TOOL_DIR)/msvs_main.mak" @%1 %STAT_MAKE_ARGUMENTS%& endlocal& GOTO :eof
	::
	:: ### Helper subroutines for list expansion and formatting
	::
	:format_list_of_values # arguments: target_name source_list prefix suffix
	setlocal EnableDelayedExpansion
	set TEMP_TARGET_LIST=
	set TEMP_SOURCE_ITEMS=%~2
	FOR %%G IN ("%TEMP_SOURCE_ITEMS: =" "%") DO (IF NOT "%%~G" == "" set TEMP_TARGET_LIST=!TEMP_TARGET_LIST! %~3%%~G%~4)
	endlocal& set %~1=%TEMP_TARGET_LIST%& EXIT /B
	::
	:add_to_arguments_file # arguments: variable_name arguments_file_name
	setlocal EnableDelayedExpansion& call :trim_whitespaces %%%1%%
	endlocal& echo %1="%TRIMMED_VARIABLE_VALUE%" \>>%2
	EXIT /B
	::
	:trim_whitespaces
	set TRIMMED_VARIABLE_VALUE=%*& EXIT /B
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
