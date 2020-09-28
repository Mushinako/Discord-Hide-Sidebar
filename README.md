# Discord Hide Sidebars

I don't need the side bars all the time, so why not hide it?

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

### Basic Usage

#### Windows

* Double click `hideside.bat`

#### Others

* Currently, these platforms are not supported because I don't currently have access to a testing machine.

### Advanced Usage

```text
```

## Known issues

### The Discord client stutters/feels slower/uses more CPU

This is a side effect of debug mode. I'm not sure if this can be fixed.
I try to make the JavaScript payload as efficient as possible.

### The toggle does not immediately show up when I switch to another server/conversation

It takes some time for the code to detect that a new window is open.
I'm not sure if this can be fixed using current method.
