# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2016, Florian JUNG"
__license__ = "All rights reserved"
__version__ = "0.1.2"
__date__ = "2017-04-20"
# Created: 2016-08-19 19:41

import threading

from kombu import Exchange, Connection, Queue
from kombu.mixins import ConsumerMixin
from kombu.serialization import register
from flotils.runable import StartStopable
from flotils import Loadable


def setup_kombu():
    from ..dto.utils import encode, decode
    register(
        "datetimejson", encode, decode, "application/datetime-json", "utf-8"
    )


class EventListener(ConsumerMixin, Loadable, StartStopable):

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        Loadable.__init__(self, settings)
        StartStopable.__init__(self, settings)
        self._broker_url = settings['AMQP_URI']
        self._heartbeat = settings.get('heartbeat', None)
        events = settings.get('events', [])
        """ Which events to monitor
            :type : list[dict[unicode, unicode | callable]] """
        self._exchanges = {}
        """ Created exchanges
            :type : dict[unicode, kombu.Exchange] """
        self.process_message = settings.get('process_message')
        """ Process function
            :type : callable """
        self.connection = None
        """ Connection to broker
            :type : kombu.Connection """
        self._queues = []
        """ Queues listening on
            :type : list[kombu.Queue] """
        self._accept_formats = settings.get('accept_formats', ["json"])
        """ Which formats for serialization to support
            :type : list[unicode] """
        self.info("Registering events..")
        for event in events:
            if "pub_service_name" in event:
                self.debug("Registering as nameko event:\n{}".format(event))
                self.register_nameko_event(**event)
            elif "exchange" in event:
                self.debug("Registering as normal event:\n{}".format(event))
                self.register_event(**event)
            else:
                self.error("Could not register event:\n{}".format(event))

    def _thread_wrapper(self, func):
        """
        Wrap function for exception handling with threaded calls

        :param func: Function to call
        :type func: callable
        :rtype: None
        """
        try:
            func()
        except:
            self.exception("Threaded execution failed")

    def register_event(
            self, exchange_name, exchange_type, queue_name, routing_key,
            queue_durable=True,
            queue_auto_delete=False, exchange_auto_delete=False
    ):
        self.debug(
            "Registering Exchange({}, {})".format(exchange_name, exchange_type)
        )
        self.debug(
            "Registering Queue({}, {})".format(queue_name, routing_key)
        )
        if exchange_name not in self._exchanges:
            self._exchanges[exchange_name] = Exchange(
                exchange_name, type=exchange_type,
                auto_delete=exchange_auto_delete
            )
        exchange = self._exchanges[exchange_name]
        self._queues.append(Queue(
            queue_name, exchange, routing_key=routing_key
        ))
        self._queues[-1].durable = queue_durable
        self._queues[-1].auto_delete = queue_auto_delete

    def register_nameko_event(
            self,
            pub_service_name, pub_event_type, exchange_type="topic",
            sub_service_name=None, sub_handle_name="handle_event"
    ):
        self.register_event(
            "{}.events".format(pub_service_name), exchange_type,
            "evt-{}.{}--{}.{}".format(
                pub_service_name, pub_event_type,
                sub_service_name, sub_handle_name
            ), pub_event_type, exchange_auto_delete=True
        )

    def get_consumers(self, Consumer, channel):
        self.debug("()")
        return [Consumer(
            queues=self._queues,
            accept=self._accept_formats,
            callbacks=[self._process_message]
        )]

    def _process_message(self, body, message):
        exchange = message.delivery_info['exchange']
        routing_key = message.delivery_info['routing_key']

        if self.process_message:
            try:
                self.process_message(exchange, routing_key, body)
            except:
                self.exception("Failed to call process function")
        else:
            self.warning("No process function found")
        # TODO: Send occurred errors via message
        message.ack()

    def _run_worker(self):
        with Connection(self._broker_url, heartbeat=self._heartbeat) as conn:
            self.connection = conn
            self.run()

    def start(self, blocking=False):
        super(EventListener, self).start(False)
        if not blocking:
            try:
                a_thread = threading.Thread(
                    target=self._thread_wrapper,
                    args=(self._run_worker,)
                )
                a_thread.daemon = True
                a_thread.start()
            except:
                self.exception("Failed to run receive loop")
                self.stop()
                return
        else:
            self._run_worker()

    def stop(self):
        self.should_stop = True
        super(EventListener, self).stop()
        self._exchanges = {}
        self._queues = []
