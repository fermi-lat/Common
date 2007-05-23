
## @package pXmlAlarmParser
## @brief Specific xml parser for the alarm handler.

import os
import sys
from xml.dom import minidom

from pXmlList  import pXmlList
from pAlarmSet import pAlarmSet


## @brief Class describing a xml parser specific to the alarm handler.

class pXmlAlarmParser:

    ## @brief Basic constructor.
    ## @param self
    #  The class instance.
    ## @param xmlConfigFilePath
    #  The path to the xml configuration file.

    def __init__(self, xmlConfigFilePath):

        ## @var self.__AlarmListsDict
        ## @brief A dictionary containing the alarm lists, indexed by name.

        ## @var self.__EnabledAlarmSetsDict
        ## @brief A dictionary containing the enabled alem sets, indexed by
        #  name.

        ## @var __XmlDoc
        ## @brief The xml document representation from the minidom module.
        
        self.__AlarmListsDict       = {}
        self.__EnabledAlarmSetsDict = {}
        if os.path.exists(xmlConfigFilePath):
            self.__XmlDoc = minidom.parse(file(xmlConfigFilePath))
        else:
            sys.exit('Input configuration file %s not found. Exiting...' %\
        	     filePath)
        self.populateAlarmLists()

    ## @brief Populate the alarm lists and the dictionary of the enabled
    #  alarm sets.
    ## @param self
    #  The class instance.

    def populateAlarmLists(self):
        for element in self.__XmlDoc.getElementsByTagName('alarmList'):
    	    xmlList = pXmlList(element)
	    self.__AlarmListsDict[xmlList.getName()] = xmlList
	    if xmlList.isEnabled():
	        for (key, value) in \
                        xmlList.getEnabledElementsDict('alarmSet').items():
                    self.__EnabledAlarmSetsDict[key] = pAlarmSet(value)

    ## @brief Return the dictionary of the enebled alarm sets.
    ## @param self
    #  The class instance.
	   
    def getEnabledAlarmSetsDict(self):
    	return self.__EnabledAlarmSetsDict

    ## @brief Return the enabled alarm sets.
    ## @param self
    #  The class instance.
	
    def getEnabledAlarmSets(self):
        return self.__EnabledAlarmSetsDict.values()

    ## @brief Return the enabled alarms.
    ## @param self
    #  The class instance.

    def getEnabledAlarms(self):
        alarmsList = []
        for alarmSet in self.getEnabledAlarmSets():
	    for alarm in alarmSet.getEnabledAlarmsList():
                alarmsList.append(alarm)
        return alarmsList
	    


if __name__ == '__main__':
    parser = pXmlAlarmParser('../xml/config.xml')
    for alarmSet in parser.getEnabledAlarmSets():
    	print 'Alarm set found!\n%s'  % alarmSet
	for alarm in alarmSet.getEnabledAlarmsList():
	    print alarm.getFormattedStatus()
