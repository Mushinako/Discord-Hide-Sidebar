#!/usr/bin/env python3
"""Module that contains the objects for each operating system."""

import os.path
import subprocess
import logging
from string import Template
from glob import glob
from typing import List, Dict, Optional

import requests

from hide_sidebars.action import ACTIONS


class DiscordHideSidebar:
    """Base class for all operating systems

    Class variables:
        DEFAULT_DISCORD_PATH_PATTERNS [List[str]]: Glob pattern of default path of Discord executable
        DEFAULT_PORT                  [int]      : Default port for the debugging session to run
        DEBUG_PARAMETER               [Template] : Parameter template to trigger Discord debugging mode
        MINIMIZED_PARAMETR            [str]      : Parameter to ask Discord to start minimized
        URL                           [Template] : URL template of the debugging session

    Instance variables:
        discord_path [str]                       : Path of Discord executable
        port         [int]                       : Port for the debugging session to run
        url          [str]                       : URL of the debugging session
        minimized    [bool]                      : Whether to start Discord minimized
        process [Optional[subprocess.Popen[str]]]: The started Discord process
    """

    DEFAULT_DISCORD_PATH_PATTERNS = [""]
    DEFAULT_PORT = 34726
    DEBUG_PARAMETER = Template("--remote-debugging-port=${port}")
    MINIMIZED_PARAMETER = "--start-minimized"
    URL = Template("http://localhost:${port}/json")

    def __new__(cls, *args, **kwargs):
        """Prevents `DiscordHideSidebar` from directly initialized"""
        if cls is DiscordHideSidebar:
            raise NotImplementedError(
                "Initiation has to be specialized by operating system!"
            )
        return super().__new__(cls)

    def __init__(self, discord_path: Optional[str], port: Optional[int], minimized: bool) -> None:
        if not self.DEFAULT_DISCORD_PATH_PATTERNS[0]:
            raise NotImplementedError(
                f"This class {type(self).__name__} is not fully implemented!"
            )
        self.discord_path = discord_path
        if self.discord_path is None:
            for pattern in self.DEFAULT_DISCORD_PATH_PATTERNS:
                # The last match is assumed to be the latest version
                paths = glob(pattern)
                if not paths:
                    logging.warn(
                        f"No Discord executable found in {pattern}"
                    )
                    continue
                self.discord_path = paths[-1]
                break
            else:
                raise FileNotFoundError(
                    f"No Discord executable found in default paths {self.DEFAULT_DISCORD_PATH_PATTERNS}"
                )
        # Test Discord path validity
        elif not os.path.isfile(self.discord_path):
            raise FileNotFoundError(f"{self.discord_path} is not a file!")
        # Other variables
        self.port = port or self.DEFAULT_PORT
        self.url = self.URL.substitute(port=self.port)
        self.minimized = minimized
        self.process = None

    def run(self) -> None:
        """Injection go brrrr"""
        self.kill_running()
        self.start_program()
        while True:
            info = self.get_info()
            if info is None:
                continue
            for window in info:
                if ACTIONS.init.run(window):
                    break
            else:
                continue
            break
        self.process.wait()

    def kill_running(self) -> None:
        raise NotImplementedError(
            f"This class {type(self).__name__} is not fully implemented!"
        )

    def start_program(self) -> None:
        """Start Discord program"""
        command: List[str] = [
            self.discord_path,
            self.DEBUG_PARAMETER.substitute(port=self.port)
        ]
        if self.minimized:
            command.append(self.MINIMIZED_PARAMETER)
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )

    def get_info(self) -> Optional[List[Dict[str, str]]]:
        """Get window infos

        Returns:
            [Optional[List[Dict[str, str]]]]: The response JSON object, if any
        """
        response = self.get_req(self.url)
        if response is None:
            return
        response_json: List[Dict[str, str]] = response.json()
        return response_json

    @staticmethod
    def get_req(url: str) -> Optional[requests.Response]:
        """GET URL, with proper error handling

        Args:
            url [str]: URL to GET

        Returns:
            [Optional[requests.Response]]: Response object, if any
        """
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            # Possibly the program has exited
            logging.warn(f"json from {url} connection error")
            return
        return response


class WinDiscordHideSidebar(DiscordHideSidebar):
    """Special variables/functions for Windows"""

    # Non-PTB version is priorized
    DEFAULT_DISCORD_PATH_PATTERNS = [
        os.path.join(
            os.path.expandvars(r"%LocalAppData%"),
            r"Discord\*\Discord.exe"
        ),
        os.path.join(
            os.path.expandvars(r"%LocalAppData%"),
            r"DiscordPTB\*\DiscordPTB.exe"
        ),
    ]

    def kill_running(self) -> None:
        """Kill all running Discord processes"""
        DISCORD_EXECUTABLE_NAME = "Discord.exe"
        processes = subprocess.Popen(
            ["taskkill", "/F", "/IM", DISCORD_EXECUTABLE_NAME, "/T"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, err = processes.communicate()
        if err and b"\"Discord.exe\" not found" not in err:
            raise OSError(err)
