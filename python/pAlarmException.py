## @package pAlarmException
## @brief Module describing an alarm exception.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmException')

from pXmlElement import pXmlElement



class pAlarmException(pXmlElement):

    def __init__(self, domElement):
        pXmlElement.__init__(self, domElement)
        self.AlgorithmName = self.getAttribute('algorithm')
        self.IdsList = []
        for element in self.getElementsByTagName('identifier'):
            self.IdsList.append(eval(str(element.childNodes[0].data).strip()))
    
    def getTextSummary(self):
        summary =  'Name       : %s\n' % self.Name
        summary += 'Algorithm  : %s\n' % self.AlgorithmName
        summary += 'List of Ids: %s\n' % self.IdsList
        return summary

    def __str__(self):
        return self.getTextSummary()
