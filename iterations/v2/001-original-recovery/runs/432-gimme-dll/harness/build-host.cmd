@echo off
rem Builds the Run 432 native harness tools (x86) into %1.
setlocal
set OUT=%~1
if "%OUT%"=="" (echo usage: build-host.cmd ^<output dir^> & exit /b 2)
if not exist "%OUT%" mkdir "%OUT%"
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat" >nul || exit /b 1
for %%T in (gimme_host gimme_about) do (
  cl /nologo /O1 /W3 /D_CRT_SECURE_NO_WARNINGS /Fo"%OUT%\\" /Fe"%OUT%\%%T.exe" "%~dp0%%T.cpp" || exit /b 1
)
