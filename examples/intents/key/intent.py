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
__date__ = "2017-04-21"
# Created: 2017-04-15 17:50

from nameko.rpc import rpc
from nameko.extensions import DependencyProvider
from flotils import get_logger, Loadable, StartStopable

from alexander_fw.dto import IntentMessage


logger = get_logger()


class KeywordIntent(Loadable, StartStopable):
    # TODO: Type argument - regex match group

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(KeywordIntent, self).__init__(settings)
        self._map = settings['map']
        """ :type : list[dict[unicode, unicode]] """

    def _verify_map(self, map):
        """
        Verify that map has valid structure

        :param map: Map to test
        :type map: list[dict[unicode, unicode]]
        :rtype: None
        """
        for entry in self._map:
            if not isinstance(entry, dict):
                raise TypeError("Map entry needs to be object")
            if "key" not in entry:
                raise ValueError("Missing key argument")
            if "intent" not in entry:
                raise ValueError("Missing intent argument")

    def match_all(self, line):
        """
        Find all matching intents

        :param line: Line to match
        :type line: unicode
        :return: All matches as tuple of intent, meta-intent,
                 information about best match
        :rtype: list[(unicode, unicode, float)]
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

    def match(self, line):
        """
        Find best match

        :param line: Line to match
        :type line: unicode
        :return: Match as tuple of intent, meta-intent,
                 information about best match or None if nothing found
        :rtype: (unicode, unicode, float) | None
        """
        matches = self.match_all(line)
        res = None
        for match in matches:
            if res is None:
                res = match
            elif res[2] < match[2]:
                res = match
        return res

    def start(self, blocking=False):
        self._verify_map(self._map)


class KeywordDependency(DependencyProvider):

    def setup(self):
        settings = self.container.config['intent']
        self.instance = KeywordIntent(settings)
        super(KeywordDependency, self).setup()

    def start(self):
        logger.debug("Dependency starting..")
        self.instance.start(False)
        super(KeywordDependency, self).start()

    def stop(self):
        self.instance.stop()
        super(KeywordDependency, self).stop()

    def get_dependency(self, worker_ctx):
        return self.instance


class KeywordIntentService(object):
    name = "service_intent_keyword"
    keyword = KeywordDependency()
    """ :type : KeywordIntent """

    @rpc
    def status(self):
        return "OK"

    @rpc
    def likes(self, message):
        """
        How much do I like this message

        :param message: Message to asses
        :type message: alexander_fw.dto.InputMessage
        :return: Value between 0 and 1
        :rtype: float
        """
        match = self.keyword.match(message.data)
        res = 0.8 if match is not None else 0.0
        logger.debug("{}: {}".format(message, res))
        return res

    @rpc
    def intent(self, message):
        """
        Get intent for message

        :param message: Message to asses
        :type message: alexander_fw.dto.InputMessage
        :return: Message intent
        :rtype: alexander_fw.dto.IntentMessage
        """
        logger.debug(message.to_dict())
        match = self.keyword.match(message.data)
        res = IntentMessage.from_msg(message)
        if match is None:
            logger.error("Should have never been chosen")
            raise Exception("Unsupported match")
        res.intent = match[0]
        if match[1]:
            res.metaintent = match[1]
        return res


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
