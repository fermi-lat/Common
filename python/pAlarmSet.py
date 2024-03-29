## @package pAlarmSet
## @brief Description of an alarm set.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmSet')

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
        
        ## @var PlotsList
        ## @brief The list of plots the alarm is set on.

        ## @var EnabledAlarmsList
        ## @brief The list of enabled alarms within the set.
        
        pXmlElement.__init__(self, domElement)
        excludeList = self.evalAttribute('exclude')
        selectList = self.evalAttribute('only')
        if excludeList is not None:
            self.Selection = ('exclude', excludeList)
        elif selectList is not None:
            self.Selection = ('only', selectList)
        else:
            self.Selection = None
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
	
    def setPlotsList(self, plotsList, referenceDict):
        self.PlotsList = plotsList
	self.__populateEnabledAlarmsList(referenceDict)

    ## @brief Populate the list of enabled alarms.
    #
    #  This is actually done when the alarm handler sets the plots list
    #  for the specific alarm.
    ## @param self
    #  The class instance.
	
    def __populateEnabledAlarmsList(self, referenceDict):
        if self.PlotsList == []:
            logger.error('Alarm set "%s" has no associated plots.' %\
                         self.Name)
            logger.info('All the alarms in the set will be UNDEFINED.')
        for element in self.getElementsByTagName('alarm'):
	    xmlElement = pXmlElement(element)
	    if xmlElement.Enabled:
	        for plot in self.PlotsList:
                    alarm = pAlarm(element, plot)
                    if alarm.FunctionName == 'reference_histogram':
                        if alarm.Algorithm is not None:
                            alarm.Algorithm.setReferenceDict(referenceDict)
                        else:
                            logger.error('Could not set reference.')
                    if (alarm.Algorithm is not None) and \
                           (alarm.Algorithm.isValid()):
                        self.EnabledAlarmsList.append(alarm)
                if self.PlotsList == []:
                    alarm = pAlarm(element, None, self.Name)
                    self.EnabledAlarmsList.append(alarm)
