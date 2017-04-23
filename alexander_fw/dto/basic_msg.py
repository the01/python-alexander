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
__date__ = "2017-04-23"
# Created: 2017-04-15 16:02

import uuid as uuid_lib
import datetime


class BasicMessage(object):
    """
    Basic message object
    """

    def __init__(self, uuid=None, timestamp=None):
        self.uuid = uuid
        """ Message uuid (uuid4)
            :type : unicode """
        self.timestamp = timestamp
        """ Time in utc (Serialized in ISO 8601)
            :type : datetime.datetime """
        if self.uuid is None:
            self.uuid = "{}".format(uuid_lib.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.datetime.utcnow()

    @classmethod
    def from_dict(cls, kwargs):
        if "__type__" in kwargs:
            del kwargs['__type__']
        return cls(**kwargs)

    @classmethod
    def from_msg(cls, msg):
        """
        Creat instance from other message

        :param msg: Message to create instance from
        :type msg: BasicMessage
        :return: New instance
        """
        return cls.from_dict(msg.to_dict())

    def to_dict(self):
        res = self.__dict__
        res['__type__'] = self.__class__.__name__
        return res
