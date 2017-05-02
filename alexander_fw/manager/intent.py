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
# Created: 2017-04-15 14:46

from .manager import Manager


class IntentManager(Manager):

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(IntentManager, self).__init__(settings)
        self._intents = settings.get("intents", [])
        self.debug("Intents: {}".format(self._intents))

    def _setup(self):
        # Setup listeners
        self._register("manager_intent", "input_new", "IntentManager")

    def react_nameko(self, exchange, routing_key, msg):
        pass

    def react(self, exchange, routing_key, msg):
        self.debug("{}-{}: {}".format(exchange, routing_key, msg))

        if exchange == "manager_intent":
            if routing_key == "input_new":
                self._do_input_new(msg)

    def act(self, intent):
        """
        Tell actor manager to act on intent

        :param intent: Intent to act on
        :type intent: dto.IntentMessage
        :rtype: None
        """
        self.debug(intent)
        self.emit(intent, self.get_exchange("manager_actor"))

    def _do_input_new(self, msg):
        """
        Retrieve intent for input message
        
        :param msg: Input message to react to
        :type msg: dto.InputMessage
        :rtype: None
        """
        likes = []
        """ :type : [unicode] """
        max_like = -1.0
        """ :type : float """

        # Ask all intents who likes it
        for intent in self._intents:
            intent = "service_intent_{}".format(intent)
            try:
                ilike = self.proxy[intent].likes(msg)
                """ :type : float """
            except:
                self.exception(
                    "Failed to get likes from {}:\n{}".format(intent, msg)
                )
                continue

            if ilike > max_like:
                # New like highscore
                likes = [intent]
                max_like = ilike
            elif ilike == max_like:
                # Likes the same
                likes.append(intent)

        # Error if none like it
        if not likes or max_like <= 0:
            self.error("No intent likes:\n{}".format(msg))
            self.say_error(msg.source, msg, "No intent found")
            return

        # Give it to those that like it the most
        intent_msgs = []
        """ :type : [dto.IntentMessage] """
        for intent in likes:
            try:
                intent_msgs.append(self.proxy[intent].intent(msg))
            except:
                self.exception(
                    "Failed to get intent from {}:\n{}".format(intent, msg)
                )
        if not intent_msgs:
            self.error("No intents gathered\n{}".format(msg))
            self.say_error(msg.source, msg, "No intents gathered")
            return
        # Act on intends
        for intent in intent_msgs:
            try:
                self.act(intent)
            except:
                self.exception(
                    "Failed act on intent\n{}".format(msg)
                )
                self.say_error(
                    msg.source, msg, "Failed act on intent\n{}".format(intent)
                )

    def start(self, blocking=False):
        self._setup()
        super(IntentManager, self).start(blocking)
