# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2016-23, Florian JUNG"
__license__ = "All rights reserved"
__version__ = "0.2.0"
__date__ = "2023-02-26"
# Created: 2016-08-19 19:41

import threading
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from flotils import Loadable
from flotils.runable import StartStopable
from kombu import Connection, Exchange, Queue
import kombu.message
from kombu.mixins import ConsumerMixin


T = TypeVar("T")
T_Class = Type[T]


class EventListener(ConsumerMixin, Loadable, StartStopable):
    """ Listen for incoming messages """

    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """ Constructor """
        if settings is None:
            settings = {}

        Loadable.__init__(self, settings)
        StartStopable.__init__(self, settings)

        self._broker_url: str = settings['AMQP_URI']
        self._heartbeat: float = settings.get('heartbeat', None)
        self._prefetch_count: int = settings.get('prefetch_count', 1)
        """ Number of messages to get from the broker at a time (consumer) """
        events: List[Dict[str, Union[str, Callable]]] = settings.get('events', [])
        """ Which events to monitor """
        self._exchanges: Dict[str, Exchange] = {}
        """ Created exchanges """
        self.process_message: Optional[
            Callable[[str, str, Any], bool]
        ] = settings.get('process_message')
        """ Process function """
        self.connection: Optional[Connection] = None
        """ Connection to broker """
        self._queues: List[Queue] = []
        """ Queues listening on """
        self._accept_formats: List[str] = settings.get('accept_formats', ["json"])
        """ Which formats for serialization to support """
        self.info("Registering events..")

        for event in events:
            if "pub_service_name" in event:
                self.debug(f"Registering as nameko event:\n{event}")
                self.register_nameko_event(**event)  # type: ignore
            elif "exchange" in event:
                self.debug(f"Registering as normal event:\n{event}")
                self.register_event(**event)  # type: ignore
            else:
                self.error(f"Could not register event:\n{event}")

    def _thread_wrapper(self, func: Callable) -> None:
        """
        Wrap function for exception handling with threaded calls

        :param func: Function to call
        """
        try:
            func()
        except Exception:
            self.exception("Threaded execution failed")

    def register_event(
            self,
            exchange_name: str, exchange_type: str,
            queue_name: str,
            routing_key: str,
            queue_durable: bool = True,
            queue_auto_delete: bool = False,
            exchange_auto_delete: bool = False,
    ) -> None:
        """
        Register given event to listen for

        :param exchange_name: Name of the exchange for this event
        :param exchange_type: Type of exchange to set up
        :param queue_name: Name of queue to associate with
        :param routing_key: Routing for incoming messages
        :param queue_durable: Should the queue be durable (not deleted without consumer)
        :param queue_auto_delete: Auto-delete queue
        :param exchange_auto_delete: Auto-delete exchange
        """
        self.debug(
            "Registering Exchange({}, {})".format(exchange_name, exchange_type)
        )
        self.debug(
            "Registering Queue({}, {})".format(queue_name, routing_key)
        )
        if exchange_name not in self._exchanges:
            self._exchanges[exchange_name] = Exchange(
                exchange_name,
                type=exchange_type,
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
            pub_service_name: str,
            pub_event_type: str,
            exchange_type: str = "topic",
            sub_service_name: Optional[str] = None,
            sub_handle_name: str = "handle_event",
    ) -> None:
        """
        Register given nameko event to listen for
        Exchange is auto deletable

        :param pub_service_name: Service name to listen to
        :param pub_event_type: Type of listen event
        :param exchange_type: Type of exchange to use (default: topic)
        :param sub_service_name: Service name that is listening for events
        :param sub_handle_name: Function to call with events (default: handle_event)
        """
        self.register_event(
            f"{pub_service_name}.events",
            exchange_type,
            f"evt-{pub_service_name}.{pub_event_type}--"
            f"{sub_service_name}.{sub_handle_name}",
            pub_event_type,
            exchange_auto_delete=True,
        )

    def get_consumers(self, consumer_class: T_Class, channel: Any) -> List[T]:
        """ Get a single consumer for incoming messages """
        self.debug("()")

        return [consumer_class(
            queues=self._queues,
            accept=self._accept_formats,
            callbacks=[self._process_message],
            prefetch_count=self._prefetch_count,
        )]

    def _process_message(self, body: Any, message: kombu.message.Message) -> None:
        """
        Called whenever a message is received

        :param body: Decoded message body
        :param message: Message instance
        """
        exchange: str = message.delivery_info['exchange']
        routing_key: str = message.delivery_info['routing_key']

        if self.process_message:
            try:
                self.process_message(exchange, routing_key, body)
            except Exception:
                self.exception("Failed to call process function")
        else:
            self.warning("No process function found")

        # TODO: Send occurred errors via message
        message.ack()

    def _run_worker(self) -> None:
        """ Connect and run worker """
        with Connection(self._broker_url, heartbeat=self._heartbeat) as conn:
            self.connection = conn
            self.run()

    def start(self, blocking: bool = False):
        """ Start instance """
        super().start(False)

        if not blocking:
            try:
                a_thread = threading.Thread(
                    target=self._thread_wrapper,
                    args=(self._run_worker,)
                )
                a_thread.daemon = True
                a_thread.start()
            except Exception:
                self.exception("Failed to run receive loop")
                self.stop()

                return
        else:
            self._run_worker()

    def stop(self):
        """ Stop instance """
        self.should_stop = True

        super().stop()

        self._exchanges = {}
        self._queues = []
