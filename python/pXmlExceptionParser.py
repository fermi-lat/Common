## @package pXmlExceptionParser
## @brief Specific xml parser for the alarm handler exceptions.

import pSafeLogger
logger = pSafeLogger.getLogger('pXmlExceptionParser')

import os
import sys
from xml.dom import minidom

from pAlarmException import pAlarmException


class pXmlExceptionParser:

    def __init__(self, xmlExceptionFilePath):
        self.XmlExceptionFilePath = xmlExceptionFilePath
        if os.path.exists(self.XmlExceptionFilePath):
            logger.info('Parsing %s...' % xmlExceptionFilePath)
            self.XmlDoc = minidom.parse(file(xmlExceptionFilePath))
        else:
            sys.exit('Input exception file %s not found. Exiting...' %\
        	     xmlExceptionFilePath)
        self.ExceptionsDict = {}
        self.__populateExceptionsDict()
        logger.info('Done. %d exceptions found.' % len(self.ExceptionsDict))

    def __populateExceptionsDict(self):
        for element in self.XmlDoc.getElementsByTagName('exception'):
            exception = pAlarmException(element)
            self.ExceptionsDict[(exception.Name, exception.AlgorithmName)] =\
                exception



if __name__ == '__main__':
    parser = pXmlExceptionParser('../xml/fastmon_eor_alarms_exceptions.xml')
    for (key, value) in parser.ExceptionsDict.items():
        print key
        print value
