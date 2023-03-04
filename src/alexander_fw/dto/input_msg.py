# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.1"
__date__ = "2023-02-26"
# Created: 2017-04-15 16:09

import dataclasses
from typing import Any, Optional

from .basic_msg import BasicMessage


@dataclasses.dataclass
class InputMessage(BasicMessage):
    """ Input message sent by communicator """

    source: Optional[str] = None
    """" Communicator sending this message """
    data: Optional[Any] = None
    """ Data received by communicator (Depends on communicator) """
    metadata: Optional[Any] = dataclasses.field(default=None, repr=False)
    """ Meta information added by communicator (Depends on communicator) """
