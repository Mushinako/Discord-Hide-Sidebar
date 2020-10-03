#!/usr/bin/env python3
"""Module that contains the objects for each operating system."""

import os.path
import subprocess
import logging
from pathlib import Path
from string import Template
from time import sleep
from typing import List, Dict, Optional

import requests

from hide_sidebars.action import ACTIONS
from hide_sidebars.custom_types import RunnerArgs

logger = logging.getLogger(__name__)


class Runner:
    """Base class for all operating systems

    Class variables:
        DEFAULT_PATH_ROOT           [Optional[pathlib.Path]]: Root of default path of Discord(PTB) executables
        DEFAULT_STABLE_PATH_PATTERN [Optional[str]]         : Glob pattern of default path of Discord executable
        DEFAULT_PTB_PATH_PATTERN    [Optional[str]]         : Glob pattern of default path of DiscordPTB executable
        DEFAULT_PORT                [int]                   : Default port for the debugging session to run
        DEBUG_PARAMETER             [Template]              : Parameter template to trigger Discord debugging mode
        MINIMIZED_PARAMETR          [str]                   : Parameter to ask Discord to start minimized
        URL                         [Template]              : URL template of the debugging session

    Instance variables:
        discord_path [pathlib.Path]              : Path of Discord executable
        is_ptb       [bool]                      : Whether the Discord executable is PTB
        port         [int]                       : Port for the debugging session to run
        url          [str]                       : URL of the debugging session
        minimized    [bool]                      : Whether to start Discord minimized
        boot         [bool]                      : Whether to patch registry to override boot
        boot_path    [Optional[pathlib.Path]]    : Path of the boot script file, if not default
        process [Optional[subprocess.Popen[str]]]: The started Discord process
    """

    DEFAULT_PATH_ROOT: Optional[Path] = None
    DEFAULT_STABLE_PATH_PATTERN: Optional[str] = None
    DEFAULT_PTB_PATH_PATTERN: Optional[str] = None
    DEFAULT_PORT = 34726
    DEBUG_PARAMETER = Template("--remote-debugging-port=${port}")
    MINIMIZED_PARAMETER = "--start-minimized"
    URL = Template("http://localhost:${port}/json")

    def __new__(cls, *args, **kwargs):
        """Prevents `Runner` from being directly initialized"""
        log = f"[{cls.__name__}.__new__]"
        if cls is Runner:
            logger.critical(
                f"{log} Initiation has to be specialized by operating system",
                stack_info=True
            )
            raise NotImplementedError(
                "Initiation has to be specialized by operating system!"
            )
        return super().__new__(cls)

    def __init__(self, args: RunnerArgs) -> None:
        log = f"[{type(self).__name__}.__init__]"
        self.is_ptb: bool = False
        # No path provided. Check defaults
        if args.discord_path is None:
            logger.info(f"{log} No \"discord_path\" provided")
            root = self.DEFAULT_PATH_ROOT
            stable_glob = self.DEFAULT_STABLE_PATH_PATTERN
            ptb_glob = self.DEFAULT_PTB_PATH_PATTERN
            logger.debug(f"{log} Default path root: \"{root}\"")
            logger.debug(f"{log} Default glob stable: \"{stable_glob}\"")
            logger.debug(f"{log} Default glob PTB: \"{ptb_glob}\"")
            # No defaults
            if root is None or all(g is None for g in [stable_glob, ptb_glob]):
                logger.critical(f"{log} No Discord executable path provided")
                raise ValueError("No Discord executable path provided!")
            # Check default stable
            if not args.ptb and (path := self.default_path(root, stable_glob)) is not None:
                self.discord_path = path
            # Check default PTB
            elif (path := self.default_path(root, ptb_glob)) is not None:
                self.is_ptb = True
                self.discord_path = path
            # No executable found
            else:
                logger.critical(
                    f"{log} No Discord executable found in default paths"
                )
                raise FileNotFoundError(
                    f"No Discord executable found in root \"{root}\" with patterns {[stable_glob, ptb_glob]} and ptb flag {args.ptb}"
                )
        # Test provided path validity
        elif not args.discord_path.is_file():
            logger.critical(f"{log} Provided `discord_path` is not a file")
            raise FileNotFoundError(f"\"{args.discord_path}\" is not a file!")
        # Check if provided path is potentially PTB
        else:
            logger.info(f"{log} Provided `discord_path` used")
            self.discord_path = args.discord_path
            self.is_ptb = "ptb" in self.discord_path.name.lower()
        # PTB flag override
        if args.ptb:
            logger.info(f"{log} PTB flag overridden")
            self.is_ptb = args.ptb
        # Other variables
        self.port = args.port or self.DEFAULT_PORT
        self.url = self.URL.substitute(port=self.port)
        self.minimized = args.minimized
        self.boot: bool = False
        self.boot_path: Optional[Path] = None
        if args.boot is not None:
            self.boot = True
            if isinstance(args.boot, str):
                self.boot_path = Path(args.boot)
        self.process: Optional[subprocess.Popen[str]] = None
        logger.debug(f"{log} Initialized: {self.__dict__}")

    def default_path(self, root: Path, pattern: Optional[str]) -> Optional[Path]:
        """Get the default path , set the vars, and return whether it exists

        Args:
            root    [pathlib.Path] : Root path to run the pattern in
            pattern [Optional[str]]: glob pattern

        Returns:
            [Optional[pathlib.Path]]: A path if it is found; `None` otherwise
        """
        log = f"[{type(self).__name__}.default_path]"
        if pattern is None:
            logger.warn(f"{log} Empty pattern")
            return
        paths = list(root.glob(pattern))
        if not paths:
            logger.warn(
                f"{log} No Discord executable found in \"{root}\" with pattern \"{pattern}\""
            )
            return
        return paths[-1]

    def run(self) -> None:
        """Injection go brrrr"""
        log = f"[{type(self).__name__}.run]"
        self.kill_running()
        logger.debug(f"{log} Running instances killed")
        self.start_program()
        logger.debug(
            f"{log} Discord started process {self.process.pid}"
        )
        while True:
            sleep(0.5)
            info = self.get_info()
            if info is None:
                if self.process.poll() is None:
                    # No info got; retry
                    continue
                else:
                    # Process terminated; exit loop
                    break
            for window in info:
                if ACTIONS.init.run(window):
                    # Injection successful
                    break
            else:
                continue
            break
        self.process.wait()
        if self.boot:
            self.patch_boot()

    def kill_running(self) -> None:
        log = f"[{type(self).__name__}.kill_running]"
        logger.critical(f"{log} Unimplemented `kill_running`")
        raise NotImplementedError(
            f"Class `{type(self).__name__}` does not have `kill_running` method!"
        )

    def start_program(self) -> None:
        """Start Discord program"""
        log = f"[{type(self).__name__}.start_program]"
        command: List[str] = [
            str(self.discord_path),
            self.DEBUG_PARAMETER.substitute(port=self.port)
        ]
        if self.minimized:
            command.append(self.MINIMIZED_PARAMETER)
        logger.debug(f"{log} Command: `{command}`")
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
        log = f"[{type(self).__name__}.get_info]"
        response = self.get_req(self.url)
        if response is None:
            logger.warn(f"{log} No response got from \"{self.url}\"")
            return
        response_obj: List[Dict[str, str]] = response.json()
        return response_obj

    def get_req(self, url: str) -> Optional[requests.Response]:
        """GET URL, with proper error handling

        Args:
            url [str]: URL to GET

        Returns:
            [Optional[requests.Response]]: Response object, if any
        """
        log = f"[{type(self).__name__}.get_req]"
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError as err:
            # Possibly the program has exited
            logger.warn(f"{log} JSON from \"{url}\" connection error {err}")
            return
        logger.debug(f"{log} Got response from \"{url}\": {response}")
        return response

    def patch_boot(self) -> None:
        log = f"[{type(self).__name__}.patch_boot]"
        logger.critical(f"{log} Unimplemented `patch_boot`")
        raise NotImplementedError(
            f"Class `{type(self).__name__}` does not have `patch_boot` method!"
        )


