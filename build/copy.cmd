:: # Standalone test (STAT) tools makefile
:: #
:: # SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
:: #                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
:: #
:: # SPDX-License-Identifier: MIT

@echo off
setlocal

set ITEMS_COUNT=0
:ARG_LOOP
set "ARGUMENT=%~1"
set "FULL_PATHNAME=%~f1"
SHIFT /1
IF "%ARGUMENT%" EQU "" GOTO :NO_MORE_ARGS
IF "%ARGUMENT:~0,1%" EQU "-" (
    :: Named parameter
    set "OPTION_%ARGUMENT:~1%=TRUE"
) ELSE (
    :: Unnamed parameter (option)
    set COPY_ITEMS[%ITEMS_COUNT%]=%ARGUMENT:/=\%
    set INCLUDES_PATH=%FULL_PATHNAME:/=\%
    set /A ITEMS_COUNT+=1
)
GOTO :ARG_LOOP
:NO_MORE_ARGS

IF DEFINED OPTION_h (
    echo This script mimics basics of Linux 'cp' command
    echo Usage: copy.cmd [OPTION]... SOURCE DESTINATION
    echo        copy.cmd [OPTION]... SOURCE [SOURCE] DIRECTORY
    echo.
    echo Command line options:
    echo    -h - show this help screen
    echo    -n - do not overwrite the existing files
    echo    -s - create symbolic links instead of copying files
    exit /B
)

IF %ITEMS_COUNT% LEQ 1 (
    echo ERROR: No source or destination has been specified!
    exit /B
)

setlocal EnableDelayedExpansion

set /A LAST_SOURCE_INDEX=%ITEMS_COUNT%-2
set COPY_SOURCES=
FOR /L %%a in (0,1,%LAST_SOURCE_INDEX%) DO set COPY_SOURCES=!COPY_SOURCES! "!COPY_ITEMS[%%a]!"


IF DEFINED OPTION_s (
    :: If symbolic link shall be created instead of copying
    IF DEFINED OPTION_n (
        FOR %%F IN (%COPY_SOURCES%) DO IF NOT EXIST "%INCLUDES_PATH%\%%~nxF" (
            mklink "%INCLUDES_PATH%\%%~nxF" "%%~fF"
        )
    ) ELSE (
        FOR %%F IN (%COPY_SOURCES%) DO (
            IF EXIST "%INCLUDES_PATH%\%%~nxF" del /q /f "%INCLUDES_PATH%\%%~nxF"
            mklink "%INCLUDES_PATH%\%%~nxF" "%%~fF"
        )
    )
) ELSE (
    :: If regular copying was requested
    IF DEFINED OPTION_n (
        FOR %%F IN (%COPY_SOURCES%) DO IF NOT EXIST "%INCLUDES_PATH%\%%~nxF" copy /Y "%%~fF" "%INCLUDES_PATH%\%%~nxF"
    ) ELSE (
        FOR %%F IN (%COPY_SOURCES%) DO copy /Y "%%~fF" "%INCLUDES_PATH%\%%~nxF"
    )
)
