# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.0"
__date__ = "2023-03-03"
# Created: 2017-04-15 16:46

import logging
from typing import Any, Dict, Optional

from seta import Decoder, Encoder

from .actor_msg import ActorMessage
from .basic_msg import BasicMessage
from .input_msg import InputMessage
from .intent_msg import IntentMessage


logger = logging.getLogger(__name__)


def serialize(msg: BasicMessage) -> Dict:
    """
    Prepare message for serialization

    :param msg: Message to serialize
    :return: Message as dict
    """
    return msg.to_dict()


def deserialize(d: Dict) -> Optional[BasicMessage]:
    """
    Get class from serialized dict

    :param d: Serialized dict
    :return: Class or None if not loadable
    """
    class_name = d.pop('__type__')

    if class_name == "BasicMessage":
        return BasicMessage.from_dict(d)
    elif class_name == "InputMessage":
        return InputMessage.from_dict(d)
    elif class_name == "IntentMessage":
        return IntentMessage.from_dict(d)
    elif class_name == "ActorMessage":
        return ActorMessage.from_dict(d)
    else:
        d['__type__'] = class_name

        return None


class MessageEncoder(Encoder):
    """ Encode messages for json """

    def default(self, obj: Any) -> Any:
        """ Handle serialization """
        if isinstance(obj, BasicMessage):
            return obj.to_dict()

        return super().default(obj)


class MessageDecoder(Decoder):
    """ Decode messages from json """

    @staticmethod
    def _as_message(dct: Dict) -> BasicMessage:
        """
        Handle deserialization of dict

        :param dct: Dict to deserialize
        :returns: The instantiated class
        :raises TypeError: Not a BasicMessage
        """
        res = None

        if "__type__" in dct:
            try:
                res = deserialize(dct)
            except Exception:  # nosec: B110
                pass

            if res is not None:
                return res

        raise TypeError("Not BasicMessage")

    @staticmethod
    def decode(data: Any) -> Any:
        """ Deserialize dct """
        if not isinstance(data, dict):
            return super(MessageDecoder, MessageDecoder).decode(data)

        res = None

        if "__type__" in data:
            try:
                res = deserialize(data)
            except Exception:  # nosec: B110
                pass

            if res is not None:
                return res

        return super(MessageDecoder, MessageDecoder).decode(data)
