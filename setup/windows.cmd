@echo off
setlocal
rem Double-click fallback for helpers: runs the same setup as "Follow SETUP.md".
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows.ps1"
set "RESULT=%ERRORLEVEL%"
pause
endlocal & exit /b %RESULT%
