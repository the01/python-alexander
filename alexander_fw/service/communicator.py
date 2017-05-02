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
__date__ = "2017-05-02"
# Created: 2017-05-01 23:55

from abc import ABCMeta, abstractmethod

from nameko.rpc import rpc
from flotils import get_logger

from .dispatcher import EventDispatcher


logger = get_logger()


class CommunicatorService(object):
    __metaclass__ = ABCMeta

    name = "service_communicator"
    dispatch_intent = EventDispatcher()

    def communicate(self, msg):
        msg.source = self.name
        logger.debug(msg.to_dict())
        self.dispatch_intent("input_new", msg)

    @rpc
    def status(self):
        return "ok"

    @rpc
    def say(self, msg):
        return self.do_say(msg)

    @abstractmethod
    def do_say(self, msg):
        raise NotImplementedError()
