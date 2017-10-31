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
__date__ = "2017-08-10"
# Created: 2017-08-10 10:29

from kombu.serialization import register

from .dto.utils import encode, decode


def setup_kombu():
    register(
        "datetimejson", encode, decode, "application/datetime-json", "utf-8"
    )
