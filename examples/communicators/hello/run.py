# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.3"
__date__ = "2023-02-26"
# Created: 2017-04-15 17:59

import logging.config

import eventlet
# Needs to be patched ASAP
eventlet.monkey_patch()

from alexander_fw.dto import InputMessage
from alexander_fw.cli import cli_run
from alexander_fw.service import CommunicatorService
import nameko.rpc
from nameko.timer import timer
from flotils import get_logger


logging.captureWarnings(True)
logger = get_logger()


class HelloCommunicator(CommunicatorService):
    name = "service_communicator_hello"

    def do_say(self, msg):
        from pprint import pformat

        logger.info("Got:\n{}".format(pformat(msg.to_dict())))

    @timer(interval=5)
    def _emit(self):
        msg = InputMessage(
            data="ping"
        )
        self.communicate(msg)


if __name__ == "__main__":
    from flotils.logable import default_logging_config

    logging.config.dictConfig(default_logging_config)
    logging.getLogger().setLevel(logging.DEBUG)
    nameko.rpc.RPC_REPLY_QUEUE_TEMPLATE = \
        "rpc.reply-HelloCommunicator-{}-{}"

    quit(cli_run("HelloCommunicator", __version__, HelloCommunicator))
