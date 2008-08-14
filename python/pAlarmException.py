## @package pAlarmException
## @brief Module describing an alarm exception.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmException')

from pXmlElement  import pXmlElement
from pAlarmLimits import WARNING_BADNESS
from pAlarmLimits import ERROR_BADNESS


BADNESS_DICT = {'clean'  : WARNING_BADNESS/2.,
                'warning': (WARNING_BADNESS + ERROR_BADNESS)/2.,
                'error'  : 2*ERROR_BADNESS
                }


class pAlarmException(pXmlElement):

    def __init__(self, domElement):
        pXmlElement.__init__(self, domElement)
        self.AlgorithmName = self.getAttribute('algorithm')
        self.ExceptionsDict = {}
        for element in self.getElementsByTagName('exception'):
            element = pXmlElement(element)
            identifier = element.evalAttribute('identifier', 'status')
            status = element.getAttribute('status_on_violation', 'error')
            if status not in BADNESS_DICT.keys():
                status = 'error'
            self.ExceptionsDict[identifier] = status

    def refersTo(self, detail = 'status'):
        return detail in self.ExceptionsDict.keys()

    def getBadness(self, detail = 'status'):
        return BADNESS_DICT[self.ExceptionsDict[detail]]
    
    def getTextSummary(self):
        summary =  'Name           : %s\n' % self.Name
        summary += 'Algorithm      : %s\n' % self.AlgorithmName
        summary += 'ExceptionDict  : %s\n' % self.ExceptionsDict
        return summary

    def __str__(self):
        return self.getTextSummary()

    
