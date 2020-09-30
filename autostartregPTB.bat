@echo off

set regkey="HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
set regnameptb="DiscordPTB"
set discordptbtmppath="discordptb.tmp"

@REM Check existence of DiscordPTB
reg query %regkey% /v %regnameptb% > %discordptbtmppath% 2>nul || goto ptbfail
for /f "usebackq tokens=3" %%a in (%discordptbtmppath%) do (
    echo %%a > %discordptbtmppath%
)
goto ptbnewreg

:ptbfail
del %discordptbtmppath%
set /p ptbcont="No Discord startup detected. Are you sure you want to add? (y/N)"
if /i %cont%==y goto ptbnewreg
exit

:ptbnewreg
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
