# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.1"
__date__ = "2023-02-26"
# Created: 2017-04-15 21:20

import dataclasses
from typing import Any, Optional

from .intent_msg import IntentMessage


@dataclasses.dataclass
class ActorMessage(IntentMessage):
    """ Actor message sent by Actor after processing IntentMessage """

    result: Optional[Any] = None
    """ Actor result """
