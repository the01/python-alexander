# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2023, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.0"
__date__ = "2023-03-02"
# Created: 2023-02-26 18:22

from typing import Optional, Type

from flotils import get_logger
import seta

from .dto.utils import MessageDecoder, MessageEncoder


logger = get_logger()


def cli_run(
        prog_name: str,
        version: str,
        service: Type[object],
        config: Optional[dict] = None,
        runable: bool = False,
) -> int:
    """
    Setup and run service cli

    :param prog_name: Name of cli program
    :param version: Version of program
    :param service: Nameko service class to run
    :param config: Optional config to overwrite file config
    :param runable: Is this directly runable or should be run as nameko service
        If true will create instance with ['instance'] config and StartStopable
        interface
    :return: System exit code
    """
    if not config:
        config = {}

    config.setdefault(
        'nameko', {
            'encoder': MessageEncoder,
            'decoder': MessageDecoder,
        }
    )

    return seta.cli.cli_run(prog_name, version, service, config, runable)
