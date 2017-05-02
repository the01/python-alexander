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
__date__ = "2017-04-20"
# Created: 2017-04-15 17:59

from alexander_fw.dto import InputMessage
from alexander_fw.service import CommunicatorService
from nameko.timer import timer
from flotils import get_logger


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
    import os
    import sys
    import logging.config
    from flotils.logable import default_logging_config
    from alexander_fw import setup_kombu
    from nameko.cli.main import main

    logging.config.dictConfig(default_logging_config)

    pid = os.getpid()
    logger.info(u"Detected pid {}".format(pid))
    logger.info(u"Using virtualenv {}".format(hasattr(sys, 'real_prefix')))
    logger.info(u"Using supervisor {}".format(
        bool(os.getenv('SUPERVISOR_ENABLED', False)))
    )

    setup_kombu()
    main()
