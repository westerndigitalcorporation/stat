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
	echo Collecting dependent headers...
	set INCLUDES_PATH=.\$(INCLUDES_DIR:/=\)
	FOR %%F IN ($(DEPENDENT_HEADERS:/=\)) DO @IF NOT EXIST "%INCLUDES_PATH%\%%~nxF" mklink "%INCLUDES_PATH%\%%~nxF" "%%~pnxF" >nul

# Copy proper versions of header-files
copy_headers :
	echo Collecting dependent headers...
	set INCLUDES_PATH=.\$(INCLUDES_DIR:/=\)
	FOR %%F IN ($(DEPENDENT_HEADERS:/=\)) DO @IF NOT EXIST "%INCLUDES_PATH%\%%~nxF" copy /Y "%%~pnxF" "%INCLUDES_PATH%\%%~nxF" >nul

# Invoke incremental compilation and linkage
build : $(DEP_INCLUSIONS)
	$(MAKE) /F"$(TOOL_DIR)/msvs_builder.mak" @$(OUTPUT_DIR)/arguments.mak

# Re-compile all sources and re-link the target
rebuild :
	echo Compiling sources...
	$(CC) $(CFLAGS) $(DEFINES) -Fd$(OBJECTS_DIR)\ -I$(INCLUDES_DIR)\ /Fo$(OBJECTS_DIR)\ @<<$(OUTPUT_DIR)/cc_response.txt
$(SOURCES: =^
)
<<NOKEEP
	echo Linking target...
	LINK /NOLOGO /DEBUG /WX @<<$(OUTPUT_DIR)/link_response.txt /out:$(EXECUTABLE)
$(OBJ_FILES: =^
)
<<NOKEEP

# Collect proper versions of header-files and update the collection if needed
$(EXECUTABLE) :: $(DEPENDENT_HEADERS)
	setlocal EnableExtensions
	echo Handling dependencies ...
	set INCLUDES_PATH=.\$(INCLUDES_DIR:/=\)
	FOR %%G IN ( $(?B) ) DO @IF EXIST %INCLUDES_PATH%\%%~G.h del /Q /F "%INCLUDES_PATH%%\%~G.h" >nul

# Track changes in dependency files with compilation rules
$(DEP_INCLUSIONS) : $(DEP_FILES)
	echo Tracking changes ...
	echo # Include files with dependency rules for object-files >$(DEP_INCLUSIONS)
	FOR %%G in ( $(DEP_FILES) ) DO @echo !INCLUDE %%G >>$(DEP_INCLUSIONS)

# Track changes in source files
$(DEP_FILES) : $(SOURCES)
	FOR %%G in ( $? ) DO @IF "%%~nG" == "$(@B)" PowerShell -NoProfile -ExecutionPolicy Bypass -File <<$(OUTPUT_DIR)/build_dep.ps1 -source "%%G" -depFile "$@" -objFile "$(@:.dep=.obj)"
	Param([string]$$source, [string]$$depFile, [string]$$objFile)
	$$dependencies=($(CC) /nologo /Fonul /EHar /showIncludes /I$(INCLUDES_DIR) $$source 2>&1 | %{ [Regex]::Matches($$_, "$(INCLUDES_DIR).*\.h") } | %{ $$_.Value }) -join ' '
	@(("$$objFile : $$source  $$dependencies"), ("	`$$(CC) `$$(CFLAGS) `$$(DEFINES) $$source -Fd`$$(OBJECTS_DIR)\ -I`$$(INCLUDES_DIR)\ /Fo$$objFile") ) | Set-Content -Path ($$depFile)
<<NOKEEP