class WinRunner(Runner):
    """Special variables/functions for Windows

    Class variables:
        BOOT_BAT_DIR         [pathlib.Path]: Directory containing boot patch batch files
        STABLE_BOOT_BAT_PATH [pathlib.Path]: Path for stable Discord boot patch batch file
        PTB_BOOT_BAT_PATH    [pathlib.Path]: Path for DiscordPTB boot patch batch file
    """

    DEFAULT_PATH_ROOT = Path(os.path.expandvars(r"%LocalAppData%"))
    DEFAULT_STABLE_PATH_PATTERN = r"Discord\*\Discord.exe"
    DEFAULT_PTB_PATH_PATTERN = r"DiscordPTB\*\DiscordPTB.exe"
    BOOT_BAT_DIR = Path(__file__).parent.parent / "scripts" / "windows"
    STABLE_BOOT_BAT_PATH = BOOT_BAT_DIR / "autostartreg.bat"
    PTB_BOOT_BAT_PATH = BOOT_BAT_DIR / "autostartregPTB.bat"

    def kill_running(self) -> None:
        """Kill all running Discord processes"""
        log = f"[{type(self).__name__}.kill_running]"
        DISCORD_EXECUTABLE_NAME = "DiscordPTB.exe" if self.is_ptb else "Discord.exe"
        logger.debug(f"{log} Process name: \"{DISCORD_EXECUTABLE_NAME}\"")
        command = ["taskkill", "/F", "/IM", DISCORD_EXECUTABLE_NAME, "/T"]
        logger.debug(f"{log} Command: `{command}`")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = process.communicate()
        logger.debug(f"{log} Process STDOUT: {out.strip()}")
        logger.warn(f"{log} Process STDERR: {err.strip()}")

    def patch_boot(self) -> None:
        """Patch boot"""
        log = f"[{type(self).__name__}.patch_boot]"
        command = [
            str(self.PTB_BOOT_BAT_PATH)
            if self.is_ptb
            else str(self.STABLE_BOOT_BAT_PATH)
        ]
        if self.boot_path is not None:
            boot = str(self.boot_path)
            if any(char != "\"" for char in [boot[0], boot[-1]]):
                boot = f"\"{boot}\""
            command.append(boot)
        logger.debug(f"{log} Command: `{command}`")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = process.communicate()
        logger.debug(f"{log} Process STDOUT: {out.strip()}")
        logger.warn(f"{log} Process STDERR: {err.strip()}")


