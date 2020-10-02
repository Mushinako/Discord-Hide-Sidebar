#!/usr/bin/env python3
"""Main module. Decides which functions to call"""

import platform
import logging
from pathlib import Path
from argparse import ArgumentParser

from hide_sidebars.runner_obj import WinRunner, MacOsRunner, LinuxRunner
from hide_sidebars.custom_types import RunnerArgs

logger = logging.getLogger(__name__)


def parse_arguments() -> RunnerArgs:
    """Parse command line arguments

    Returns:
        [DiscordHideSidebarArgs]: The object containing all arguments
    """
    log = "[parse_arguments]"
    parser = ArgumentParser(description="Hide sidebar on Discord!")
    parser.add_argument(
        "-d", "--discord-path",
        nargs=1,
        default=None,
        type=Path,
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
    logger.info(f"{log} Args: {args.args_dict()}")
    return args


def main() -> None:
    """Main function
    Gets command line options
    Checks OS
    Runs respective code
    """
    log = "[main]"
    args = parse_arguments()

    operating_system = platform.system()
    logger.info(f"{log} Operating system: {operating_system}")

    if operating_system == "Windows":
        runner = WinRunner(args)
        runner.run()
        return
    if operating_system == "Darwin":
        runner = MacOsRunner(args)
        runner.run()
        return
    if operating_system == "Linux":
        runner = LinuxRunner(args)
        runner.run()
        return
    logger.critical(
        f"Your operating system \"{platform.platform()}\" is not yet supported"
    )
    raise NotImplementedError(
        f"Your operating system \"{platform.platform()}\" is not yet supported"
    )
