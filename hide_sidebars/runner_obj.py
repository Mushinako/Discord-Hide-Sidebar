#!/usr/bin/env python3
"""Module that contains the objects for each operating system."""
import os.path
import subprocess
from string import Template
from glob import glob
from typing import Optional

JS_FILE_NAME = "inject.js"


class DiscordHideSidebar:
    """Base class for all operating systems

    Class variables:
        DEFAULT_DISCORD_PATH_PATTERN [str]: Glob pattern of default path of Discord executable
        DEFAULT_JS_PATH              [str]: Default path of JavaScript to be run
        DEFAULT_PORT                 [int]: Default port for the debugging session to run
        COMMAND_PARAMETERS           [str]: Command parameters to trigger Discord debugging mode

    Instance variables:
        discord_path [str]                       : Path of Discord executable
        js_path      [str]                       : Path of JavaScript
        port         [int]                       : Port for the debugging session to run
        debug_url    [str]                       : URL of the debugging session
        process [Optional[subprocess.Popen[str]]]: The started Discord process
    """

    DEFAULT_DISCORD_PATH_PATTERN: str = ""
    DEFAULT_JS_PATH: str = os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        JS_FILE_NAME
    )
    DEFAULT_PORT: int = 34726
    COMMAND_PARAMETER = Template("--remote-debugging-port=${port}")
    URL = Template("https://localhost:${port}/json")

    def __new__(cls, *args, **kwargs):
        """Prevents `DiscordHideSidebar` from directly initialized"""
        if cls is DiscordHideSidebar:
            raise NotImplementedError(
                "Initiation has to be specialized by operating system!"
            )
        return super().__new__(cls)

    def __init__(self, discord_path: Optional[str], js_path: Optional[str], port: Optional[int]) -> None:
        if not self.DEFAULT_DISCORD_PATH_PATTERN:
            raise NotImplementedError(
                f"This class {type(self).__name__} is not fully implemented!"
            )
        self.discord_path = discord_path
        if self.discord_path is None:
            # The last match is assumed to be the latest version
            paths = glob(self.DEFAULT_DISCORD_PATH_PATTERN)
            if not paths:
                raise FileNotFoundError(
                    f"No Discord executable found in default path {self.DEFAULT_DISCORD_PATH_PATTERN}!"
                )
            self.discord_path = paths[-1]
        # Test path validity
        elif not os.path.isfile(self.discord_path):
            raise FileNotFoundError(f"{self.discord_path} is not a file!")
        self.js_path = js_path or self.DEFAULT_JS_PATH
        # Test path validity
        if not os.path.isfile(self.js_path):
            raise FileNotFoundError(f"{self.js_path} is not a file!")
        self.port = port or self.DEFAULT_PORT
        self.debug_url = self.URL.substitute(port=self.port)
        self.process: Optional[subprocess.Popen[str]] = None

    def run(self) -> None:
        self.kill_running()
        self.start_program()

    def kill_running(self) -> None:
        raise NotImplementedError(
            f"This class {type(self).__name__} is not fully implemented!"
        )

    def start_program(self) -> None:
        """Start Discord program"""
        self.process = subprocess.Popen(
            [
                self.discord_path,
                self.COMMAND_PARAMETER.substitute(port=self.port)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )


class WinDiscordHideSidebar(DiscordHideSidebar):
    """Special variables/functions for Windows"""
    DEFAULT_DISCORD_PATH_PATTERN = os.path.join(
        os.path.expandvars(r"%LocalAppData%"),
        r"Discord\*\Discord.exe"
    )

    def kill_running(self) -> None:
        """Kill all running Discord processes"""
        DISCORD_EXECUTABLE_NAME = "Discord.exe"
        processes = subprocess.Popen(
            ["taskkill", "/F", "/IM", DISCORD_EXECUTABLE_NAME, "/T"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _, err = processes.communicate()
        if err is not None:
            raise OSError(err)
