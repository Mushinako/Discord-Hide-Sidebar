# Discord Hide Sidebar

I don't need the left sidebar all the time, so why not hide it when I need more screen dedicated to the messages?

**This script starts your Discord in debug mode.**
**This means that your personal information may be visible to other programs on your computer or others on the Internet.**
**Do not use this script unless you know what you're doing!**
**By using this script, you acknowledge this possibility.**
**I will *not* be responsible for any damage caused by this script.**
If you don't know how to mitigate this risk and are not willing to take it, please wait for Discord to implement this functionality.

## Requirements

* Python (latest version `3.8` guaranteed, may work on `3.7` and above)
* Libraries (can be installed via `pip install -r requirements.txt`)
  * [requests](https://requests.readthedocs.io/en/master/): tested on `2.24.0`
  * [websocket-client](https://github.com/websocket-client/websocket-client): tested on `0.57.0`

## How to use

When Discord is launched through the script, there'll be a `<` next to `?` on the top-right.
Click `<` to toggle.

### Basic Usage

#### Windows

* If you want to see the console window, double click `hideside.bat`
* If you do not want to see the console window, double click `hideside.vbs`
  * Note this will also start Discord minimized

#### Others

Currently, these platforms are not supported because I don't currently have access to a testing machine.
However, it's possible the script will work, but you'll have to provide the location of Discord executable.

For example, for Discord installed in `/usr/bin/discord`, run:

```bash
python3 hideside.py -d "/usr/bin/discord"
```

### Advanced Usage

```text
usage: hideside.py [-h] [-d DISCORD_PATH] [-j JS_PATH] [-p range65536] [-m]

Hide sidebars on Discord!

optional arguments:
  -h, --help            show this help message and exit
  -d DISCORD_PATH, --discord-path DISCORD_PATH
                        Path of Discord executable
  -j JS_PATH, --js-path JS_PATH
                        Path of JavaScript to be executed
  -p range(65536), --port range(65536)
                        Port for the debugging session to run
  -m, --minimized       Use this to start Discord minimized
```

## Known issues

### The Discord client stutters/feels slower/uses more CPU

The performance is expected to dip but it should not dip by much.
This is a side effect of debug mode. I'm not sure if this can be fixed.
I try to make the JavaScript payload as efficient as possible.
Please open an issue if the performance dip is severe.

### The toggle does not immediately show up when I switch to another server/conversation

It takes some time for the code to detect that a new window is open.
I'm not sure if this can be fixed using current method.
