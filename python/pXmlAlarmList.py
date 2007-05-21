
import logging
import sys

from pXmlList  import pXmlList
from pAlarmSet import pAlarmSet


class pXmlAlarmList(pXmlList):

    def __init__(self, element):
        pXmlList.__init__(self, element)
        self.__EnabledAlarmSetsDict = {}
        self.__populateEnabledAlarmSetsDict()

    def __populateEnabledAlarmSetsDict(self):
        for domElement in self.getEnabledElementsDict('alarmSet').values():
            alarmSet = pAlarmSet(domElement)
            if alarmSet.isEnabled():
                self.__EnabledAlarmSetsDict[alarmSet.getName()] = alarmSet

    def getEnabledAlarmSetsDict(self):
        return self.__EnabledAlarmSetsDict

if __name__ == '__main__':
    from xml.dom  import minidom
    doc = minidom.parse(file('../xml/config.xml'))
    for element in doc.getElementsByTagName('alarmList'):
        alarmList =  pXmlAlarmList(element)
        print alarmList.getEnabledAlarmSetsDict()
