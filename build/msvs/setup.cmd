:: Standalone test (STAT) tools makefile
::
:: SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
::                             Arseniy Aharonov <arseniy.aharonov@gmail.com>
::
:: SPDX-License-Identifier: MIT

@echo OFF
setlocal EnableExtensions
SET STAT_MSVS_IN_LOOP=YES
call "%MSVS_DEV:/=\%" >nul
%*
endlocal
