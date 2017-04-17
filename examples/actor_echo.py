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
# Created: 2017-04-15 17:23

from nameko.rpc import rpc
from flotils import get_logger

from alexander.dto import ActorMessage, serialize


logger = get_logger()


class EchoActorService(object):
    name = "service_actor_echo"

    @rpc
    def status(self):
        return "OK"

    @rpc
    def act(self, message):
        logger.debug(message)
        reply = ActorMessage.from_dict(serialize(message))
        reply.result = message.data
        return reply


if __name__ == "__main__":
    import logging.config
    import os
    import sys

    from flotils.logable import default_logging_config
    from nameko.cli.main import main
    from kombu.serialization import register
    from alexander.dto import encode, decode

    logging.config.dictConfig(default_logging_config)
    logging.getLogger().setLevel(logging.DEBUG)
    logger = logging.getLogger(__name__)

    register(
        "datetimejson",
        encode, decode,
        "application/datetime-json", "utf-8"
    )

    pid = os.getpid()
    logger.info(u"Detected pid {}".format(pid))
    logger.info(u"Using virtualenv {}".format(hasattr(sys, 'real_prefix')))
    logger.info(u"Using supervisor {}".format(
        bool(os.getenv('SUPERVISOR_ENABLED', False)))
    )

    main()
