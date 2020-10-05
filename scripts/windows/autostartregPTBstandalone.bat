@echo off
set scriptdir=%~dp0
set scriptname=autostartregPTB.bat
set scriptpath="%scriptdir%%scriptname%"

%scriptpath% %*
ping localhost -n 5 >nul
