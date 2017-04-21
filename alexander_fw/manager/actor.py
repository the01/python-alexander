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
__date__ = "2017-04-15"
# Created: 2017-04-15 16:59

from .manager import Manager


class ActorManager(Manager):

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(ActorManager, self).__init__(settings)
        self._actors = settings.get("actors", [])

    def _setup(self):
        # Setup listeners
        self._register("manager_actor", "intent_new", "ActorManager")

    def react(self, exchange, routing_key, msg):
        self.debug("{}-{}: {}".format(exchange, routing_key, msg))

        if exchange == "manager_actor":
            if routing_key == "intent_new":
                self._do_act(msg)

    def react_nameko(self, exchange, routing_key, msg):
        pass

    def _do_act(self, msg):
        """
        React to message
        
        :param msg: Received message
        :type msg: dto.IntentMessage
        :rtype: None
        """
        if not isinstance(msg.intent, list):
            msg.intent = [msg.intent]
        match_actors = 0
        for actor in self._actors:
            if actor not in msg.intent:
                # Not matched
                continue
            match_actors += 1
            actor_service = "service_actor_{}".format(actor)
            try:
                resp = self.proxy[actor_service].act(msg)
                """ :type : None | object """
            except:
                self.exception(
                    "Failed to act {}:\n{}".format(
                        actor_service, msg
                    )
                )
                self.say_error(
                    msg.source, msg, "Failed {} to act".format(actor_service)
                )
            else:
                self.debug("{} returned: {}".format(actor_service, resp))
                if resp is not None:
                    self.say_result(resp)

    def start(self, blocking=False):
        self._setup()
        super(ActorManager, self).start(blocking)
