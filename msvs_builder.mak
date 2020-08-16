# Standalone test (STAT) tools makefile
#
# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
#
# SPDX-License-Identifier: MIT

# Target executable
EXECUTABLE="$(BINARY_DIR)/$(OUTPUT_EXEC)"

# Build default target
build : $(EXECUTABLE)

# Include dependency files with rules for incremental compilation
!INCLUDE $(DEP_INCLUSIONS)

build_upon_demand:
	call <<$(OUTPUT_DIR)/build_upon_demand.bat
	@echo off
	IF NOT ""=="%SOURCES_TO_REBUILD%" (
		echo Compile affected sources...
		@$(CC) $(CFLAGS) $(DEFINES) -Fd$(OBJECTS_DIR)\ -I$(INCLUDES_DIR)\ /Fo$(OBJECTS_DIR)\ %SOURCES_TO_REBUILD%
		echo Linking target...
		IF EXIST $(BINARY_DIR:/=\) @DEL /Q /F $(BINARY_DIR:/=\)\*.* >nul
		LINK /NOLOGO /DEBUG $(OBJECTS_DIR)\*.obj /out:$(EXECUTABLE)
	)
<<NOKEEP

# Link target upon changes
$(EXECUTABLE) : $(OBJ_FILES) build_upon_demand
