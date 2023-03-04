# -*- coding: UTF-8 -*-
""" Package describing the actor and intent classes """
__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.0"
__date__ = "2023-03-03"
# Created: 2017-04-17 20:32

from .actor import ActorManager
from .intent import IntentManager
from .manager import Manager

__all__ = ["Manager", "ActorManager", "IntentManager"]
