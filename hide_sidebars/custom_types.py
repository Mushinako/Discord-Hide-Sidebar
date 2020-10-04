#!/usr/bin/env python3
"""Custom classes, mainly for type notation"""

from pathlib import Path
from argparse import Namespace
from dataclasses import dataclass
from typing import Dict, Union, Optional


@dataclass
class RunnerArgs(Namespace):
    """Specific `Namespace` object for arguments of this program
    Mainly used for type notation

    Instance variables:
        discord_path  [Optional[pathlib.Path]]: Path of Discord executable
        port          [Optional[int]]         : Port for the debugging session to run
        boot          [Union[bool, str, None]]: Whether to patch registry to override boot, and optionally the script path
        minimized     [bool]                  : Whether to start Discord minimized
        ptb           [bool]                  : Whether Discord is PTB
    """

    discord_path: Optional[Path]
    port: Optional[int]
    boot: Union[bool, str, None]
    minimized: bool
    ptb: bool

    @classmethod
    def args_dict(cls) -> Dict:
        return {
            "discord_path": cls.discord_path,
            "port": cls.port,
            "boot": cls.boot,
            "minimized": cls.minimized,
            "ptb": cls.ptb
        }
