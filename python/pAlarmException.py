## @package pAlarmException
## @brief Module describing an alarm exception.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmException')

from pXmlElement import pXmlElement



class pAlarmException(pXmlElement):

    def __init__(self, domElement):
        pXmlElement.__init__(self, domElement)
        self.AlgorithmName = self.getAttribute('algorithm')
        if self.getElementByTagName('out_status') is None:
            self.FlippedStatus = False
        else:
            self.FlippedStatus = True
        element = self.getElementByTagName('out_details')
        if element is None:
            self.FlippedDetails = []
        else:
            element = pXmlElement(element)
            self.FlippedDetails = element.evalAttribute('identifiers')
    
    def getTextSummary(self):
        summary =  'Name           : %s\n' % self.Name
        summary += 'Algorithm      : %s\n' % self.AlgorithmName
        summary += 'Flipped status : %s\n' % self.FlippedStatus
        summary += 'Flipped details: %s'   % self.FlippedDetails
        return summary

    def __str__(self):
        return self.getTextSummary()
