@echo off
set triggerstr="ptb"

set scriptdir=%~dp0
set scriptname=hideside.vbs
set scriptpath="%scriptdir%%scriptname%"

echo %scriptpath%

set regkey="HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
set regname="Discord"
set regnameptb="DiscordPTB"

set discordtmppath="discord.tmp"
set discordptbtmppath="discordptb.tmp"

set addptb=1

@REM Check existence of Discord
reg query %regkey% /v %regname% > %discordtmppath% 2>&1 || goto cleanup
for /f "usebackq tokens=3" %%a in (%discordtmppath%) do (
    echo "Hi"
    echo %%a
)
goto ptb

:cleanup
del %discordtmppath%

:ptb
@REM Check existence of DiscordPTB
reg query %regkey% /v %regnameptb% > %discordptbtmppath% 2>&1 || goto ptbcleanup
for /f "usebackq tokens=3" %%a in (%discordptbtmppath%) do (
    echo "Hi PTB"
    echo %%a
)
goto end

:ptbcleanup
del %discordptbtmppath%

:end
if %1==ptb echo var1: %1
exit
