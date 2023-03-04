# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.0"
__date__ = "2023-03-02"
# Created: 2017-07-21 13:38

import sys
import threading
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from flotils import Loadable, StartStopable
from kombu import Connection, Exchange, producers, Queue
from kombu.mixins import ConsumerMixin
import kombu.serialization
from nameko.exceptions import (
    MalformedRequest, MethodNotFound, serialize, UnserializableValueError
)


T = TypeVar("T")
T_Class = Type[T]


class RPCListener(ConsumerMixin, Loadable, StartStopable):
    """ Standalone receiver for rpc calls """

    def __init__(self, settings: Optional[Dict[str, Any]] = None) -> None:
        """ Constructor """
        if settings is None:
            settings = {}

        ConsumerMixin.__init__(self)
        Loadable.__init__(self, settings)
        StartStopable.__init__(self, settings)

        self._broker_url: str = settings['AMQP_URI']
        self._heartbeat: Optional[float] = settings.get('heartbeat', None)
        self._serializer: Union[str, List[str]] = settings.get('serializer', "json")
        """ Which formats for serialization to support """
        self._connection_timeout: float = settings.get('connection_timeout', 2.0)
        """ Timeout of timeout """
        self.service: Any = settings.get('service')
        """ Service to call """
        self.allowed_functions: Optional[List[str]] = settings.get('allowed_functions')
        """ Which functions on the service are callable (None means all) """
        self.connection: Optional[Connection] = None
        """ Connection to broker """
        self._nameko_exchange_rpc_name: str = settings.get(
            'rpc_exchange', "nameko-rpc"
        )
        """ Name of exchange """
        self._nameko_exchange_rpc: Optional[Exchange] = None
        self._nameko_queue_rpc: Optional[Queue] = None
        self._service_name = settings['service_name']

    def _thread_wrapper(self, func: Callable, *args, **kwargs) -> None:
        """
        Wrap function for exception handling with threaded calls

        :param func: Function to call
        :param args: Tuple arguments
        :param kwargs: Dict arguments
        """
        try:
            func(*args, **kwargs)
        except Exception:
            self.exception("Threaded execution failed")

    def _register_service(self, service_name: str) -> None:
        """ Register a service for rpc calls"""
        if self._nameko_exchange_rpc is None:
            self._nameko_exchange_rpc = Exchange(
                self._nameko_exchange_rpc_name, type="topic",
                auto_delete=False, durable=True
            )
        self._nameko_queue_rpc = Queue(
            "rpc-{}".format(service_name),
            self._nameko_exchange_rpc,
            routing_key="{}.*".format(service_name),
            durable=True
        )

    def get_consumers(self, consumer_class: T_Class, channel: Any) -> List[T]:
        """ Create consumer on queue rpc """
        return [consumer_class(
            queues=[self._nameko_queue_rpc],
            accept=[self._serializer],
            callbacks=[self._process_message]
        )]

    def _process_message(self, body: Any, message: kombu.message.Message) -> None:  # noqa: C901
        """
        Called whenever a message is received

        :param body: Decoded message body
        :param message: Message instance
        """
        correlation_id = message.properties.get('correlation_id')
        routing_key = message.properties['reply_to']
        called = message.delivery_info.get('routing_key', "")
        exec_info = None
        error = None
        result = None
        args = kwargs = None

        if called:
            parts = called.split(".")

            if len(parts) == 2:
                called = parts[1]
            else:
                called = None

        if not called:
            self.error("No method called: '{}'".format(
                message.delivery_info.get('routing_key')
            ))
            error = serialize(MethodNotFound("No method given"))

        if self.service and called:
            message.ack()

            try:
                try:
                    args = body['args']
                    kwargs = body['kwargs']
                except KeyError:
                    raise MalformedRequest("Message missing `args` or `kwargs`")

                fn = None

                # Only allowed methods
                if self.allowed_functions is None \
                        or called in self.allowed_functions:
                    # Attempt to call
                    fn = getattr(self.service, called, None)

                    if callable(fn):
                        result = fn(*args, **kwargs)
                    else:
                        error = serialize(MethodNotFound(
                            "No such Method on service"
                        ))
                else:
                    error = serialize(MethodNotFound("Method not allowed"))
            except Exception:
                self.exception("Failed to call process method")
                exec_info = sys.exc_info()
                result = None
        else:
            self.warning("No service found")
            message.ack()

            if not error:
                error = serialize(MethodNotFound("No service found"))

        if exec_info is not None:
            # TODO: Serialize
            try:
                error = kombu.serialization.dumps(exec_info, self._serializer)
            except Exception:
                self.exception("Failed to serialize exec_info")
                error = "{}".format(exec_info)
        elif error is None:
            # Check that kombu is able to serialize data
            try:
                kombu.serialization.dumps(result, self._serializer)
            except Exception:
                error = serialize(UnserializableValueError(result))
                result = None

        msg = {
            'result': result,
            'error': error
        }

        with producers[self.connection].acquire(
                block=True, timeout=self._connection_timeout
        ) as producer:
            producer.publish(
                msg,
                compression="bzip2",
                exchange=self._nameko_exchange_rpc_name,
                retry=True,
                routing_key=routing_key,
                serializer=self._serializer,
                correlation_id=correlation_id
            )

    def _run_worker(self) -> None:
        """ Connect and run worker """
        self._register_service(self._service_name)

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

        self._nameko_queue_rpc = None
        self._nameko_queue_rpc = None
