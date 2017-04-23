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

from flotils.runable import SignalStopWrapper

from alexander_fw.reactor import ReactorModule
from alexander_fw.dto import InputMessage


class TickerCommunicator(ReactorModule):

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(TickerCommunicator, self).__init__(settings)

    def _setup(self):
        # Setup listeners
        self._register("communicator_ticker", "say", "TickerCommunicator")

    def communicate(self, msg):
        msg.source = "communicator_ticker"
        self.emit(msg, self.get_exchange("manager_intent"))

    def react_nameko(self, exchange, routing_key, msg):
        pass

    def react(self, exchange, routing_key, msg):
        self.debug("{}-{}: {}".format(exchange, routing_key, msg))

        if exchange == "communicator_ticker":
            if routing_key == "say":
                from pprint import pformat
                self.info("Got:\n{}".format(pformat(msg.to_dict())))

    def start(self, blocking=False):
        self._setup()
        super(TickerCommunicator, self).start()

    def stop(self):
        super(TickerCommunicator, self).stop()


class Wrapper(TickerCommunicator, SignalStopWrapper):

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(Wrapper, self).__init__(settings)


if __name__ == "__main__":
    import argparse
    import time
    import logging.config
    from flotils.logable import default_logging_config
    from alexander_fw import setup_kombu

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", action="store_true",
        help="Use debug level output"
    )
    parser.add_argument(
        "--config", nargs="?",
        help="Config file"
    )
    logging.config.dictConfig(default_logging_config)
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    setup_kombu()

    instance = Wrapper({
        'settings_file': args.config
    })

    try:
        instance.start(False)
        while True:
            instance.communicate(InputMessage(
                data="time now"
            ))
            time.sleep(20.0)
    except KeyboardInterrupt:
        pass
    finally:
        instance.stop()
