# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.0"
__date__ = "2023-03-03"
# Created: 2017-04-15 14:37

import abc
import time
from typing import Any, Dict, Optional, Union

import nameko.exceptions
import nameko.rpc
from nameko.standalone.rpc import ClusterRpcProxy

from ..dto import ActorMessage, InputMessage
from ..exceptions import NoProxyError
from ..reactor.module import ReactorModule


class Manager(ReactorModule, abc.ABC):
    """ Manager """

    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """ Constructor """
        if settings is None:
            settings = {}

        super().__init__(settings)

        nameko_sett = settings['nameko']
        self._cluster_proxy: ClusterRpcProxy = ClusterRpcProxy(
            nameko_sett,
            timeout=nameko_sett.get('rpc_timeout', None),
        )
        self._proxy: Optional[Any] = None

    def _setup(self) -> None:
        """ Setup this instance - overwrite template for return queues """
        # Extend rpc template to make queue origins clearer
        nameko.rpc.RPC_REPLY_QUEUE_TEMPLATE = \
            f"rpc.reply-{self.class_name()}" + "-{}-{}"

    @property
    def proxy(self) -> Any:
        """
        Get proxy to use

        :raises NoProxyException: No proxy was set
        """
        proxy = self._proxy

        if proxy is None:
            raise NoProxyError("No proxy has been set")

        return proxy

    # TODO: make who optional
    def say(self, who: str, msg: Union[InputMessage, ActorMessage], result: Any) -> None:
        """
        Say something on other device

        :param who: Service to say on
        :param msg: Referenced message to use
        :param result: What to say
        """
        self.debug(f"{who}: {result}\n{msg}")
        actor_msg = ActorMessage.from_msg(msg)
        actor_msg.result = result

        try:
            self.proxy[who].say(actor_msg)
        except nameko.exceptions.RpcTimeout as e:
            # Timeout means it was likely dropped in the queue, but the service did not
            # finish in time - retry or assume it will be handled sometime?
            # Since we are not using result, assume it being delivered is enough
            # Eitherway will be consumed from actor queue
            self.warning(f"Service '{who}' did not respond within {e.args}")

    def say_result(self, msg: ActorMessage) -> None:
        """
        Say result of message

        msg.source is will be called

        :param msg: Message to say
        :raises ValueError: No message source set
        """
        if not msg.source:
            raise ValueError("Expected message source to be set")

        who = msg.source
        self.say(who, msg, msg.result)

    # TODO: make who optional
    def say_error(
            self, who: str, msg: Union[InputMessage, ActorMessage], result: Any
    ) -> None:
        """
        Say the result and log an error

        :param who: Service to say on
        :param msg: Referenced message to use
        :param result: What to say
        """
        self.error(f"Error - {who}: {result}\n{msg}")
        self.say(who, msg, result)

    def start(self, blocking: bool = False):
        """ Start instance """
        tries = 3
        sleep_time = 1.4

        while tries > 0:
            self.debug("Trying to establish nameko proxy..")

            try:
                self._proxy = self._cluster_proxy.start()
            except Exception as e:
                if tries <= 1:
                    raise

                if isinstance(e, ConnectionRefusedError):
                    self.error("Proxy connection refused")
                else:
                    self.exception("Failed to connect proxy")

                self.info("Sleeping {}s".format(round(sleep_time, 2)))
                time.sleep(sleep_time)
                sleep_time **= 2
            else:
                break

            tries -= 1

        super().start(blocking)

    def stop(self):
        """ Stop instance """
        self.debug("()")
        super().stop()

        try:
            self._cluster_proxy.stop()
        except Exception:
            self.exception("Failed to stop cluster proxy")
        finally:
            self._proxy = None
