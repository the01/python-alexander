# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-23, Florian JUNG"
__license__ = "MIT"
__version__ = "0.2.0"
__date__ = "2023-03-03"
# Created: 2017-02-19 22:51


class AlexanderError(Exception):
    """ Base exception for package """


class ReactorError(AlexanderError):
    """ Base exception for reactor """


class NoProxyError(ReactorError):
    """ No proxy available """
