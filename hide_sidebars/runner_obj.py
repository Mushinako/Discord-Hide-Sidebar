#!/usr/bin/env python3
"""Module that contains the objects for each operating system."""

import os.path
import subprocess
import logging
from string import Template
from glob import glob
from typing import List, Dict, Union, Optional

import requests

from hide_sidebars.action import ACTIONS
from hide_sidebars.custom_types import RunnerArgs


class Runner:
    """Base class for all operating systems

    Class variables:
        DEFAULT_DISCORD_PATH_PATTERN    [str]     : Glob pattern of default path of Discord executable
        DEFAULT_DISCORDPTB_PATH_PATTERN [str]     : Glob pattern of default path of DiscordPTB executable
        DEFAULT_PORT                    [int]     : Default port for the debugging session to run
        DEBUG_PARAMETER                 [Template]: Parameter template to trigger Discord debugging mode
        MINIMIZED_PARAMETR              [str]     : Parameter to ask Discord to start minimized
        URL                             [Template]: URL template of the debugging session

    Instance variables:
        discord_path [str]                       : Path of Discord executable
        is_ptb       [bool]                      : Whether the Discord executable is PTB
        port         [int]                       : Port for the debugging session to run
        url          [str]                       : URL of the debugging session
        minimized    [bool]                      : Whether to start Discord minimized
        boot         [bool]                      : Whether to patch registry to override boot
        boot_path    [Optional[str]]             : Path of the script file, if not default
        process [Optional[subprocess.Popen[str]]]: The started Discord process
    """

    DEFAULT_DISCORD_PATH_PATTERN = ""
    DEFAULT_DISCORDPTB_PATH_PATTERN = ""
    DEFAULT_PORT = 34726
    DEBUG_PARAMETER = Template("--remote-debugging-port=${port}")
    MINIMIZED_PARAMETER = "--start-minimized"
    URL = Template("http://localhost:${port}/json")

    def __new__(cls, *args, **kwargs):
        """Prevents `Runner` from being directly initialized"""
        if cls is Runner:
            raise NotImplementedError(
                "Initiation has to be specialized by operating system!"
            )
        return super().__new__(cls)

    def __init__(self, args: RunnerArgs) -> None:
        self.discord_path = args.discord_path
        self.is_ptb: bool = False
        if self.discord_path is None:
            if not self.DEFAULT_DISCORD_PATH_PATTERN and not self.DEFAULT_DISCORDPTB_PATH_PATTERN:
                raise ValueError("No Discord executable path provided!")
            if not self.default_path(
                self.DEFAULT_DISCORD_PATH_PATTERN,
                False
            ) and not self.default_path(
                self.DEFAULT_DISCORDPTB_PATH_PATTERN,
                True
            ):
                raise FileNotFoundError(
                    f"No Discord executable found in default paths {[self.DEFAULT_DISCORD_PATH_PATTERN, self.DEFAULT_DISCORDPTB_PATH_PATTERN]}"
                )
        # Test Discord path validity
        elif not os.path.isfile(self.discord_path):
            raise FileNotFoundError(f"{self.discord_path} is not a file!")
        # Check if provided path is potentially PTB
        else:
            self.is_ptb = "ptb" in os.path.basename(self.discord_path).lower()
        # PTB flag override
        if args.ptb:
            self.is_ptb = args.ptb
        # Other variables
        self.port = args.port or self.DEFAULT_PORT
        self.url = self.URL.substitute(port=self.port)
        self.minimized = args.minimized
        self.boot: bool = False
        self.boot_path: Optional[str] = None
        if args.boot is not None:
            self.boot = True
            if isinstance(args.boot, str):
                boot = args.boot
                if boot[0] != "\"" or boot[-1] != "\"":
                    boot = f"\"{boot}\""
                self.boot_path = boot
        self.process: Optional[subprocess.Popen[str]] = None

    def default_path(self, pattern: str, ptb: bool) -> bool:
        """Get the default path , set the vars, and return whether it exists

        Args:
            pattern [str] : glob pattern
            ptb     [bool]: `is_ptb` value corresponding to this pattern

        Returns:
            [bool]: Whether a path is found
        """
        if not pattern:
            logging.warn("Empty default path")
            return False
        paths = glob(pattern)
        if not paths:
            logging.warn(f"No Discord executable found in {pattern}")
            return False
        self.discord_path = paths[-1]
        self.is_ptb = ptb
        return True

    def run(self) -> None:
        """Injection go brrrr"""
        self.kill_running()
        self.start_program()
        while True:
            info = self.get_info()
            if info is None:
                if self.process.poll() is None:
                    continue
                else:
                    break
            for window in info:
                if ACTIONS.init.run(window):
                    break
            else:
                continue
            break
        self.process.wait()
        if self.boot:
            self.patch_boot()

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

    def patch_boot(self) -> None:
        raise NotImplementedError(
            f"This class {type(self).__name__} is not fully implemented!"
        )

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


