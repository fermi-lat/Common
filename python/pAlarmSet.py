
import logging
import pUtils

from pXmlElement import pXmlElement
from pAlarm      import pAlarm

class pAlarmSet(pXmlElement):
    
    def __init__(self, element):      
        pXmlElement.__init__(self, element)
	self.__PlotsList         = []
	self.__EnabledAlarmsList = []
	
	
    def setPlotsList(self, plotslist):
        self.__PlotsList = plotslist
	self.__populateAlarmsList()

    def getPlotsList(self):
        return self.__PlotsList
	
    def __populateAlarmsList(self):
        for element in self.getElementsByTagName('alarm'):
	    xmlElement = pXmlElement(element)
	    if xmlElement.isEnabled():
	        for plot in self.__PlotsList:
	            self.__EnabledAlarmsList.append(pAlarm(element, plot))
		
    def getEnabledAlarmsList(self):
        return self.__EnabledAlarmsList
