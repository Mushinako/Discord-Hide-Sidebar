@echo off
set scriptpath=%~dp0hideside.py
set logpath=%~dp0logs\output.log
echo HideSide > %logpath%
py -3 %scriptpath% %* > %logpath%