# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.1"
__date__ = "2023-03-03"
# Created: 2017-04-15 16:02

import dataclasses
import datetime
from typing import Any, Dict, Union
import uuid as uuid_lib

from typing_extensions import Self


@dataclasses.dataclass
class BasicMessage:
    """ Basic message object """

    uuid: str = dataclasses.field(default_factory=lambda: f"{uuid_lib.uuid4()}")
    """ Message uuid (uuid4) """
    timestamp: datetime.datetime = dataclasses.field(
        default_factory=datetime.datetime.utcnow
    )
    """ Time in utc (Serialized in ISO 8601) """

    @classmethod
    def from_dict(cls, kwargs: Dict) -> Self:
        """ New instance form dict """
        if "__type__" in kwargs:
            del kwargs['__type__']

        return cls(**kwargs)

    @classmethod
    def from_msg(cls, msg: Union["BasicMessage", Self]) -> Self:
        """
        Create instance from other message

        :param msg: Message to create instance from
        :type msg: BasicMessage
        :return: New instance
        """
        return cls.from_dict(msg.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """ Transform instance to dict """
        res = self.__dict__
        res['__type__'] = self.__class__.__name__

        return res
