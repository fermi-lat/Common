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
        self.AlarmExceptionsDict = {}
        self.__populateAlarmExceptionsDict()
        logger.info('Done. %d exceptions found.' %\
                    len(self.AlarmExceptionsDict))

    def __populateAlarmExceptionsDict(self):
        for element in self.XmlDoc.getElementsByTagName('alarm'):
            exception = pAlarmException(element)
            self.AlarmExceptionsDict[(exception.Name,\
                                      exception.AlgorithmName)] = exception


if __name__ == '__main__':
    filePath = '../../AlarmsCfg/xml/fastmon_eor_alarms_exceptions.xml'
    parser = pXmlExceptionParser(filePath)
    for (key, value) in parser.AlarmExceptionsDict.items():
        print key
        print value
