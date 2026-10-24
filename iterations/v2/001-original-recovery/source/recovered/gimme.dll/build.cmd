@echo off
rem Builds the recovered gimme.dll into %1:
rem   gimme-faithful.dll  original behaviour, including the descriptor-copy defect
rem   gimme-fixed.dll     same sources with GIMEX_FIX_DESCRIPTOR_COPY
rem   gimme_oracle.exe    recovered code (faithful) linked with the differential harness
rem Flags: static debug CRT like the original (libcmtd: same heap block framing), x87 floating
rem point (/arch:IA32) so the host's FPU control word applies as it does to the original.
setlocal enabledelayedexpansion
set OUT=%~1
if "%OUT%"=="" (echo usage: build.cmd ^<output dir^> & exit /b 2)
if not exist "%OUT%\faithful" mkdir "%OUT%\faithful"
if not exist "%OUT%\fixed" mkdir "%OUT%\fixed"
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat" >nul || exit /b 1
set ROOT=%~dp0
rem The source list goes through a response file: it is longer than a cmd line allows.
set SOURCES=%OUT%\sources.rsp
if exist "%SOURCES%" del "%SOURCES%"
for /f "usebackq eol=# tokens=*" %%S in ("%ROOT%sources.txt") do echo "%ROOT%%%S">>"%SOURCES%"
set FLAGS=/nologo /c /Od /Oy- /arch:IA32 /fp:precise /MTd /W3 /EHsc /GS- /D_CRT_SECURE_NO_WARNINGS /D_CRT_NONSTDC_NO_WARNINGS
cl %FLAGS% /Fo"%OUT%\faithful\\" @"%SOURCES%" || exit /b 1
cl %FLAGS% /DGIMEX_FIX_DESCRIPTOR_COPY /Fo"%OUT%\fixed\\" @"%SOURCES%" || exit /b 1
set LFLAGS=/nologo /DLL /BASE:0x10000000 /DYNAMICBASE:NO /INCREMENTAL:NO
link %LFLAGS% /OUT:"%OUT%\gimme-faithful.dll" "%OUT%\faithful\*.obj" user32.lib || exit /b 1
link %LFLAGS% /OUT:"%OUT%\gimme-fixed.dll" "%OUT%\fixed\*.obj" user32.lib || exit /b 1
if not exist "%OUT%\faithful\oracle" mkdir "%OUT%\faithful\oracle"
cl %FLAGS% /Fo"%OUT%\faithful\oracle\\" "%ROOT%oracle\*.cpp" || exit /b 1
link /nologo /OUT:"%OUT%\gimme_oracle.exe" /BASE:0x00400000 /DYNAMICBASE:NO /INCREMENTAL:NO "%OUT%\faithful\oracle\*.obj" "%OUT%\faithful\*.obj" user32.lib || exit /b 1
echo built %OUT%
