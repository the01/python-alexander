# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.1"
__date__ = "2023-03-13"
# Created: 2017-04-15 17:50

from typing import Any, Dict, List, Optional, Tuple

import eventlet

# Needs to be patched ASAP
eventlet.monkey_patch()

from flotils import get_logger, Loadable, StartStopable
from nameko.rpc import rpc
import nameko.messaging
import seta

from alexander_fw.dto import IntentMessage, InputMessage
from alexander_fw.cli import cli_run


logger = get_logger()
connection_errors = 0


def patch_queue_consumer():
    from nameko.rpc import RpcConsumer, ReplyListener
    from nameko.messaging import Consumer

    RpcConsumer.queue_consumer = PatchedQueueConsumer()
    ReplyListener.queue_consumer = PatchedQueueConsumer()
    Consumer.queue_consumer = PatchedQueueConsumer()


class PatchedQueueConsumer(nameko.messaging.QueueConsumer):

    is_patched = True

    def on_connection_error(self, exc, interval):
        global connection_errors

        connection_errors += 1

        if connection_errors > 10:
            logger.error("Too many connection errors, exiting")

            raise SystemExit(1)

        super().on_connection_error(exc, interval)

    def on_consume_ready(self, connection, channel, consumers, **kwargs):
        global connection_errors

        connection_errors = 0

        return super().on_consume_ready(connection, channel, consumers, **kwargs)


class KeywordIntent(Loadable, StartStopable):
    # TODO: Type argument - regex match group

    def __init__(self, settings=None):
        if settings is None:
            settings = {}

        super(KeywordIntent, self).__init__(settings)
        self._map: List[Dict[str, str]] = settings['map']

    def _verify_map(self, map: List[Dict[str, str]]) -> None:
        """
        Verify that map has valid structure

        :param map: Map to test
        """
        for entry in map:
            if not isinstance(entry, dict):
                raise TypeError("Map entry needs to be dict")
            if "key" not in entry:
                raise ValueError("Missing key argument")
            if "intent" not in entry:
                raise ValueError("Missing intent argument")

    def match_all(self, line: str) -> List[Tuple[str, str, float]]:
        """
        Find all matching intents

        :param line: Line to match
        :return: All matches as tuple of intent, meta-intent,
                 information about best match
        """
        matches = []

        if not line:
            return matches

        for entry in self._map:
            key = entry['key']

            if line.startswith(key):
                meta = line[len(key):]
                matches.append((entry['intent'], meta, len(key)))

        return matches

    def match(self, line: str) -> Optional[Tuple[str, str, float]]:
        """
        Find best match

        :param line: Line to match
        :return: Match as tuple of intent, meta-intent,
                 information about best match or None if nothing found
        """
        matches = self.match_all(line)
        res = None

        for match in matches:
            if res is None or res[2] < match[2]:
                res = match

        return res

    def start(self, blocking: bool = False):
        self._verify_map(self._map)


class KeywordDependency(seta.BaseDependency):

    def setup(self):
        super().setup()
        self.instance = KeywordIntent(self.instance_config)


class KeywordIntentService(seta.BaseService):
    name = "service_intent_keyword"
    __version__ = __version__
    keyword: KeywordIntent = KeywordDependency()

    @rpc
    def likes(self, message: InputMessage) -> float:
        """
        How much do I like this message

        :param message: Message to asses
        :return: Value between 0 and 1
        """
        match = self.keyword.match(message.data)
        res = 0.8 if match is not None else 0.0
        logger.debug(f"{message}: {res}")

        return res

    @rpc
    def intent(self, message: InputMessage) -> IntentMessage:
        """
        Get intent for message

        :param message: Message to assess
        :return: Message intent
        """
        logger.debug(message)
        match = self.keyword.match(message.data)
        res = IntentMessage.from_msg(message)

        if match is None:
            logger.error("Should have never been chosen")

            raise ValueError("Unsupported match")

        res.intent = match[0]

        if match[1]:
            res.metaintent = match[1]

        return res


if __name__ == "__main__":
    import logging.config

    logging.basicConfig(**seta.cli.prod_formatter_config, level=logging.DEBUG)
    patch_queue_consumer()

    quit(cli_run(
        "KeywordIntentService", __version__, KeywordIntentService, runable=False
    ))
