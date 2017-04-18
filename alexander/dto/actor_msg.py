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
# Created: 2017-04-15 21:20

from .intent_msg import IntentMessage

class ActorMessage(IntentMessage):
    """
    Actor message sent by Actor after processing IntentMessage
    """

    def __init__(self,
            uuid=None, timestamp=None,
            source=None, data=None, metadata=None,
            intent=None, metaintent=None,
            result=None
    ):
        super(ActorMessage, self).__init__(
            uuid, timestamp,
            source, data, metadata,
            intent, metaintent
        )
        self.result = result
        """ Actor result
            :type : object """
