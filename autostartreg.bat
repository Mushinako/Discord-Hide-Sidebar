@echo off
set scriptdir=%~dp0
set scriptname=hideside.vbs
set scriptpath="%scriptdir%%scriptname%"

set regkey="HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
set regname="Discord"
set discordtmppath="discord.tmp"

@REM Check existence of Discord
reg query %regkey% /v %regname% > %discordtmppath% 2>&1 || goto cleanup
for /f "usebackq tokens=3" %%a in (%discordtmppath%) do (
    echo "Hi"
    echo %%a
)

exit
