@echo off
set scriptdir=%~dp0
set scriptname=hideside.vbs
set scriptpath="%scriptdir%%scriptname%"

set regkey="HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
set regnameptb="DiscordPTB"
set discordptbtmppath="discordptb.tmp"

@REM Check existence of DiscordPTB
reg query %regkey% /v %regnameptb% > %discordptbtmppath% 2>&1 || goto ptbcleanup
for /f "usebackq tokens=3" %%a in (%discordptbtmppath%) do (
    echo "Hi PTB"
    echo %%a
)

exit
