# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.0"
__date__ = "2023-06-15"
# Created: 2017-04-26 23:13

import logging.config

import eventlet
# Needs to be patched ASAP
eventlet.monkey_patch()

from alexander_fw.dto import ActorMessage
from alexander_fw.cli import cli_run
from flotils import get_logger
from nameko.rpc import rpc
import seta


logging.captureWarnings(True)
logger = get_logger()


class PingActorService(seta.BaseService):
    """ Simple ping service (return pong) """
    name = "service_actor_ping"
    __version__ = __version__

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

    logging.basicConfig(**seta.cli.prod_formatter_config, level=logging.DEBUG)

    quit(cli_run("PingActorService", __version__, PingActorService, runable=False))