class WinRunner(Runner):
    """Special variables/functions for Windows

    Class variables:
        BOOT_BAT_DIR         [str]: Directory containing boot patch batch files
        STABLE_BOOT_BAT_PATH [str]: Path for stable Discord boot patch batch file
        PTB_BOOT_BAT_PATH    [str]: Path for DiscordPTB boot patch batch file
    """

    # Non-PTB version is priorized
    DEFAULT_DISCORD_PATH_PATTERN = os.path.join(
        os.path.expandvars(r"%LocalAppData%"),
        r"Discord\*\Discord.exe"
    )
    DEFAULT_DISCORDPTB_PATH_PATTERN = os.path.join(
        os.path.expandvars(r"%LocalAppData%"),
        r"DiscordPTB\*\DiscordPTB.exe"
    )
    BOOT_BAT_DIR = os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        "scripts",
        "windows"
    )
    STABLE_BOOT_BAT_PATH = os.path.join(
        BOOT_BAT_DIR,
        "autostartreg.bat"
    )
    PTB_BOOT_BAT_PATH = os.path.join(
        BOOT_BAT_DIR,
        "autostartregPTB.bat"
    )

    def kill_running(self) -> None:
        """Kill all running Discord processes"""
        DISCORD_EXECUTABLE_NAME = "DiscordPTB.exe" if self.is_ptb else "Discord.exe"
        processes = subprocess.Popen(
            ["taskkill", "/F", "/IM", DISCORD_EXECUTABLE_NAME, "/T"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = processes.communicate()
        logging.debug(out)
        logging.warn(err)
        if err and b"\"Discord.exe\" not found" not in err:
            raise OSError(err)

    def patch_boot(self) -> None:
        """Patch boot"""
        args = [
            self.PTB_BOOT_BAT_PATH
            if self.is_ptb
            else self.STABLE_BOOT_BAT_PATH
        ]
        if self.boot_path is not None:
            args.append(self.boot_path)
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = proc.communicate()
        logging.debug(out.strip())
        logging.warn(err.strip())


class MacOsRunner(Runner):
    """Special variables/functions for macOS"""

    def kill_running(self) -> None:
        """Kill all running Discord processes"""
        DISCORD_EXECUTABLE_NAME = "DiscordPTB" if self.is_ptb else "Discord"
        process = subprocess.Popen(
            ["pkill", "-a", DISCORD_EXECUTABLE_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = process.communicate()
        logging.debug(out)
        logging.warn(err)

    def patch_boot(self) -> None:
        """Patch boot, not written yet"""
        print("Patching boot is currently Windows only!")


class LinuxRunner(Runner):
    """Special variables/functions for Linux"""

    def kill_running(self) -> None:
        """Kill all running Discord processes"""
        DISCORD_EXECUTABLE_NAME = "DiscordPTB" if self.is_ptb else "Discord"
        process = subprocess.Popen(
            ["pkill", "-a", DISCORD_EXECUTABLE_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = process.communicate()
        logging.debug(out)
        logging.warn(err)

    def patch_boot(self) -> None:
        """Patch boot, not written yet"""
        print("Patching boot is currently Windows only!")
