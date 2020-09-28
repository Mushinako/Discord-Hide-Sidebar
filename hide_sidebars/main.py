#!/usr/bin/env python3
"""Main module. Decides which functions to call"""

import platform
from argparse import ArgumentParser, Namespace
from typing import Optional

from hide_sidebars.runner_obj import WinDiscordHideSidebar

DEFAULT_JS_PATH = "inject.js"


class DiscordHideSidebarArgs(Namespace):
    """Specific `Namespace` object for arguments of this program
    Mainly used for type notation

    Instance variables:
        discord_path [Optional[str]]: Path of Discord executable
        js_path      [Optional[str]]: Path of JavaScript to be executed
        port         [Optional[int]]: Port for the debugging session to run
    """

    def __init__(
        self,
        discord_path: Optional[str],
        js_path: Optional[str],
        port: Optional[int]
    ) -> None:
        self.discord_path = discord_path
        self.js_path = js_path
        self.port = port


def parse_arguments() -> DiscordHideSidebarArgs:
    """Parse command line arguments

    Returns:
        [DiscordHideSidebarArgs]: The object containing all arguments
    """
    parser = ArgumentParser(description="Hide sidebars on Discord!")
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
        dest="port"
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

    operating_system = platform.platform().lower()

    if operating_system.startswith("windows"):
        runner = WinDiscordHideSidebar(
            args.discord_path,
            args.js_path,
            args.port
        )
        runner.run()
    else:
        raise NotImplementedError(
            f"Your operating system \"{platform.platform()}\" is not yet supported"
        )
