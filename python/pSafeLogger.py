
LOGGING_LEVEL  = 'DEBUG'
LOGGING_FORMAT = '%(levelname)s:%(name)s -- %(message)s'

import sys

if 'logging' not in sys.modules:
    import logging
    loggingLevel = eval('logging.%s' % LOGGING_LEVEL)
    logging.basicConfig(level = loggingLevel, format = LOGGING_FORMAT)
    logger = logging.getLogger('pSafeLogger')

def getLogger(loggerName):
    return logging.getLogger(loggerName)
