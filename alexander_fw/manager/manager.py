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
# Created: 2017-04-15 14:37

from abc import ABCMeta
import time

from nameko.standalone.rpc import ClusterRpcProxy

from ..reactor.module import ReactorModule
from ..reactor.exceptions import NoProxyException
from ..dto import serialize, deserialize


class Manager(ReactorModule):
    __metaclass__ = ABCMeta

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(Manager, self).__init__(settings)
        nameko_sett = settings['nameko']

        self._cluster_proxy = ClusterRpcProxy(
            nameko_sett, timeout=settings.get('rpc_timeout', None)
        )
        self._proxy = None

    @property
    def proxy(self):
        proxy = self._proxy
        if proxy is None:
            raise NoProxyException("No proxy has been set")
        return proxy

    def say_result(self, msg):
        who = msg.source
        self.emit(msg, self.get_exchange(who))

    # TODO: make who optional
    def say(self, who, msg, result):
        self.debug("Would have sent say - {}: {}\n{}".format(
            who, result, msg
        ))
        actor_msg = serialize(msg)
        actor_msg['__type__'] = "ActorMessage"
        actor_msg = deserialize(actor_msg)
        actor_msg.result = result
        self.debug(self.get_exchange(who))
        self.emit(
            actor_msg,
            self.get_exchange(who)
        )

    # TODO: make who optional
    def say_error(self, who, msg, result):
        self.debug("Would have sent error - {}: {}\n{}".format(
            who, result, msg
        ))
        actor_msg = serialize(msg)
        actor_msg['__type__'] = "ActorMessage"
        actor_msg = deserialize(actor_msg)
        actor_msg.result = result
        self.debug(self.get_exchange(who))
        self.emit(
            actor_msg,
            self.get_exchange(who)
        )

    def start(self, blocking=False):
        tries = 3
        sleep_time = 1.4
        while tries > 0:
            self.debug("Trying to establish nameko proxy..")
            try:
                self._proxy = self._cluster_proxy.start()
            except:
                if tries <= 1:
                    raise
                self.exception("Failed to connect proxy")
                self.info("Sleeping {}s".format(round(sleep_time, 2)))
                time.sleep(sleep_time)
                sleep_time **= 2
            else:
                break
            tries -= 1
        super(Manager, self).start(blocking)

    def stop(self):
        super(Manager, self).stop()
        try:
            self._cluster_proxy.stop()
        except:
            self.exception("Failed to stop cluster proxy")
        finally:
            self._proxy = None
