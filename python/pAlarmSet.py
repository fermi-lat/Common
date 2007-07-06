
## @package pAlarmSet
## @brief Description of an alarm set.

import pUtils

from pXmlElement import pXmlElement
from pAlarm      import pAlarm


## @brief Class describing an alarm set.
#
#  An alarm set is a set of alarms set on a particular plot
#  (or a particular set of plots which can be specified using
#  wildcards).

class pAlarmSet(pXmlElement):

    ## @brief Basic constructor.
    ## @param self
    #  The class instance.
    ## @param domElement
    #  The xml element from which the alarm is constructed.
    
    def __init__(self, domElement):
        
        ## @var __PlotsList
        ## @brief The list of plots the alarm is set on.

        ## @var __EnabledAlarmsList
        ## @brief The list of enabled alarms within the set.
        
        pXmlElement.__init__(self, domElement)
	self.PlotsList         = []
	self.EnabledAlarmsList = []

    ## @brief Set the plot list for the alarm set.
    #
    #  This is done by the alarm handler, which is responsible for
    #  diving into the ROOT file and finding all the objects matching the
    #  name defined into the xml configuration file.
    ## @param self
    #  The class instance.
    ## @param plotsList
    #  The list of plots.
	
    def setPlotsList(self, plotsList):
        self.PlotsList = plotsList
	self.__populateEnabledAlarmsList()

    ## @brief Populate the list of enabled alarms.
    #
    #  This is actually done when the alarm handler sets the plots list
    #  for the specific alarm.
    ## @param self
    #  The class instance.
	
    def __populateEnabledAlarmsList(self):
        for element in self.getElementsByTagName('alarm'):
	    xmlElement = pXmlElement(element)
	    if xmlElement.Enabled:
	        for plot in self.PlotsList:
                    alarm = pAlarm(element, plot)
                    if (alarm.Algorithm is not None) and \
                           (alarm.Algorithm.isValid()):
                        self.EnabledAlarmsList.append(alarm)
                    