class MacOsRunner(Runner):
    """Special variables/functions for macOS"""

    def kill_running(self) -> None:
        """Kill all running Discord processes"""
        log = f"[{type(self).__name__}.kill_running]"
        DISCORD_EXECUTABLE_NAME = "DiscordPTB" if self.is_ptb else "Discord"
        logger.debug(f"{log} Process name: \"{DISCORD_EXECUTABLE_NAME}\"")
        command = ["pkill", "-a", DISCORD_EXECUTABLE_NAME]
        logger.debug(f"{log} Command: `{command}`")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = process.communicate()
        logger.debug(f"{log} {out.strip()}")
        logger.warn(f"{log} {err.strip()}")

    def patch_boot(self) -> None:
        """Patch boot, not written yet"""
        log = f"[{type(self).__name__}.patch_boot]"
        logger.warn(f"{log} Patching boot is currently unavailable on macOS")
        print("Patching boot is currently unavailable on macOS")


class LinuxRunner(Runner):
    """Special variables/functions for Linux"""

    def kill_running(self) -> None:
        """Kill all running Discord processes"""
        log = f"[{type(self).__name__}.kill_running]"
        DISCORD_EXECUTABLE_NAME = "DiscordPTB" if self.is_ptb else "Discord"
        logger.debug(f"{log} Process name: \"{DISCORD_EXECUTABLE_NAME}\"")
        command = ["pkill", "-a", DISCORD_EXECUTABLE_NAME]
        logger.debug(f"{log} Command: `{command}`")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = process.communicate()
        logger.debug(f"{log} {out.strip()}")
        logger.warn(f"{log} {err.strip()}")

    def patch_boot(self) -> None:
        """Patch boot, not written yet"""
        log = f"[{type(self).__name__}.patch_boot]"
        logger.warn(f"{log} Patching boot is currently unavailable on Linux")
        print("Patching boot is currently unavailable on Linux")
