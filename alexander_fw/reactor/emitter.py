# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.0"
__date__ = "2017-05-01"
# Created: 2017-05-01 19:47

from abc import ABCMeta
import datetime
import uuid

from flotils import Loadable, StartStopable
from kombu import producers, Connection, Exchange

from ..dto import InputMessage, IntentMessage, ActorMessage


class EmitterModule(Loadable, StartStopable):
    __metaclass__ = ABCMeta

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(EmitterModule, self).__init__(settings)
        nameko_sett = settings['nameko']
        self._broker = settings.get('broker', nameko_sett.get('AMQP_URI'))
        self._serializer = settings.get(
            'serializer', nameko_sett.get('serializer', "datetimejson")
        )
        self._connection_timeout = settings.get('connection_timeout', 2.0)

        self._connection = Connection(self._broker)
        self._com_exchanges = {}

    def get_exchange(self, key):
        if key not in self._com_exchanges:
            self._com_exchanges[key] = Exchange(
                key, type="topic", durable=True, auto_delete=False
            )
        return self._com_exchanges[key]

    def emit(self, message, exchange):
        """
        Emit data

        :param message: Message data to emit
        :type message: dto.InputMessage | dto.IntentMessage
        :param exchange: Exchange to publish message on
        :type exchange: kombu.Exchange
        :rtype: None
        """
        if isinstance(message, ActorMessage):
            routing_key = "say"
        elif isinstance(message, IntentMessage):
            routing_key = "intent_new"
        elif isinstance(message, InputMessage):
            routing_key = "input_new"
        else:
            self.error("No routing key for\n{}".format(message))
            raise ValueError("No routing key")
        if message.timestamp is None:
            message.timestamp = datetime.datetime.utcnow()
        if message.uuid is None:
            message.uuid = "{}".format(uuid.uuid4())
        # self.debug("{}:\n{}".format(routing_key, message))
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
