# -*- coding: UTF-8 -*-
""" Framework implementing a chatbot like system """

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__date__ = "2023-03-02"
# Created: 2017-04-17 20:26

from . import dto  # noqa: F401
from . import manager  # noqa: F401
from . import reactor  # noqa: F401
from .__version__ import __version__  # noqa: F401
from .manager import ActorManager, IntentManager  # noqa: F401
from .reactor import EventListener, ReactorModule, RPCListener  # noqa: F401
from .service import CommunicatorService, StandaloneCommunicatorService  # noqa: F401


__all_ = [
    "__version__",
    "dto",
    "IntentManager", "ActorManager",
    "CommunicatorService", "StandaloneCommunicatorService",
    "RPCListener", "ReactorModule", "EventListener",
]
