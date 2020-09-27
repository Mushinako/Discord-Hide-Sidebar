@echo off
set port=38000
"%LocalAppdata%\Discord\app-0.0.308\Discord.exe" --remote-debugging-port=%port%
echo "Debugging started on port %port%"
