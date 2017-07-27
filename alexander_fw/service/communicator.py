# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.0"
__date__ = "2017-07-27"
# Created: 2017-05-01 23:55

from abc import ABCMeta, abstractmethod

from nameko.rpc import rpc
from flotils import get_logger

from .dispatcher import EventDispatcher


logger = get_logger()


class StandaloneCommunicatorService(object):
    __metaclass__ = ABCMeta

    name = "service_communicator"
    allowed = ["status", "say"]
    dispatch_intent = None
    """ :type : (unicode, alexander_fw.dto.InputMessage) -> None """

    def communicate(self, msg):
        """
        Communicate incoming message to intent manager

        :param msg: New input
        :type msg: alexander_fw.dto.InputMessage
        :rtype: None
        """
        msg.source = self.name
        logger.debug(msg.to_dict())
        self.dispatch_intent("input_new", msg)

    def status(self):
        """
        Service status

        :return: Status
        :rtype: unicode
        """
        return "ok"

    def say(self, msg):
        """
        Send a message through this communicator

        :param msg: Message to send
        :type msg: alexander_fw.dto.ActorMessage
        :return: Result
        :rtype: object
        """
        return self.do_say(msg)

    @abstractmethod
    def do_say(self, msg):
        """
        Do the actual sending

        :param msg: Message to send
        :type msg: alexander_fw.dto.ActorMessage
        :return: Result
        :rtype: object
        """
        raise NotImplementedError()


class CommunicatorService(StandaloneCommunicatorService):
    __metaclass__ = ABCMeta

    dispatch_intent = EventDispatcher()

    @rpc
    def status(self):
        """
        Service status

        :return: Status
        :rtype: unicode
        """
        super(CommunicatorService, self).status()

    @rpc
    def say(self, msg):
        """
        Send a message through this communicator

        :param msg: Message to send
        :type msg: alexander_fw.dto.ActorMessage
        :return: Result
        :rtype: object
        """
        return super(CommunicatorService, self).say(msg)
