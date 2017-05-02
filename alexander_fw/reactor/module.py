# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.2"
__date__ = "2017-05-01"
# Created: 2017-04-15 14:06

from abc import ABCMeta, abstractmethod

from .emitter import EmitterModule
from .events import EventListener


class ReactorModule(EmitterModule):
    __metaclass__ = ABCMeta

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(ReactorModule, self).__init__(settings)
        nameko_sett = settings['nameko']
        nameko_sett.setdefault('AMQP_URI', self._broker)
        nameko_sett.setdefault('serializer', self._serializer)

        evt_sett = settings.get("event_listener", {})
        evt_sett.setdefault('AMQP_URI', self._broker)
        evt_sett.setdefault('accept_formats', [self._serializer])

        evt_sett_nameko = dict(evt_sett)
        evt_sett_nameko['AMQP_URI'] = nameko_sett['AMQP_URI']
        evt_sett_nameko.update(settings.get("event_listener_nameko", {}))

        self._event_listener = EventListener(evt_sett)
        self._event_listener.process_message = self.react
        self._event_listener_nameko = EventListener(evt_sett_nameko)
        self._event_listener_nameko.process_message = self.react_nameko

    def class_name(self):
        return self.__class__.__name__

    def _register(self, exchange, routing_key, queue=None):
        if queue is None:
            queue = self.class_name()
        self._event_listener.register_event(
            exchange, "topic", queue, routing_key
        )

    def _register_nameko(self, pub_service_name, pub_event_type):
        self._event_listener_nameko.register_nameko_event(
            pub_service_name, pub_event_type, "topic",
            sub_service_name=self.class_name()
        )

    @abstractmethod
    def react(self, exchange, routing_key, msg):
        """
        React to input

        :param exchange: What exchange the message came from
        :type exchange: unicode
        :param routing_key: What routing key was used
        :type routing_key: unicode
        :param msg: The received message
        :type msg: dict
        :return: Accept the input or refuse it
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    def react_nameko(self, exchange, routing_key, msg):
        """
        React to nameko input

        :param exchange: What exchange the message came from
        :type exchange: unicode
        :param routing_key: What routing key was used
        :type routing_key: unicode
        :param msg: The received message
        :type msg: dict
        :return: Accept the input or refuse it
        :rtype: bool
        """
        raise NotImplementedError

    def start(self, blocking=False):
        self._event_listener.start(False)
        self._event_listener_nameko.start(False)
        super(ReactorModule, self).start(blocking)

    def stop(self):
        if not self._is_running:
            # Already stopped
            return
        try:
            self._event_listener.stop()
        except:
            self.exception("Failed to stop event listener")
        try:
            self._event_listener_nameko.stop()
        except:
            self.exception("Failed to stop event listener nameko")
        super(ReactorModule, self).stop()
