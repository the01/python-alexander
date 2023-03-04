# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.1"
__date__ = "2023-03-03"
# Created: 2017-04-15 16:18

import dataclasses
from typing import Any, Optional

from .input_msg import InputMessage


@dataclasses.dataclass
class IntentMessage(InputMessage):
    """ Intent message sent by Intent after processing InputMessage """

    intent: Optional[Any] = None
    """ Extracted intent """
    metaintent: Optional[Any] = dataclasses.field(default=None, repr=False)
    """ Meta information about extracted intent """
