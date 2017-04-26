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
__date__ = "2017-04-26"
# Created: 2017-04-26 23:13

from nameko.rpc import rpc
from flotils import get_logger

from alexander_fw.dto import ActorMessage


logger = get_logger()


class EchoActorService(object):
    name = "service_actor_ping"

    @rpc
    def status(self):
        return "OK"

    @rpc
    def act(self, message):
        """
        
        :param message:
        :type message: alexander_fw.dto.IntentMessage
        :return: 
        """
        logger.debug(message)
        reply = ActorMessage.from_msg(message)
        if message.data == "ping":
            reply.result = "pong"
        else:
            reply.result = "you are doing it wrong"
        return reply


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
