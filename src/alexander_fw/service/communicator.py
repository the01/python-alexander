# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-22, Florian JUNG"
__license__ = "MIT"
__version__ = "0.3.0"
__date__ = "2022-11-15"
# Created: 2017-05-01 23:55


import abc
import logging
from typing import Any, Callable, List, Optional

from nameko.rpc import rpc
from seta.service import MetricService

from .dispatcher import EventDispatcher
from ..dto import ActorMessage, InputMessage


logger = logging.getLogger(__name__)


class StandaloneCommunicatorService(abc.ABC):
    """ Base class for standalone communicator interface """

    name: str = "service_communicator"
    __version__: str = "unset"
    allowed: List[str] = ["status", "version", "say"]
    """ List of allowed functions """
    dispatch_intent: Optional[Callable[[str, InputMessage], None]] = None
    """ Function to dispatch an intent to the intent manager """

    def communicate(self, msg: InputMessage) -> None:
        """
        Communicate incoming message to intent manager

        :param msg: New input
        :raises ValueError: dispatch_intent was not set
        """
        if self.dispatch_intent is None:
            raise ValueError("No dispatch intent set")

        msg.source = self.name
        logger.debug(msg.to_dict())
        self.dispatch_intent("input_new", msg)

    def status(self) -> str:
        """
        Service status

        :return: Status
        """
        logger.debug("()")

        return "ok"

    def version(self) -> str:
        """
        Service version

        :return: Version
        """
        logger.debug("()")

        return self.__version__

    def say(self, msg: ActorMessage) -> Any:
        """
        Send a message through this communicator

        :param msg: Message to send
        :return: Result
        """
        return self.do_say(msg)

    @abc.abstractmethod
    def do_say(self, msg: ActorMessage) -> Any:
        """
        Do the actual sending

        :param msg: Message to send
        :return: Result
        """
        raise NotImplementedError()


class CommunicatorService(StandaloneCommunicatorService, MetricService, abc.ABC):
    """ Base class for standalone communicator with metrics """

    dispatch_intent = EventDispatcher()

    @rpc
    def status(self) -> str:
        """
        Service status

        :return: Status
        """
        return super().status()

    @rpc
    def say(self, msg: ActorMessage) -> Any:
        """
        Send a message through this communicator

        :param msg: Message to send
        :return: Result
        """
        return super().say(msg)
