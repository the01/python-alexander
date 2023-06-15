# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "All rights reserved"
__version__ = "0.2.1"
__date__ = "2023-03-12"
# Created: 2017-04-20 14:09

import logging

import eventlet

from alexander_fw import IntentManager, __version__ as package_version
from alexander_fw.cli import cli_run
from flotils.runable import SignalStopWrapper


logging.captureWarnings(True)
logger = logging.getLogger(__name__)


class WrapperIntentManager(IntentManager, SignalStopWrapper):

    def stop(self):
        """ Stop instance """
        # greenlet does not want blocking calls in mainloop
        # self._is_running = False
        eventlet.spawn_n(super().stop)


if __name__ == "__main__":
    import logging.config
    from flotils.logable import default_logging_config
    
    logging.config.dictConfig(default_logging_config)

    quit(cli_run(
        "IntentManager", package_version, WrapperIntentManager, runable=True
    ))
