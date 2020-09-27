#!/usr/bin/env python3
"""Module that contains the objects for each operating system."""
import os.path
import glob
from typing import List, Optional

JS_FILE_NAME = "inject.js"


class DiscordHideSidebar:
    """Base class for all operating systems

    Class variables:
        DEFAULT_DISCORD_PATH_PATTERN [str]: Glob pattern of default path of Discord executable
        DEFAULT_JS_PATH              [str]: Default path of JavaScript to be run
        DEFAULT_PORT                 [int]: Default port for the debugging session to run
        COMMAND_PARAMETERS           [str]: Command parameters to trigger Discord debugging mode

    Instance variables:
        discord_path [str]: Path of Discord executable
        js_path      [str]: Path of JavaScript
        port         [int]: Port forthe debugging session to run
    """
    DEFAULT_DISCORD_PATH_PATTERN: str = ""
    DEFAULT_JS_PATH: str = os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        JS_FILE_NAME
    )
    DEFAULT_PORT: str = 34726
    COMMAND_PARAMETERS: str = "--remote-debugging-port={port}"

    def __new__(cls, *args, **kwargs) -> object:
        """Prevents `DiscordHideSidebar` from directly initialized"""
        if cls is DiscordHideSidebar:
            raise NotImplementedError(
                "Initiation has to be specialized by operating system!"
            )
        return object.__new__(cls, *args, **kwargs)

    def __init__(self, discord_path: Optional[str], js_path: Optional[str], port: Optional[int]) -> None:
        if not self.DEFAULT_DISCORD_PATH:
            raise NotImplementedError(
                f"This class {type(self).__name__} is not fully implemented!"
            )
        self.discord_path = discord_path
        if self.discord_path is None:
            # The last match is assumed to be the latest version
            self.discord_path = glob.glob(
                self.DEFAULT_DISCORD_PATH_PATTERN
            )[-1]
        # Check if Discord path is correct
        self.js_path = js_path or self.DEFAULT_JS_PATH
        self.port = port or self.DEFAULT_PORT


class WinDiscordHideSidebar(DiscordHideSidebar):
    """Special variables/functions for Windows"""
    DEFAULT_DISCORD_PATH_PATTERN = os.path.join(
        os.path.expandvars(r"%LocalAppData%"),
        r"Discord\*\Discord.exe"
    )
