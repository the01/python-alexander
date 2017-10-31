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
__date__ = "2017-10-31"
# Created: 2017-10-30 20:55

from nameko.rpc import rpc, RpcProxy
from flotils import get_logger



logger = get_logger()


class LockKeywordIntentService(object):
    name = "service_intent_keyword_lock"
    keyword = RpcProxy("service_intent_keyword")
    keystore = RpcProxy("service_keystore")

    @rpc
    def status(self):
        return "OK"

    def _split(self, data):
        if not data:
            return False, data
        parts = data.split(" ")
        if len(parts) >= 2 and parts[0] == "lock":
            return True, " ".join(parts[1:])
        return False, data

    @rpc
    def likes(self, message):
        """
        How much do I like this message

        :param message: Message to asses
        :type message: alexander_fw.dto.InputMessage
        :return: Value between 0 and 1
        :rtype: float
        """
        user = None
        meta = message.metadata
        if meta and isinstance(meta, dict):
            user = meta.get('user', {}).get('id')
        lock_cmd, rest = self._split(message.data)
        intent = self.keystore.get("{}.{}".format(self.name, user), None)
        if intent:
            return 1.0
        if lock_cmd == "lock":
            return self.keyword.likes(rest) + 0.001
        return 0.0

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
        user = None
        meta = message.metadata
        if meta and isinstance(meta, dict):
            user = meta.get('user', {}).get('id')
        lock_cmd, rest = self._split(message.data)
        key = "{}.{}".format(self.name, user)
        intent = self.keystore.get(key, None)
        if intent:
            return self.keyword.intent(intent)
        self.keystore.set(key, intent)
        return self.keyword.intent(rest)

    @rpc
    def lock(self, key, intent):
        self.keystore.set("{}.{}".format(self.name, key), intent)


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
