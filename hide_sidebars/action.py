#!/usr/bin/env python3
"""A module that stores the actions"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional

import websocket

JS_DIR_PATH = Path(__file__).resolve().parent.parent / "js"
JS_NAMES = {
    "init": "init.min.js",
}


class Action:
    """One action object

    Class variables:
        SOCKET_URL_KEY [str]: Key name for socket URL

    Properties:
        name    [str]         : Name of action
        js_path [pathlib.Path]: Path of JavaScript file
        payload [str]         : JSON payload
    """

    SOCKET_URL_KEY = "webSocketDebuggerUrl"
    TITLE_BLACKLIST = [
        "discord updater",
    ]

    def __init__(self, name: str) -> None:
        self.name = name
        self.js_path = JS_DIR_PATH / JS_NAMES[name]
        self.payload = self.get_js_payload()

    def get_js_payload(self) -> str:
        """Get JS and generate JSON

        Returns:
            [str]: JSON payload for the JavaScript
        """
        # Test JavaScript path validity
        if not self.js_path.is_file():
            raise FileNotFoundError(f"{self.js_path} is not a file!")
        # Read JavaScript
        with self.js_path.open("r") as file_obj:
            js = file_obj.read().strip()
        # Assemble data
        payload = self.gen_payload(js)
        return payload

    def run(self) -> None:
        raise NotImplementedError(
            f"This class {type(self).__name__} is not fully implemented!"
        )

    def ws_req_and_res(self, window: Dict[str, str]) -> int:
        """Send request to WebSocket and check success

        Args:
            window [Dict[str, str]]: Window info

        Returns:
            [int]: Error codes: 0 is successful, 1 is error, -1 is unknown
        """
        logging.debug(f'\"{window["title"]}\"')
        if window["title"].lower() in self.TITLE_BLACKLIST:
            logging.debug("1 Blacklist")
            return 1
        socket_url = window[self.SOCKET_URL_KEY]
        ws = self.ws_req(socket_url)
        if ws is None:
            return 1
        ws.send(self.payload)
        response: Optional[str] = ws.recv()
        err_code = self.parse_ws_response(response, window)
        return err_code

    def parse_ws_response(self, response: Optional[str], window: Dict[str, str]) -> int:
        """Parse WebSocket response and act accordingly

        Args:
            response [Optional[str]] : Response from WebSocket
            window   [Dict[str, str]]: Window info

        Returns:
            [int]: Error codes: 0 is successful, 1 is error, -1 is unknown
        """
        title = f"\"{window['title']}\""
        if response is None:
            logging.warn(f"{title} {self.name} response empty")
            return -1
        response_dict: Dict = json.loads(response)
        if "result" not in response_dict:
            logging.warn(f"{title} {self.name} response has no 'result'")
            return -1
        result = response_dict["result"]
        if "exceptionDetails" in result:
            exception_details = result["exceptionDetails"]
            if "exception" not in exception_details:
                logging.warn(f"{title} {self.name} failed but no details")
            else:
                exception = exception_details["exception"]
                logging.warn(f"{title} {self.name} failed by {exception}")
            return 1
        logging.info(f"{title} {self.name} successful")
        return 0

    @staticmethod
    def gen_payload(js: str) -> str:
        """Generate payload JSON from JavaScript

        Args:
            js [str]: JavaScript string

        Returns:
            [str]: JSON payload
        """
        data = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": js,
                "objectGroup": "discordHideSidebar",
                "userGesture": True,
            },
        }
        data_json = json.dumps(data)
        return data_json

    @staticmethod
    def ws_req(url: str) -> Optional[websocket.WebSocket]:
        """Establish WebSocket to URL, with proper error handling

        Args:
            url [str]: URL to WebSocket

        Returns:
            [Optional[websocket.WebSocket]]: WebSocket connection, if any
        """
        try:
            ws = websocket.create_connection(url)
        except ConnectionRefusedError:
            # Possibly the program has exited
            logging.warn(f"websocket to {url} refused")
            return
        except ConnectionResetError:
            # Possibly the program has crashed
            logging.warn(f"websocket to {url} reset")
            return
        except websocket.WebSocketBadStatusException:
            # Possibly the window is changed
            logging.warn(f"websocket to {url} bad status")
            return
        return ws


class InitAction(Action):
    """Initialization action"""

    def __init__(self) -> None:
        super().__init__("init")

    def run(self, window: Dict[str, str]) -> bool:
        """Initialization

        Args:
            window [Dict[str, str]]: The window info

        Return:
            [bool]: Whether the initialization is successful
        """
        err_code = self.ws_req_and_res(window)
        return err_code == 0


@dataclass
class Actions:
    """A collection of actions

    Properties:
        init   [InitAction]  : `init` action
    """

    init: InitAction


ACTIONS = Actions(InitAction())
