#!/usr/bin/env python3
"""Main module. Decides which functions to call"""

import platform
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Union, Optional

from hide_sidebars.runner_obj import WinRunner


@dataclass
class RunnerArgs(Namespace):
    """Specific `Namespace` object for arguments of this program
    Mainly used for type notation

    Instance variables:
        discord_path  [Optional[str]]: Path of Discord executable
        port          [Optional[int]]: Port for the debugging session to run
        boot [Union[bool, str, None]]: Whether to patch registry to override boot, and optionally the script path
        minimized     [bool]         : Whether to start Discord minimized
        ptb           [bool]         : Whether Discord is PTB
    """

    discord_path: Optional[str]
    port: Optional[int]
    boot: Union[bool, str, None]
    minimized: bool
    ptb: bool


def parse_arguments() -> RunnerArgs:
    """Parse command line arguments

    Returns:
        [DiscordHideSidebarArgs]: The object containing all arguments
    """
    parser = ArgumentParser(description="Hide sidebar on Discord!")
    parser.add_argument(
        "-d", "--discord-path",
        nargs=1,
        default=None,
        help="Path of Discord executable",
        dest="discord_path"
    )
    parser.add_argument(
        "-p", "--port",
        nargs=1,
        default=None,
        type=int,
        choices=range(65536),
        help="Port for the debugging session to run",
        metavar="{0-65535}",
        dest="port"
    )
    parser.add_argument(
        "-b", "--boot",
        nargs="?",
        const=True,
        default=None,
        help="Use this to patch registry to override boot. Specify script path as necessary",
        dest="boot"
    )
    parser.add_argument(
        "-m", "--minimized",
        action="store_true",
        help="Use this to start Discord minimized",
        dest="minimized"
    )
    parser.add_argument(
        "-t", "--ptb",
        action="store_true",
        help="Use this to indicate Discord is PTB",
        dest="ptb"
    )
    args = parser.parse_args(namespace=RunnerArgs)
    return args


def main() -> None:
    """Main function
    Gets command line options
    Checks OS
    Runs respective code
    """

    args = parse_arguments()

    operating_system = platform.system()

    if operating_system == "Windows":
        runner = WinRunner(
            args.discord_path,
            args.port,
            args.boot,
            args.minimized,
            args.ptb
        )
        runner.run()
        return
    if operating_system == "Darwin":
        runner
    raise NotImplementedError(
        f"Your operating system \"{platform.platform()}\" is not yet supported"
    )
