:: SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
::                             Arseniy Aharonov <arseniy@aharonov.icu>
::
:: SPDX-License-Identifier: MIT

@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION
SET CWD=/%CD::=%
SET CWD=!CWD:\=/!
docker run --volume %CWD%:/data fsfe/reuse lint