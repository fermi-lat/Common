import os
import sys
from xml.dom import minidom

from pXmlList  import pXmlList
from pAlarmSet import pAlarmSet

class pXmlAlarmParser:

    def __init__(self, filePath):
        self.__AlarmListsDict       = {}
        self.__EnabledAlarmSetsDict = {}
        if os.path.exists(filePath):
            self.XmlDoc = minidom.parse(file(filePath))
        else:
            sys.exit('Input configuration file %s not found. Exiting...' %\
        	     filePath)
        self.populateAlarmLists()

    def populateAlarmLists(self):
        for element in self.XmlDoc.getElementsByTagName('alarmList'):
    	    xmlList = pXmlList(element)
	    self.__AlarmListsDict[xmlList.getName()] = xmlList
	    if xmlList.isEnabled():
	        for (key, value) in xmlList.getEnabledElementsDict('alarmSet').items():
                    self.__EnabledAlarmSetsDict[key] = pAlarmSet(value)
	   
    def getEnabledAlarmSetsDict(self):
    	return self.__EnabledAlarmSetsDict
	
    def getEnabledAlarmSets(self):
        return self.__EnabledAlarmSetsDict.values()
	    


if __name__ == '__main__':
    parser = pXmlAlarmParser('../xml/config.xml')
    for alarmSet in parser.getEnabledAlarmSets():
    	print 'Alarm set found!\n%s'  % alarmSet
	for alarm in alarmSet.getEnabledAlarmsList():
	    print alarm.getFormattedStatus()
