# -*- coding: UTF-8 -*-
""" Run actor manager """

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "All rights reserved"
__version__ = "0.2.0"
__date__ = "2023-03-12"
# Created: 2017-04-20 03:33

import logging

# import eventlet
# # Needs to be patched ASAP
# eventlet.monkey_patch()
from flotils.runable import SignalStopWrapper

from alexander_fw import __version__ as package_version, ActorManager
from alexander_fw.cli import cli_run


logging.captureWarnings(True)
logger = logging.getLogger(__name__)


class WrapperActorManager(ActorManager, SignalStopWrapper):
    """ Main class """

    def stop(self):
        """ Stop instance """
        # greenlet does not want blocking calls in mainloop
        # self._is_running = False
        # eventlet.spawn_n(super().stop)
        super().stop()


if __name__ == "__main__":
    import logging.config
    from flotils.logable import default_logging_config

    logging.config.dictConfig(default_logging_config)

    quit(cli_run(
        "ActorManager", package_version, WrapperActorManager, runable=True
    ))
