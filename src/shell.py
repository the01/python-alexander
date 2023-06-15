# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2022, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.0"
__date__ = "2022-11-16"
# Created: 2022-11-16 03:03

from argparse import Namespace
import os

from nameko.cli.shell import main
from seta import setup_kombu

setup_kombu(
    serializer="datetimejson",
    serializer_type="application/json",
)
args = Namespace(
    config=None,
    broker=os.environ['SETA_BROKER_URI'],
    interface="ipython",
)
main(args)
