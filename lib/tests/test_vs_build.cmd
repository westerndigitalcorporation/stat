@echo off
for /f usebackq^ tokens^=2^ delims^=^" %%i in (`makestat.py -p lib stat_mock.mak -vs`) do set solution=%%i
for /f "usebackq tokens=1* delims=: " %%i in (`..\..\resources\vswhere.exe -latest -requires Microsoft.VisualStudio.Workload.NativeDesktop`) do (
	if /i "%%i"=="productPath" set ide=%%j
)
if "%solution%"=="" (
	echo Failed to create a VS solution file.
	exit 1
)
if "%ide%"=="" (
	echo Failed to retrieve the location of devenv.ext file.
	exit 1
)
echo Building...
"%ide%" "%solution%" /Rebuild