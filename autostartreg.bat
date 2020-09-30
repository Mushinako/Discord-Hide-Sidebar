@echo off

set regkey="HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
set regname="Discord"
set discordtmppath="discord.tmp"

@REM Check existence of Discord
reg query %regkey% /v %regname% > %discordtmppath% 2>nul || goto fail
for /f "usebackq tokens=3" %%a in (%discordtmppath%) do (
    echo %%a > %discordtmppath%
)
goto newreg

:fail
del %discordtmppath%
set /p cont="No Discord startup detected. Are you sure you want to add? (y/N)"
if /i %cont%==y goto newreg
exit

:newreg
set scriptdir=%~dp0
if [%1]==[] goto default
set scriptpath=%1
goto after
:default
set scriptname=hideside.vbs
set scriptpath="%scriptdir%%scriptname%"

:after
set regtype=REG_SZ

echo "reg add %regkey% /f /v %regnameptb% /t %regtype% /d %scriptpath%"
reg add %regkey% /f /v %regnameptb% /t %regtype% /d %scriptpath%

echo Boot patch finished!
ping localhost -n 5 >nul
