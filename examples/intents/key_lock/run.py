# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.0"
__date__ = "2023-02-27"
# Created: 2017-10-30 20:55

from typing import Tuple

from alexander_fw.dto import IntentMessage, InputMessage
from alexander_fw.service import KeystoreService
from alexander_fw.cli import cli_run
from flotils import get_logger
from nameko.rpc import rpc, RpcProxy
import seta


logger = get_logger()


# TODO: (un)lock actor
class LockKeywordIntentService(seta.BaseService):
    name = "service_intent_keyword_lock"
    __version__ = __version__
    keyword = RpcProxy("service_intent_keyword")
    keystore: KeystoreService = RpcProxy("service_keystore")

    def _split(self, data: str) -> Tuple[bool, str]:
        if not data:
            return False, data

        parts = data.split(" ")

        if len(parts) >= 2 and parts[0] == "/lock":
            return True, " ".join(parts[1:])

        return False, data

    @rpc
    def likes(self, message: InputMessage) -> float:
        """
        How much do I like this message

        :param message: Message to assess
        :return: Value between 0 and 1
        """
        logger.debug(message)
        user = None
        meta = message.metadata

        if meta and isinstance(meta, dict):
            user = meta.get('mapped_user', meta.get('user', {}).get('id'))

        lock_cmd, rest = self._split(message.data)
        intent = self.keystore.get(f"{self.name}.{user}", None)
        logger.debug(
            f"\nuser: {user}\n"
            f"lock_cmd: {lock_cmd}\n"
            f"rest: {rest}\n"
            f"intent: {intent}"
        )

        if intent:
            return 1.0

        if lock_cmd:
            message.data = rest
            like = self.keyword.likes(message) + 0.001
            logger.debug(f"like: {like}")

            return like

        logger.debug("none")

        return 0.0

    @rpc
    def intent(self, message: InputMessage) -> IntentMessage:
        """
        Get intent for message

        :param message: Message to assess
        :return: Message intent
        """
        logger.debug(message)
        user = None
        meta = message.metadata

        if meta and isinstance(meta, dict):
            user = meta.get('mapped_user', meta.get('user', {}).get('id'))

        lock_cmd, rest = self._split(message.data)
        intent = self.is_locked(user)
        logger.debug(f"stored intent: {intent}")

        if intent:
            if message.data == "/unlock":
                self.unlock(user)
                res = IntentMessage.from_msg(message)
                res.intent = "ok"

                return res

            if message.data is not None:
                message.data = f"{intent} {message.data}"
            else:
                message.data = f"{intent}"

            return self.keyword.intent(message)

        if lock_cmd:
            message.data = rest

        intent_msg = self.keyword.intent(message)
        self.lock(user, intent_msg.intent)
        logger.debug(f"keyword intent: {intent_msg.intent}")

        return intent_msg

    @rpc
    def lock(self, key, intent):
        self.keystore.set(f"{self.name}.{key}", intent)
        logger.debug(f"{key}: {intent}")

    @rpc
    def is_locked(self, key):
        return self.keystore.get(f"{self.name}.{key}")

    @rpc
    def unlock(self, key):
        self.keystore.delete(f"{self.name}.{key}")
        logger.debug(key)


if __name__ == "__main__":
    import logging.config

    logging.basicConfig(**seta.cli.prod_formatter_config, level=logging.DEBUG)

    quit(cli_run("LockKeywordIntentService", __version__, LockKeywordIntentService))
