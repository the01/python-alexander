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
# Created: 2017-04-15 16:09

from .basic_msg import BasicMessage


class InputMessage(BasicMessage):
    """
    Input message sent by communicator
    """

    def __init__(self,
            uuid=None, timestamp=None,
            source=None, data=None, metadata=None
    ):
        super(InputMessage, self).__init__(uuid, timestamp)
        self.source = source
        """ Communicator sending this message
            :type : unicode """
        self.data = data
        """ Data received by communicator (Depends on communicator)
            :type : object """
        self.metadata = metadata
        """ Meta information added by communicator (Depends on communicator)
            :type : object """
