# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.0"
__date__ = "2023-03-03"
# Created: 2017-04-15 14:46

from typing import Any, Dict, List, Optional, Union

import nameko.exceptions
import nameko.rpc

from .manager import Manager
from ..dto import BasicMessage, InputMessage, IntentMessage


class IntentManager(Manager):
    """ Manager handling and distributing intents """

    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """ Constructor """
        if settings is None:
            settings = {}

        super().__init__(settings)

        self._intents: List[str] = settings.get("intents", [])

        if self._intents is None:
            raise ValueError("No intents set")

        self.debug("Intents: {}".format(self._intents))

    def _setup(self) -> None:
        """ Setup listeners """
        super()._setup()
        self._register("manager_intent", "input_new", "IntentManager")

    def react_nameko(
            self, exchange: str, routing_key: str, msg: Dict[str, Any]
    ) -> bool:
        """
        React to nameko events

        :return: Accept the input or refuse it
        """
        return False

    def react(
            self,
            exchange: str,
            routing_key: str,
            msg: Union[Dict[str, Any], BasicMessage],
    ) -> bool:
        """
        React to custom events

        :params exchange: Exchange the event was received on
        :params routing_key: Routing key the event was received on
        :params msg: Event data (InputMessage)
        :return: Accept the input or refuse it
        :raises TypeError: Msg is not InputMessage
        """
        self.debug(f"{exchange}-{routing_key}: {msg}")

        if not isinstance(msg, InputMessage):
            raise TypeError("Expected an InputMessage")

        if exchange == "manager_intent":
            if routing_key == "input_new":
                self._do_input_new(msg)

                return True

        return False

    def act(self, intent: IntentMessage) -> None:
        """
        Tell actor manager to act on intent

        :param intent: Intent to act on
        """
        self.debug(intent)
        self.emit(intent, self.get_exchange("manager_actor"))

    def _do_input_new(self, msg: InputMessage) -> None:
        """
        Retrieve intent for input message

        :param msg: Input message to react to
        :raises ValueError: No source in msg
        """
        likes: List[str] = []
        max_like: float = -1.0
        self.debug(msg)

        if not msg.source:
            # Only allow messages with valid source field
            self.error("No source specified for message")

            raise ValueError("No source set in message")

        # Ask all intents who like it
        for intent in self._intents:
            self.debug(f"Attempting intent {intent}")
            intent = f"service_intent_{intent}"

            try:
                ilike: float = self.proxy[intent].likes(msg)
            except nameko.exceptions.UnknownService:
                self.error(f"No intent '{intent}' found")

                continue
            except Exception:
                self.exception(
                    f"Failed to get likes from {intent}:\n{msg}"
                )

                continue

            if ilike > max_like:
                # New like high score
                likes = [intent]
                max_like = ilike
            elif ilike == max_like:
                # Likes the same
                likes.append(intent)

        # Error if none like it
        if not likes or max_like <= 0:
            self.error("No intent likes:\n{}".format(msg))
            self.say_error(msg.source, msg, "No intent found")

            return

        # Give it to those that like it the most
        intent_msgs: List[IntentMessage] = []

        for intent in likes:
            try:
                intent_msgs.append(
                    self.proxy[intent].intent(msg)
                )
            except Exception:
                self.exception(
                    f"Failed to get intent from {intent}:\n{msg}"
                )

        if not intent_msgs:
            self.error(f"No intents gathered\n{msg}")
            self.say_error(msg.source, msg, "No intents gathered")

            return

        # Act on intends
        for intent_msg in intent_msgs:
            try:
                self.act(intent_msg)
            except Exception:
                self.exception(
                    f"Failed act on intent\n{msg}"
                )
                self.say_error(
                    msg.source, msg, f"Failed act on intent\n{intent_msg}"
                )

    def start(self, blocking: bool = False):
        """ Setup and start instance """
        self._setup()
        super().start(blocking)
