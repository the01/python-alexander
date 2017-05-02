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
# Created: 2017-05-01 23:47

# based on nameko
import warnings
from kombu import Exchange
from six.moves import queue

from nameko.amqp import get_connection, get_producer, UndeliverableMessage
from nameko.constants import (
    DEFAULT_RETRY_POLICY, DEFAULT_SERIALIZER, SERIALIZER_CONFIG_KEY)
from nameko.messaging import AMQP_URI_CONFIG_KEY, PERSISTENT
from nameko.messaging import Publisher


def get_exchange(service_name):
    exchange_name = "{}".format(service_name)
    exchange = Exchange(
        exchange_name, type="topic", durable=True, auto_delete=False,
        delivery_mode=PERSISTENT
    )
    return exchange


def event_dispatcher(nameko_config, **kwargs):
    """ Return a function that dispatches nameko events.
    """
    amqp_uri = nameko_config[AMQP_URI_CONFIG_KEY]

    kwargs = kwargs.copy()
    retry = kwargs.pop('retry', True)
    retry_policy = kwargs.pop('retry_policy', DEFAULT_RETRY_POLICY)
    use_confirms = kwargs.pop('use_confirms', True)
    mandatory = kwargs.pop('mandatory', False)

    def dispatch(service_name, event_type, event_data):
        """ Dispatch an event claiming to originate from `service_name` with
        the given `event_type` and `event_data`.
        """
        serializer = nameko_config.get(
            SERIALIZER_CONFIG_KEY, DEFAULT_SERIALIZER)

        exchange = get_exchange(service_name)

        with get_connection(amqp_uri) as connection:
            exchange.maybe_bind(connection)  # TODO: reqd? maybe_declare?
            with get_producer(amqp_uri, use_confirms) as producer:
                msg = event_data
                routing_key = event_type
                producer.publish(
                    msg,
                    exchange=exchange,
                    serializer=serializer,
                    routing_key=routing_key,
                    retry=retry,
                    retry_policy=retry_policy,
                    mandatory=mandatory,
                    **kwargs)

                if mandatory:
                    if not use_confirms:
                        warnings.warn(
                            "Mandatory delivery was requested, but "
                            "unroutable messages cannot be detected without "
                            "publish confirms enabled."
                        )

                    try:
                        returned_messages = producer.channel.returned_messages
                        returned = returned_messages.get_nowait()
                    except queue.Empty:
                        pass
                    else:
                        raise UndeliverableMessage(returned)

    return dispatch


class EventDispatcher(Publisher):
    """ Provides an event dispatcher method via dependency injection.
    Events emitted will be dispatched via the service's events exchange,
    which automatically gets declared by the event dispatcher
    as a topic exchange.
    The name for the exchange will be `{service-name}.events`.
    Events, emitted via the dispatcher, will be serialized and published
    to the events exchange. The event's type attribute is used as the
    routing key, which can be used for filtering on the listener's side.
    The dispatcher will return as soon as the event message has been published.
    There is no guarantee that any service will receive the event, only
    that the event has been successfully dispatched.
    Example::
        class Spammer(object):
            dispatch_spam = EventDispatcher()
            def emit_spam(self):
                evt_data = 'ham and eggs'
                self.dispatch_spam('spam.ham', evt_data)
    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.service_name = "manager_intent"
        super(EventDispatcher, self).__init__()

    def setup(self):
        self.config = self.container.config
        self.exchange = get_exchange(self.service_name)
        super(EventDispatcher, self).setup()

    def get_dependency(self, worker_ctx):
        """ Inject a dispatch method onto the service instance
        """
        headers = self.get_message_headers(worker_ctx)
        kwargs = self.kwargs
        dispatcher = event_dispatcher(self.config, headers=headers, **kwargs)

        def dispatch(event_type, event_data):
            dispatcher(self.service_name, event_type, event_data)
        return dispatch
