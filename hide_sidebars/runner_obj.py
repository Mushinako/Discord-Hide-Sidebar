#!/usr/bin/env python3
"""Module that contains the objects for each operating system."""
import os.path
import glob
from typing import List, Optional


class DiscordHideSidebar:
    """Base class for all operating systems

    Class variables:
        DEFAULT_DISCORD_PATH [str]: Default path for Discord executable
        DEFAULT_JS_PATH      [str]: Default path for JavaScript to be run
        DEFAULT_PORT         [int]: Default port for the debugging session to run
    """
    DEFAULT_DISCORD_PATH: str = ""
    DEFAULT_JS_PATH: str = ""
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
        raise NotImplementedError()


class WinDiscordHideSidebar(DiscordHideSidebar):
    """Special variables/functions for Windows"""
    DEFAULT_DISCORD_PATH = os.path.join(
        os.path.expandvars(r"%LocalAppData%"),
        r"Discord\*\Discord.exe"
    )


pass
