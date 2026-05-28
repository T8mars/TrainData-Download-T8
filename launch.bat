@echo off
setlocal
cd /d "%~dp0"

wscript.exe "%~dp0tools\launch_gui_hidden.vbs"
exit /b 0
