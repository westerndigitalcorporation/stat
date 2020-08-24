# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

DEP_FILES=$(OBJ_FILES:.obj=.dep)
EXECUTABLE="$(BINARY_DIR)/$(OUTPUT_EXEC)"

# Track updates for incremental build
update : $(EXECUTABLE)

# Clear old dependent headers
clean_headers :
	set INCLUDES_PATH=.\$(INCLUDES_DIR:/=\)
	IF EXIST %INCLUDES_PATH% @DEL /Q /F %INCLUDES_PATH%\*.* >nul

# Create symbolic-links of proper versions of header-files
link_headers :
	set INCLUDES_PATH=.\$(INCLUDES_DIR:/=\)
	FOR %%F IN ($(DEPENDENT_HEADERS:/=\)) DO @IF NOT EXIST "%INCLUDES_PATH%\%%~nxF" mklink "%INCLUDES_PATH%\%%~nxF" "%%~pnxF" >nul

# Copy proper versions of header-files
copy_headers :
	set INCLUDES_PATH=.\$(INCLUDES_DIR:/=\)
	FOR %%F IN ($(DEPENDENT_HEADERS:/=\)) DO @IF NOT EXIST "%INCLUDES_PATH%\%%~nxF" copy /Y "%%~pnxF" "%INCLUDES_PATH%\%%~nxF" >nul

# Invoke incremental compilation and linkage
incremental_build : $(DEP_INCLUSIONS)
	$(MAKE) /$(MAKEFLAGS) /F"$(TOOL_DIR)/msvs_builder.mak" @$(OUTPUT_DIR)/arguments.mak

# Invoke fast full compilation and linkage
full_build :
	echo Compiling all sources...
	IF EXIST $(BINARY_DIR:/=\) @DEL /Q /F $(BINARY_DIR:/=\)\*.* >nul
	$(CC) $(CFLAGS) $(DEFINES) -Fd$(OBJECTS_DIR)\ -I$(INCLUDES_DIR)\ /Fo$(OBJECTS_DIR)\ @<<$(OUTPUT_DIR)/cc_response.txt
$(SOURCES: =^
)
<<NOKEEP
	echo Linking target...
	LINK /NOLOGO /DEBUG $(OBJECTS_DIR)\*.obj /out:$(EXECUTABLE)

# Collect proper versions of header-files and update the collection if needed
$(EXECUTABLE) : $(DEPENDENT_HEADERS)
	setlocal EnableExtensions
	echo Handling dependencies ...
	set INCLUDES_PATH=.\$(INCLUDES_DIR:/=\)
	set DEPENDENT_HEADER_NAMES=$(?B)
	FOR %%G IN ( %DEPENDENT_HEADER_NAMES% ) DO @IF EXIST %INCLUDES_PATH%\%%~G.h del /Q /F "%INCLUDES_PATH%%\%~G.h" >nul

# This target exists only to overcome bad coding of the programmers who create makefiles with bad syntax
$(DEPENDENT_HEADERS) :
	echo WARNING: Bad make-file syntax: inclusion path "$@" is incorrect!!!

# Track changes in dependency files with compilation rules
$(DEP_INCLUSIONS) : $(SOURCES)
	echo Track changes ...
	::
	call <<$(OUTPUT_DIR)/build_dep.bat
	@echo off
	setlocal EnableExtensions
	::
	:: # Erase old dependency file
	echo # Dependency targets >$(DEP_INCLUSIONS)
	::
	set SOURCES_NAMES=$(SOURCES)
	FOR %%G in ( %SOURCES_NAMES% ) DO @ (
		echo $(OBJECTS_DIR)/%%~nG.obj : "%%~fG" $(INCLUDES_DIR)/*.h
		echo   echo "%%~fG" ^>^>$(OBJECTS_DIR:/=\)\changed_sources.txt
	) >>$(DEP_INCLUSIONS)
<<NOKEEP
