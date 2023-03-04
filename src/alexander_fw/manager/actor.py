# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.0"
__date__ = "2023-03-03"
# Created: 2017-04-15 16:59

from typing import Any, Dict, List, Optional, Union

import nameko.exceptions

from .manager import Manager
from ..dto import ActorMessage, BasicMessage, IntentMessage


class ActorManager(Manager):
    """ Manager handling distribution of messages to actors"""

    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """ Constructor """
        if settings is None:
            settings = {}

        super().__init__(settings)

        self._actors: List[str] = settings.get("actors", [])
        """ List of registered actors """

    def _setup(self) -> None:
        """ Setup listeners """
        super()._setup()
        self._register("manager_actor", "intent_new", "ActorManager")

    def react(
            self,
            exchange: str,
            routing_key: str,
            msg: Union[Dict[str, Any], BasicMessage]
    ) -> bool:
        """
        React to incoming message

        :param exchange: What exchange the message came from
        :param routing_key: What routing key was used
        :param msg: The received message (IntentMessage)
        :return: Accept the input or refuse it
        :raises TypeError: Msg is not IntentMessage
        """
        self.debug(f"{exchange}-{routing_key}: {msg}")

        if not isinstance(msg, IntentMessage):
            raise TypeError("Expected an IntentMessage")

        if exchange == "manager_actor":
            if routing_key == "intent_new":
                self._do_act(msg)

                return True

        return False

    def react_nameko(
            self, exchange: str, routing_key: str, msg: Dict[str, Any]
    ) -> bool:
        """
        React to incoming nameko message

        :param exchange: What exchange the message came from
        :param routing_key: What routing key was used
        :param msg: The received message
        :return: Accept the input or refuse it
        """
        return False

    def _do_act(self, msg: IntentMessage) -> None:
        """
        React to message

        :param msg: Received message
        """
        if not isinstance(msg.intent, list):
            msg.intent = [msg.intent]

        for actor in self._actors:
            if actor not in msg.intent:
                # Not matched
                continue
            if not msg.source:
                # Only allow messages with valid source field
                self.error("No source specified for message")

                continue

            actor_service = f"service_actor_{actor}"

            try:
                resp: Optional[ActorMessage] = self.proxy[actor_service].act(msg)
            except nameko.exceptions.UnknownService:
                self.error(f"No actor available: {actor_service}")
                self.say_error(
                    msg.source, msg, f"Unknown {actor_service}"
                )
            except Exception:
                self.exception(f"Failed to act {actor_service}:\n{msg}")
                self.say_error(
                    msg.source, msg, f"Failed {actor_service} to act"
                )
            else:
                self.debug(f"{actor_service} returned: {resp}")

                if resp is not None:
                    self.say_result(resp)

    def start(self, blocking: bool = False):
        """ Setup and start instance """
        self._setup()
        super().start(blocking)
