#!/usr/bin/env python3
"""Module that contains the objects for each operating system."""
import os.path
import subprocess
import json
import logging
from string import Template
from glob import glob
from typing import List, Dict, Optional

import requests
import websocket

JS_FILE_NAME = "inject.min.js"


class DiscordHideSidebar:
    """Base class for all operating systems

    Class variables:
        DEFAULT_DISCORD_PATH_PATTERN [str]: Glob pattern of default path of Discord executable
        DEFAULT_JS_PATH              [str]: Default path of JavaScript to be run
        DEFAULT_PORT                 [int]: Default port for the debugging session to run
        DEBUG_PARAMETER         [Template]: Parameter template to trigger Discord debugging mode
        MINIMIZED_PARAMETR           [str]: Parameter to ask Discord to start minimized
        URL                     [Template]: URL template of the debugging session
        SOCKET_URL_KEY               [str]: Key name for socket URL

    Instance variables:
        discord_path [str]                       : Path of Discord executable
        data         [Dict]                      : Request data to be sent
        data_json    [str]                       : Request data to be sent, but in JSON
        port         [int]                       : Port for the debugging session to run
        url          [str]                       : URL of the debugging session
        minimized    [bool]                      : Whether to start Discord minimized
        process [Optional[subprocess.Popen[str]]]: The started Discord process
    """

    DEFAULT_DISCORD_PATH_PATTERN: str = ""
    DEFAULT_JS_PATH = os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        JS_FILE_NAME
    )
    DEFAULT_PORT = 34726
    DEBUG_PARAMETER = Template("--remote-debugging-port=${port}")
    MINIMIZED_PARAMETER = "--start-minimized"
    URL = Template("http://localhost:${port}/json")
    SOCKET_URL_KEY = "webSocketDebuggerUrl"

    def __new__(cls, *args, **kwargs):
        """Prevents `DiscordHideSidebar` from directly initialized"""
        if cls is DiscordHideSidebar:
            raise NotImplementedError(
                "Initiation has to be specialized by operating system!"
            )
        return super().__new__(cls)

    def __init__(self, discord_path: Optional[str], js_path: Optional[str], port: Optional[int], minimized: bool) -> None:
        if not self.DEFAULT_DISCORD_PATH_PATTERN:
            raise NotImplementedError(
                f"This class {type(self).__name__} is not fully implemented!"
            )
        self.discord_path = discord_path
        if self.discord_path is None:
            # The last match is assumed to be the latest version
            paths = glob(self.DEFAULT_DISCORD_PATH_PATTERN)
            if not paths:
                raise FileNotFoundError(
                    f"No Discord executable found in default path {self.DEFAULT_DISCORD_PATH_PATTERN}!"
                )
            self.discord_path = paths[-1]
        # Test path validity
        elif not os.path.isfile(self.discord_path):
            raise FileNotFoundError(f"{self.discord_path} is not a file!")
        js_path_ = js_path or self.DEFAULT_JS_PATH
        # Test path validity
        if not os.path.isfile(js_path_):
            raise FileNotFoundError(f"{js_path_} is not a file!")
        # Read JavaScript
        js = self.get_js(js_path_)
        # Assemble data
        self.data = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": js,
                "objectGroup": "discordHideSidebar",
                "userGesture": True,
            },
        }
        self.data_json = json.dumps(self.data)
        self.port = port or self.DEFAULT_PORT
        self.url = self.URL.substitute(port=self.port)
        self.minimized = minimized
        self.process = None

    def run(self) -> None:
        """Injection go brrrr"""
        self.kill_running()
        self.start_program()
        while self.process.poll() is None:
            info = self.get_info()
            if info is None:
                break
            self.inject(info)

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
        """Get window infos"""
        try:
            response = requests.get(self.url)
        except ConnectionError:
            logging.warn(f"json from {self.url} connection error")
            return
        response_json: List[Dict[str, str]] = response.json()
        return response_json

    def inject(self, info: List[Dict[str, str]]) -> None:
        """Inject code!"""
        for window in info:
            socket_url = window[self.SOCKET_URL_KEY]
            try:
                ws = websocket.create_connection(socket_url)
            except ConnectionRefusedError:
                logging.warn(f"websocket to {socket_url} refused")
                continue
            ws.send(self.data_json)
            response = ws.recv()
            title = f"\"{window['title']}\""
            if response is None:
                logging.warn(f"{title} injection response empty")
                continue
            response_dict = json.loads(response)
            if "result" not in response_dict:
                logging.warn(f"{title} injection response has no 'result'")
                continue
            result = response_dict["result"]
            if "exceptionDetails" in result:
                exception_details = result["exceptionDetails"]
                if "exception" not in exception_details:
                    logging.warn(f"{title} injection failed but no details")
                else:
                    exception = exception_details["exception"]
                    logging.warn(f"{title} injection failed by {exception}")
                continue
            logging.info(f"{title} injection successful")
            continue

    @staticmethod
    def get_js(js_path: str) -> str:
        """Get JavaScript content in file

        Args:
            js_path [str]: Path of JavaScript file

        Returns:
            [str]: JavaScript code
        """
        with open(js_path, "r") as file_obj:
            data = file_obj.read().strip()
        return data


class WinDiscordHideSidebar(DiscordHideSidebar):
    """Special variables/functions for Windows"""
    DEFAULT_DISCORD_PATH_PATTERN = os.path.join(
        os.path.expandvars(r"%LocalAppData%"),
        r"Discord\*\Discord.exe"
    )

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
