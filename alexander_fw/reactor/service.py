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
__date__ = "2017-07-21"
# Created: 2017-07-21 13:38

import threading
import sys

import kombu.serialization
from kombu import Exchange, Connection, Queue, producers
from kombu.mixins import ConsumerMixin
from nameko.exceptions import (
    ContainerBeingKilled, MalformedRequest, MethodNotFound,
UnknownService, UnserializableValueError, deserialize, serialize)
from flotils import Loadable, StartStopable


class RPCListener(ConsumerMixin, Loadable, StartStopable):

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        ConsumerMixin.__init__(self)
        Loadable.__init__(self, settings)
        StartStopable.__init__(self, settings)

        self._broker_url = settings['AMQP_URI']
        self._heartbeat = settings.get('heartbeat', None)
        self._serializer = settings.get('serializer', "json")
        """ Which formats for serialization to support
            :type : list[unicode] """
        self._connection_timeout = settings.get('connection_timeout', 2.0)
        """ Timeout of timeout
            :type : float """
        self.service = settings.get('service')
        """ Service to call
            :type : object """
        self.allowed_functions = settings.get('allowed_functions')
        """ Which functions on the service are callable (None means all)
            :type : None | list[unicode] """
        self.connection = None
        """ Connection to broker
            :type : None | kombu.Connection """
        self._nameko_exchange_rpc_name = settings.get(
            'rpc_exchange', "nameko-rpc"
        )
        """ Name of exchange
            :type : unicode """
        self._nameko_exchange_rpc = None
        """ :type : None | kombu.Exchange """
        self._nameko_queue_rpc = None
        """ :type : None | kombu.Queue """
        self._service_name = settings['service_name']

    def _thread_wrapper(self, func, *args, **kwargs):
        """
        Wrap function for exception handling with threaded calls

        :param func: Function to call
        :type func: callable
        :param args: Tuple arguments
        :type args: ()
        :param kwargs: Dict arguments
        :type kwargs: dict
        :rtype: None
        """
        try:
            func(*args, **kwargs)
        except:
            self.exception("Threaded execution failed")

    def _register_service(self, service_name):
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

    def get_consumers(self, Consumer, channel):
        return [Consumer(
            queues=[self._nameko_queue_rpc],
            accept=[self._serializer],
            callbacks=[self._process_message]
        )]

    def _process_message(self, body, message):
        """
        Called whenever a message is received

        :param body: Decoded message body
        :type body: object
        :param message: Message instance
        :type message: kombu.message.Message
        :rtype: None
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
            except:
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
            except:
                self.exception("Failed to serialize exec_info")
                error = "{}".format(exec_info)
        elif error is None:
            # Check that kombu is able to serialize data
            try:
                kombu.serialization.dumps(result, self._serializer)
            except:
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

    def _run_worker(self):
        """
        Connect and run worker

        :rtype: None
        """
        self._register_service(self._service_name)
        with Connection(self._broker_url, heartbeat=self._heartbeat) as conn:
            self.connection = conn
            self.run()

    def start(self, blocking=False):
        super(RPCListener, self).start(False)
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
        super(RPCListener, self).stop()
        self._nameko_queue_rpc = None
        self._nameko_queue_rpc = None
