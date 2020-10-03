#!/usr/bin/env python3
"""A module that stores the actions"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional

import websocket

logger = logging.getLogger(__name__)

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
        log = f"[{type(self).__name__}.__init__]"
        self.name = name
        self.js_path = JS_DIR_PATH / JS_NAMES[name]
        self.payload = self.get_js_payload()
        logger.debug(f"{log} Initialized: {self.__dict__}")

    def get_js_payload(self) -> str:
        """Get JS and generate JSON

        Returns:
            [str]: JSON payload for the JavaScript
        """
        log = f"[{type(self).__name__}.get_js_payload]"
        # Test JavaScript path validity
        if not self.js_path.is_file():
            logger.critical(f"{log} \"{self.js_path}\" is not a file")
            raise FileNotFoundError(f"\"{self.js_path}\" is not a file!")
        # Read JavaScript
        with self.js_path.open("r") as file_obj:
            js = file_obj.read().strip()
        # Assemble data
        payload = self.gen_payload(js)
        return payload

    def gen_payload(self, js: str) -> str:
        """Generate payload JSON from JavaScript

        Args:
            js [str]: JavaScript string

        Returns:
            [str]: JSON payload
        """
        log = f"[{type(self).__name__}.gen_payload]"
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
        logger.debug(f"{log} Payload: {data_json}")
        return data_json

    def run(self) -> None:
        log = f"[{type(self).__name__}.run]"
        logger.critical(f"{log} Unimplemented `run`")
        raise NotImplementedError(
            f"Class `{type(self).__name__}` does not have `run` method!"
        )

    def ws_req_and_res(self, window: Dict[str, str]) -> int:
        """Send request to WebSocket and check success

        Args:
            window [Dict[str, str]]: Window info

        Returns:
            [int]: Error codes: 0 is successful, 1 is error, -1 is unknown
        """
        log = f"[{type(self).__name__}.ws_req_and_res]"
        logger.debug(f'{log} Title: \"{window["title"]}\"')
        if window["title"].lower() in self.TITLE_BLACKLIST:
            logger.debug(f"{log} Title in lacklist (1)")
            return 1
        socket_url = window[self.SOCKET_URL_KEY]
        ws = self.ws_req(socket_url)
        if ws is None:
            logger.debug(f"{log} No response from WebSocket (1)")
            return 1
        ws.send(self.payload)
        response: Optional[str] = ws.recv()
        err_code = self.parse_ws_response(response, window)
        return err_code

    def ws_req(self, url: str) -> Optional[websocket.WebSocket]:
        """Establish WebSocket to URL, with proper error handling

        Args:
            url [str]: URL to WebSocket

        Returns:
            [Optional[websocket.WebSocket]]: WebSocket connection, if any
        """
        log = f"[{type(self).__name__}.ws_req]"
        try:
            ws = websocket.create_connection(url)
        except ConnectionRefusedError as err:
            # Possibly the program has exited
            logger.warn(f"{log} WebSocket to \"{url}\" refused {err}")
            return
        except ConnectionResetError as err:
            # Possibly the program has crashed
            logger.warn(f"{log} WebSocket to \"{url}\" reset {err}")
            return
        except websocket.WebSocketBadStatusException as err:
            # Possibly the window is changed
            logger.warn(f"{log} WebSocket to \"{url}\" bad status {err}")
            return
        logger.info(f"{log} WebSocket to \"{url}\" successful")
        return ws

    def parse_ws_response(self, response: Optional[str], window: Dict[str, str]) -> int:
        """Parse WebSocket response and act accordingly

        Args:
            response [Optional[str]] : Response from WebSocket
            window   [Dict[str, str]]: Window info

        Returns:
            [int]: Error codes: 0 is successful, 1 is error, -1 is unknown
        """
        log = f"[{type(self).__name__}.parse_ws_response]"
        title = f"\'{window['title']}\'"
        if response is None:
            logger.warn(f"{log} \"{title} {self.name}\" response empty")
            return -1
        response_dict: Dict = json.loads(response)
        logger.debug(
            f"{log} Got response from { window[self.SOCKET_URL_KEY]}: {response_dict}"
        )
        if "result" not in response_dict:
            logger.warn(
                f"{log} {title} {self.name} response has no 'result'"
            )
            return -1
        result = response_dict["result"]
        if "exceptionDetails" in result:
            exception_details = result["exceptionDetails"]
            if "exception" not in exception_details:
                logger.warn(
                    f"{log} {title} {self.name} failed but no details"
                )
            else:
                exception = exception_details["exception"]
                logger.warn(
                    f"{log} {title} {self.name} failed by {exception}"
                )
            return 1
        logger.info(f"{log} {title} {self.name} successful")
        return 0


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
        log = f"[{type(self).__name__}.run]"
        err_code = self.ws_req_and_res(window)
        if err_code == 0:
            logger.info(
                f"{log} WebSocket request and response returned {err_code}"
            )
            return True
        else:
            logger.warn(
                f"{log} WebSocket request and response returned {err_code}"
            )
            return False


@dataclass
class Actions:
    """A collection of actions

    Properties:
        init   [InitAction]  : `init` action
    """

    init: InitAction


ACTIONS = Actions(InitAction())
