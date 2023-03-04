# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.0"
__date__ = "2023-03-02"
# Created: 2017-05-01 19:47

from abc import ABC
import datetime
from typing import Any, Dict, Optional, Union
import uuid

from flotils import Loadable, StartStopable
from kombu import Connection, Exchange, producers

from ..dto import ActorMessage, InputMessage, IntentMessage


class EmitterModule(Loadable, StartStopable, ABC):
    """ Class for emitting events """

    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """ Constructor """
        if settings is None:
            settings = {}

        super().__init__(settings)

        nameko_sett: dict = settings['nameko']
        self._broker: str = settings.get('broker', nameko_sett.get('AMQP_URI'))
        """ Url to connect to message broker """
        self._serializer: str = settings.get(
            'serializer', nameko_sett.get('serializer', "datetimejson")
        )
        """ Serializer for data going through the broker """
        self._connection_timeout: float = settings.get('connection_timeout', 2.0)
        """ Timeout for nameko connection """

        self._connection: Connection = Connection(self._broker)
        """ Connection to broker """
        self._com_exchanges: Dict[str, Exchange] = {}
        """ Exchanges this instance uses """

    def get_exchange(self, key: str) -> Exchange:
        """
        Get exchange or create if not already in cache

        :param key: Name of exchange
        :return: The requested exchange
        """
        if key not in self._com_exchanges:
            self._com_exchanges[key] = Exchange(
                key, type="topic", durable=True, auto_delete=False
            )

        return self._com_exchanges[key]

    def emit(
            self,
            message: Union[ActorMessage, InputMessage, IntentMessage],
            exchange: Exchange,
    ) -> None:
        """
        Emit data

        :param message: Message data to emit
        :param exchange: Exchange to publish message on
        """
        if isinstance(message, ActorMessage):
            routing_key = "say"
        elif isinstance(message, IntentMessage):
            routing_key = "intent_new"
        elif isinstance(message, InputMessage):
            routing_key = "input_new"
        else:
            self.error(f"No routing key for\n{message}")

            raise ValueError("No routing key")

        if message.timestamp is None:
            message.timestamp = datetime.datetime.utcnow()
        if message.uuid is None:
            message.uuid = f"{uuid.uuid4()}"

        self._connection.ensure_connection()

        with producers[self._connection].acquire(
                block=True, timeout=self._connection_timeout
        ) as producer:
            producer.publish(
                message,
                compression="bzip2",
                exchange=exchange,
                declare=[exchange],
                retry=True,
                routing_key=routing_key,
                serializer=self._serializer
            )
