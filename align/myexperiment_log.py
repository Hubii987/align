#!/usr/bin/env python3

import logging
from logging import handlers
import sys

logger = logging.getLogger('myexperiment')
logger.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
logger.addHandler(ch)

fh = handlers.RotatingFileHandler('myexperiment.log', maxBytes=(1048576*5), backupCount=7)
fh.setFormatter(format)
logger.addHandler(fh)
