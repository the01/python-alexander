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
__date__ = "2017-04-15"
# Created: 2017-04-15 16:46

from flotils import get_logger
from flotils.loadable import save_json as fsave_json, load_json as fload_json,\
    DateTimeDecoder, DateTimeEncoder
from .basic_msg import BasicMessage
from .intent_msg import IntentMessage
from .input_msg import InputMessage
from .actor_msg import ActorMessage


logger = get_logger()


def serialize(msg):
    """
    Prepare message for serialization

    :param msg: Message to serialize
    :type msg: BasicRequest
    :return: Message as dict
    :rtype: dict
    """
    return msg.to_dict()


def deserialize(d):
    """
    Get class from serialized dict

    :param d: Serialized dict
    :type d: dict
    :return: Class
    :rtype: BasicMessage
    """
    class_name = d['__type__']
    if class_name == "BasicMessage":
        return BasicMessage.from_dict(d)
    elif class_name == "InputMessage":
        return InputMessage.from_dict(d)
    elif class_name == "IntentMessage":
        return IntentMessage.from_dict(d)
    elif class_name == "ActorMessage":
        return ActorMessage.from_dict(d)
    else:
        return None


class MessageEncoder(DateTimeEncoder):
    """
    Encode messages for json
    """

    def default(self, obj):
        if isinstance(obj, BasicMessage):
            return obj.to_dict()
        return super(MessageEncoder, self).default(obj)


class MessageDecoder(DateTimeDecoder):
    """
    Decode messages from json
    """

    @staticmethod
    def _as_message(dct):
        res = None
        if "__type__" in dct:
            try:
                res = deserialize(dct)
            except:
                pass
            if res is not None:
                return res
        raise TypeError("Not BasicMessage")

    @staticmethod
    def decode(dct):
        if isinstance(dct, dict):
            try:
                return MessageDecoder._as_message(dct)
            except:
                pass
        return super(MessageDecoder, MessageDecoder).decode(dct)


def load_json(json_data):
    return fload_json(json_data, MessageDecoder)


def save_json(val, pretty=False, sort=True):
    return fsave_json(val, pretty, sort, encoder=MessageEncoder)


def encode(value):
    return save_json(
        value, pretty=False, sort=False
    )


def decode(value):
    return load_json(value)
