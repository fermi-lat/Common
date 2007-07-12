
DEF_LOGGING_LEVEL  = 'DEBUG'
DEF_LOGGING_FORMAT = '%(levelname)s:%(name)s -- %(message)s'

import sys

def getLogger(loggerName):
    return logging.getLogger(loggerName)

def setLevel(loglevel = DEF_LOGGING_LEVEL):
    try:
        loglevel = eval('logging.%s' % loglevel)
    except:
        loglevel = eval('logging.%s' % DEF_LOGGING_LEVEL)
        logging.error('Could not set the logging level to %s. ' % loglevel +\
                      'Setting it to %s instead...' % DEF_LOGGING_LEVEL)
    logging.basicConfig(level = loglevel, format = DEF_LOGGING_FORMAT)

if 'logging' not in sys.modules:
    import logging
    setLevel()
    logger = logging.getLogger('pSafeLogger')
