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

# Link target upon changes
$(EXECUTABLE) : $(OBJ_FILES)
