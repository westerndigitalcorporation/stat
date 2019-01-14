# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

!IF "$(PRIVATE_NAME)" == ""
TARGET_DIR = $(OUTPUT_DIR)
!ELSE
TARGET_DIR = $(OUTPUT_DIR)\$(PRIVATE_NAME)
!ENDIF

# Intermediate target directories
INCLUDES_DIR=$(TARGET_DIR)\inc
OBJECTS_DIR=$(TARGET_DIR)\obj
BINARY_DIR=$(TARGET_DIR)\bin

# Target executable
EXEC=$(BINARY_DIR)\$(OUTPUT_EXEC)

# Prepare the original items requiring formatting for the very formatting
LIST_INCLUDES=$(INCLUDES)
LIST_DEFINES=$(DEFINES)

# Include generated MAK-file to pack items requiring formatting
!INCLUDE $(TEMPFILE)

# Format the items that require formatting before being passed to the compiler
FORMATTED_DEFINES=$(LIST_DEFINES:]=)
FORMATTED_DEFINES=$(FORMATTED_DEFINES:[=-D)

# Override compiler macros...
CFLAGS=/WX /W3 /Zi /nologo $(FORMATTED_DEFINES)

# Build rule
build: prepare
    @ECHO $@...
    call <<vswrapper.bat $(CC) $(CFLAGS) $(SOURCES) -I$(INCLUDES_DIR)\ /Fo$(OBJECTS_DIR)\ /Fe"$(EXEC)"
@ECHO OFF
if "%VSINSTALLDIR%"=="" CALL "$(VS_DEV:/=\)" >NUL
%*
<<NOKEEP

rebuild: clean build
    
# Rule for cleaning
clean:
    @ECHO $@...
    IF EXIST $(INCLUDES_DIR) @DEL /Q /F $(INCLUDES_DIR)\*.* >nul
    IF EXIST $(OBJECTS_DIR) @RMDIR /Q /S $(OBJECTS_DIR)
    IF EXIST $(BINARY_DIR) @RMDIR /Q /S $(BINARY_DIR)
    IF EXIST *.pdb del *.pdb

# Rule for preparing to build
prepare:
    @ECHO $@ for [$(OUTPUT_NAME)]...
    IF NOT EXIST $(OBJECTS_DIR) MD $(OBJECTS_DIR)
    IF NOT EXIST $(INCLUDES_DIR) MD $(INCLUDES_DIR)
    IF NOT EXIST $(BINARY_DIR) MD $(BINARY_DIR)
    FOR %%d IN ($(DUMMIES_DIR)) DO @FOR %%f IN ($(DUMMIES:/=\)) DO @IF NOT EXIST "$(INCLUDES_DIR)\%%~nxf" @MKLINK "$(INCLUDES_DIR)\%%~nxf" "%%~dpnd\%%f" >nul
    FOR %%d IN ($(INCLUDES:/=\)) DO @FOR %%f IN (%%d\*.*) DO @IF NOT EXIST "$(INCLUDES_DIR)\%%~nxf" (@MKLINK "$(INCLUDES_DIR)\%%~nxf" "%%~dpnxf" >nul)
