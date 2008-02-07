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

        ## @var AlarmListsDict
        ## @brief A dictionary containing the alarm lists, indexed by name.

        ## @var EnabledAlarmSetsDict
        ## @brief A dictionary containing the enabled alem sets, indexed by
        #  name.

        ## @var XmlConfigFilePath
        ## @brief The path to the xml config file. 

        ## @var XmlDoc
        ## @brief The xml document representation from the minidom module.
        
        self.AlarmListsDict       = {}
        self.EnabledAlarmSetsDict = {}
        self.XmlConfigFilePath    = xmlConfigFilePath
        if os.path.exists(self.XmlConfigFilePath):
            self.XmlDoc = minidom.parse(file(xmlConfigFilePath))
        else:
            sys.exit('Input configuration file %s not found. Exiting...' %\
        	     xmlConfigFilePath)
        self.__populateAlarmLists()

    ## @brief Populate the alarm lists and the dictionary of the enabled
    #  alarm sets.
    ## @param self
    #  The class instance.

    def __populateAlarmLists(self):
        for element in self.XmlDoc.getElementsByTagName('alarmList'):
    	    xmlList = pXmlList(element)
	    self.AlarmListsDict[xmlList.Name] = xmlList
	    if xmlList.Enabled:
	        for (key, value) in  xmlList.getEnabledItems('alarmSet'):
                    self.EnabledAlarmSetsDict[key] = pAlarmSet(value)

    ## @brief Return the enabled alarm sets.
    ## @param self
    #  The class instance.
	
    def getEnabledAlarmSets(self):
        return self.EnabledAlarmSetsDict.values()

    ## @brief Return the enabled alarms.
    ## @param self
    #  The class instance.

    def getEnabledAlarms(self):
        alarmsList = []
        for alarmSet in self.getEnabledAlarmSets():
	    for alarm in alarmSet.EnabledAlarmsList:
                alarmsList.append(alarm)
        alarmsList.sort()
        return alarmsList

    ## @brief Return a formatted text representation of the class instances.
    ## @param self
    #  The class instance.

    def getTextSummary(self):
        return 'Configuration file %s contains:\n' % self.XmlConfigFilePath +\
               '%d alarm list(s)\n' % len(self.AlarmListsDict) +\
               '%d enabled alarm set(s)' % len(self.EnabledAlarmSetsDict)

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return self.getTextSummary()
	    


if __name__ == '__main__':
    parser = pXmlAlarmParser('../xml/alarmconfig.xml')
    print 'Printing parser information...'
    print parser
    print 'Printing detailed informations for the alarm sets...'
    for set in parser.getEnabledAlarmSets():
        print set
