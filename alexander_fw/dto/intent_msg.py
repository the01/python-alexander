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
# Created: 2017-04-15 16:18

from .input_msg import InputMessage


class IntentMessage(InputMessage):
    """
    Intent message sent by Intent after processing InputMessage
    """

    def __init__(self,
            uuid=None, timestamp=None,
            source=None, data=None, metadata=None,
            intent=None, metaintent=None
    ):
        super(IntentMessage, self).__init__(
            uuid, timestamp,
            source, data, metadata
        )
        self.intent = intent
        """ Extracted intent
            :type : object """
        self.metaintent = metaintent
        """ Meta information about extracted intent
            :type : object """
