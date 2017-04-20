# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017, Florian JUNG"
__license__ = "All rights reserved"
__version__ = "0.1.0"
__date__ = "2017-04-20"
# Created: 2017-04-20 03:33

from alexander_fw import ActorManager
from flotils.runable import SignalStopWrapper


class Wrapper(ActorManager, SignalStopWrapper):

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(Wrapper, self).__init__(settings)


if __name__ == "__main__":
    import argparse
    import logging
    import logging.config
    from flotils.logable import default_logging_config
    from alexander_fw import setup_kombu
    
    logging.config.dictConfig(default_logging_config)
    logging.getLogger().setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", action="store_true",
        help="Use debug level output"
    )
    parser.add_argument(
        "--config", nargs="?", default="settings.yaml",
        help="Config file"
    )
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    setup_kombu()
    
    instance = Wrapper({
        'settings_file': args.config
    })
    
    try:
        instance.start(True)
    except KeyboardInterrupt:
        pass
    finally:
        instance.stop()
