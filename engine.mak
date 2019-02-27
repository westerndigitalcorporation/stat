# Standalone test (STAT) tools makefile

# Intermediate target directories
INCLUDES_DIR=$(OUTPUT_DIR)\inc
OBJECTS_DIR=$(OUTPUT_DIR)\obj
BINARY_DIR=$(OUTPUT_DIR)\bin

# Target executable
EXEC=$(BINARY_DIR)\$(NAME).exe

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

rebuild: clean build

# Build rule
build: prepare
    @ECHO $@...
    call <<vswrapper.bat $(CC) $(CFLAGS) $(SOURCES) -I$(INCLUDES_DIR)\ /Fo$(OBJECTS_DIR)\ /Fe"$(EXEC)"
@ECHO OFF
PUSHD $(VS_TOOL:/=\)
CALL VCVARSALL.BAT >NUL
POPD
%*
<<NOKEEP
    
# Rule for cleaning
clean:
    @ECHO $@...
    IF EXIST $(INCLUDES_DIR) @DEL /Q /F $(INCLUDES_DIR)\*.* >nul
    IF EXIST $(OBJECTS_DIR) @RMDIR /Q /S $(OBJECTS_DIR)
    IF EXIST $(BINARY_DIR) @RMDIR /Q /S $(BINARY_DIR)
    IF EXIST *.pdb del *.pdb

# Rule for preparing to build
prepare:
    @ECHO $@ for [$(NAME)]...
    IF NOT EXIST $(OUTPUT_DIR) MD $(OUTPUT_DIR)
    IF NOT EXIST $(OBJECTS_DIR) MD $(OBJECTS_DIR)
    IF NOT EXIST $(INCLUDES_DIR) MD $(INCLUDES_DIR)
    IF NOT EXIST $(BINARY_DIR) MD $(BINARY_DIR)
    FOR %%d IN ($(DUMMIES_DIR)) DO @FOR %%f IN ($(DUMMIES:/=\)) DO @IF NOT EXIST "$(INCLUDES_DIR)\%%~nxf" @MKLINK "$(INCLUDES_DIR)\%%~nxf" "%%~dpnd\%%f" >nul
    FOR %%d IN ($(INCLUDES:/=\)) DO @FOR %%f IN (%%d\*.*) DO @IF NOT EXIST "$(INCLUDES_DIR)\%%~nxf" (@MKLINK "$(INCLUDES_DIR)\%%~nxf" "%%~dpnxf" >nul)
