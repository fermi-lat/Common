## @package pXmAlarmlList
## @brief Description of a xml alarm list.

import sys

from pXmlList  import pXmlList
from pAlarmSet import pAlarmSet


## @brief Class describing a list of alarm sets.

class pXmlAlarmList(pXmlList):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the list. 

    def __init__(self, element):

        ## @var EnabledAlarmSetsDict
        ## @brief Dictionary containing all the enabled alarm sets.
        
        pXmlList.__init__(self, element)
        self.EnabledAlarmSetsDict = {}
        self.__populateEnabledAlarmSetsDict()

    ## @brief Populate the list of enabled alarm sets.
    ## @param self
    #  The class instance.

    def __populateEnabledAlarmSetsDict(self):
        for domElement in self.getEnabledElementsDict('alarmSet').values():
            alarmSet = pAlarmSet(domElement)
            self.EnabledAlarmSetsDict[alarmSet.Name] = alarmSet

    def getTextSummary(self):
        return pXmlList.getTextSummary(self) +\
               'En. sets : %s' % self.EnabledAlarmSetsDict

    def __str__(self):
        return self.getTextSummary()


if __name__ == '__main__':
    from xml.dom  import minidom
    doc = minidom.parse(file('../xml/config.xml'))
    for element in doc.getElementsByTagName('alarmList'):
        alarmList =  pXmlAlarmList(element)
        print alarmList
