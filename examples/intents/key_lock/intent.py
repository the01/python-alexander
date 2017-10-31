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
from alexander_fw.dto import IntentMessage


logger = get_logger()


# TODO: (un)lock actor
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
        if len(parts) >= 2 and parts[0] == "/lock":
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
        logger.debug(message.to_dict())
        user = None
        meta = message.metadata
        if meta and isinstance(meta, dict):
            user = meta.get('mapped_user', meta.get('user', {}).get('id'))
        lock_cmd, rest = self._split(message.data)
        intent = self.keystore.get("{}.{}".format(self.name, user), None)
        logger.debug("\nuser: {}\nlock_cmd: {}\nrest: {}\nintent: {}".format(
            user, lock_cmd, rest, intent
        ))
        if intent:
            return 1.0
        if lock_cmd:
            message.data = rest
            like = self.keyword.likes(message) + 0.001
            logger.debug("like: {}".format(like))
            return like
        logger.debug("none")
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
            user = meta.get('mapped_user', meta.get('user', {}).get('id'))
        lock_cmd, rest = self._split(message.data)
        intent = self.is_locked(user)
        logger.debug("stored intent: {}".format(intent))
        if intent:
            if message.data == "/unlock":
                self.unlock(user)
                res = IntentMessage.from_msg(message)
                res.intent = "ok"
                return res
            message.data = "{} {}".format(intent, message.data)
            return self.keyword.intent(message)
        if lock_cmd:
            message.data = rest
        intent_msg = self.keyword.intent(message)
        self.lock(user, intent_msg.intent)
        logger.debug("keyword intent: {}".format(intent_msg.intent))
        return intent_msg

    @rpc
    def lock(self, key, intent):
        self.keystore.set("{}.{}".format(self.name, key), intent)
        logger.debug("{}: {}".format(key, intent))

    @rpc
    def is_locked(self, key):
        return self.keystore.get("{}.{}".format(self.name, key))

    @rpc
    def unlock(self, key):
        self.keystore.delete("{}.{}".format(self.name, key))
        logger.debug(key)


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
