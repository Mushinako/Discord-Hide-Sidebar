#!/usr/bin/env python3
"""A module that stores the actions"""

import os.path
import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional

import websocket

JS_DIR_PATH = os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
    "js"
)
JS_NAMES = {
    "init": "init.min.js",
    "inject": "inject.min.js",
}


class Action:
    """One action object

    Class variables:
        SOCKET_URL_KEY [str]: Key name for socket URL

    Properties:
        name    [str]: Name of action
        js_path [str]: Path of JavaScript file
        payload [str]: JSON payload
    """

    SOCKET_URL_KEY = "webSocketDebuggerUrl"

    def __init__(self, name: str) -> None:
        self.name = name
        self.js_path = os.path.join(JS_DIR_PATH, JS_NAMES[name])
        self.payload = self.get_js_payload()

    def get_js_payload(self) -> str:
        """Get JS and generate JSON

        Returns:
            [str]: JSON payload for the JavaScript
        """
        # Test JavaScript path validity
        if not os.path.isfile(self.js_path):
            raise FileNotFoundError(f"{self.js_path} is not a file!")
        # Read JavaScript
        with open(self.js_path, "r") as file_obj:
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
        socket_url = window[self.SOCKET_URL_KEY]
        ws = self.ws_req(socket_url)
        if ws is None:
            return False
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


class InjectAction(Action):
    """Injection action"""

    def __init__(self) -> None:
        super().__init__("inject")

    def run(self, info: List[Dict[str, str]]) -> None:
        """Call the functions

        Args:
            info [List[Dict[str, str]]]: List of windows infos
        """
        for window in info:
            err_code = self.ws_req_and_res(window)
            if err_code == 1:
                ACTIONS.init.run(window)
                self.ws_req_and_res(window)


@dataclass
class Actions:
    """A collection of actions

    Properties:
        init   [InitAction]  : `init` action
        inject [InjectAction]: `inject` action
    """

    init: InitAction
    inject: InjectAction


ACTIONS = Actions(InitAction(), InjectAction())
