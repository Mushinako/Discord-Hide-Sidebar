#!/usr/bin/env python3
"""Main module. Decides which functions to call"""

import os.path
import platform
from argparse import ArgumentParser, Namespace
from typing import Optional

from hide_sidebars.runner_obj import WinDiscordHideSidebar


class DiscordHideSidebarArgs(Namespace):
    """Specific `Namespace` object for arguments of this program
    Mainly used for type notation

    Instance variables:
        discord_path [Optional[str]]: Path of Discord executable
        js_path      [Optional[str]]: Path of JavaScript to be executed
        port         [Optional[int]]: Port for the debugging session to run
        minimized    [bool]         : Whether to start Discord minimized
    """

    def __init__(
        self,
        discord_path: Optional[str],
        js_path: Optional[str],
        port: Optional[int],
        minimized: bool
    ) -> None:
        self.discord_path = discord_path
        self.js_path = js_path
        self.port = port
        self.minimized = minimized


def parse_arguments() -> DiscordHideSidebarArgs:
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
        "-j", "--js-path",
        nargs=1,
        default=None,
        help="Path of JavaScript to be executed",
        dest="js_path"
    )
    parser.add_argument(
        "-p", "--port",
        nargs=1,
        default=None,
        type=int,
        choices=range(65536),
        help="Port for the debugging session to run",
        metavar="range(65536)",
        dest="port"
    )
    parser.add_argument(
        "-m", "--minimized",
        action="store_true",
        help="Use this to start Discord minimized",
        dest="minimized"
    )
    args = parser.parse_args(namespace=DiscordHideSidebarArgs)
    return args


def main() -> None:
    """Main function
    Gets command line options
    Checks OS
    Runs respective code
    """

    args = parse_arguments()

    operating_system = platform.system().lower()

    if operating_system == "windows":
        runner = WinDiscordHideSidebar(
            args.discord_path,
            args.js_path,
            args.port,
            args.minimized
        )
        runner.run()
    else:
        raise NotImplementedError(
            f"Your operating system \"{platform.platform()}\" is not yet supported"
        )
