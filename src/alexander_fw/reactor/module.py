# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.0"
__date__ = "2023-03-02"
# Created: 2017-04-15 14:06

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from .emitter import EmitterModule
from .events import EventListener
from ..dto import BasicMessage


class ReactorModule(EmitterModule, ABC):
    """ React to incoming messages """

    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """ Constructor """
        if settings is None:
            settings = {}

        super().__init__(settings)

        nameko_sett: dict = settings['nameko']
        nameko_sett.setdefault('AMQP_URI', self._broker)
        nameko_sett.setdefault('serializer', self._serializer)

        evt_sett = settings.get("event_listener", {})
        evt_sett.setdefault('AMQP_URI', self._broker)
        evt_sett.setdefault('accept_formats', [self._serializer])

        evt_sett_nameko = dict(evt_sett)
        evt_sett_nameko.setdefault('id', "nameko")
        evt_sett_nameko['AMQP_URI'] = nameko_sett['AMQP_URI']
        evt_sett_nameko.update(settings.get("event_listener_nameko", {}))

        self._event_listener = EventListener(evt_sett)
        self._event_listener.process_message = self.react
        self._event_listener_nameko = EventListener(evt_sett_nameko)
        self._event_listener_nameko.process_message = self.react_nameko

    def class_name(self) -> str:
        """ Function to get class name """
        return self.__class__.__name__

    def _register(
            self, exchange: str, routing_key: str, queue: Optional[str] = None
    ) -> None:
        """
        Register event listening

        :param exchange: Which exchange should the event use
        :param routing_key: Routing key for event
        :param queue: Which queue should it be added to (defaults to own class name)
        """
        if queue is None:
            queue = self.class_name()

        self._event_listener.register_event(
            exchange, "topic", queue, routing_key
        )

    def _register_nameko(self, pub_service_name: str, pub_event_type: str) -> None:
        """
        Register a nameko event listener

        :param pub_service_name: Which service to listen for
        :param pub_event_type: Name of event
        """
        self._event_listener_nameko.register_nameko_event(
            pub_service_name, pub_event_type, "topic",
            sub_service_name=self.class_name()
        )

    @abstractmethod
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
        :param msg: The received message
        :return: Accept the input or refuse it
        """
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    def start(self, blocking: bool = False) -> None:
        """ Start instance """
        self._event_listener.start(False)
        self._event_listener_nameko.start(False)

        super().start(blocking)

    def stop(self) -> None:
        """ Stop instance """
        if not self._is_running:
            # Already stopped
            return

        try:
            self._event_listener.stop()
        except Exception:
            self.exception("Failed to stop event listener")

        try:
            self._event_listener_nameko.stop()
        except Exception:
            self.exception("Failed to stop event listener nameko")

        super().stop()
