# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.1"
__date__ = "2017-04-21"
# Created: 2017-04-15 17:50

from nameko.rpc import rpc
from flotils import get_logger

from alexander_fw.dto import serialize, deserialize


logger = get_logger()


class DirectIntentService(object):
    name = "service_intent_direct"

    @rpc
    def status(self):
        return "OK"

    @rpc
    def likes(self, message):
        """
        How much do I like this message

        :param message: Message to asses
        :type message: alexander_fw.dto.InputMessage
        :return: Value between 0 and 1
        :rtype: float
        """
        # Like everything from hello
        res = 1.0 if message.source == "communicator_hello" else 0.0
        logger.debug("{}: {}".format(message, res))
        return res

    @rpc
    def intent(self, message):
        """
        Get intent for message

        :param message: Message to asses
        :type message: alexander_fw.dto.InputMessage
        :return: Message intent
        :rtype: alexander_fw.dto.IntentMessage
        """
        logger.debug(message.to_dict())
        res = serialize(message)
        res['__type__'] = "IntentMessage"
        res = deserialize(res)
        res.intent = "echo"
        return res


if __name__ == "__main__":
    import logging.config
    import os
    import sys

    from flotils.logable import default_logging_config
    from nameko.cli.main import main
    from alexander_fw import setup_kombu

    logging.config.dictConfig(default_logging_config)
    logging.getLogger().setLevel(logging.DEBUG)
    logger = logging.getLogger(__name__)

    setup_kombu()

    pid = os.getpid()
    logger.info(u"Detected pid {}".format(pid))
    logger.info(u"Using virtualenv {}".format(hasattr(sys, 'real_prefix')))
    logger.info(u"Using supervisor {}".format(
        bool(os.getenv('SUPERVISOR_ENABLED', False)))
    )

    main()
