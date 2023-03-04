# -*- coding: UTF-8 -*-

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2023, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.0"
__date__ = "2023-03-04"
# Created: 2023-03-04 15:33

import logging


logger = logging.getLogger(__name__)


def test_importable():
    import alexander_fw


def test_version():
    import alexander_fw

    logger.debug(alexander_fw.__version__)
