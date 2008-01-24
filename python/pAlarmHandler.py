#!/bin/env python

## @package pAlarmHandler
## @brief Module managing the data automated alarm system.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmHandler')

import os
import sys
import pUtils
import time

from pXmlElement               import pXmlElement
from pXmlAlarmParser           import pXmlAlarmParser
from pAlarm                    import pAlarm
from pAlarmReportGenerator     import pAlarmReportGenerator
from pAlarmXmlSummaryGenerator import pAlarmXmlSummaryGenerator
from pSafeROOT                 import ROOT
from pRootFileManager          import pRootFileManager


## @brief Base class handling the alarms.
#
#  The alarm handler digests ROOT file containing either TTrees of generic
#  plots (histograms, TGraphs, etc.) and verify they are within specification,
#  according to an input xml configuration file.
#  An xml output summary for the web interface, along with a doxygen report,
#  is produced.

class pAlarmHandler:

    ## @brief Basic constructor.
    ## @param self
    #  The class instance.
    ## @param rootFilePath
    #  The path to the input ROOT file containing the data.
    ## @param xmlConfigFilePath
    #  The path to the input xml configuration file.
    ## @param xmlSummaryFilePath
    #  The path to the output xml summary path.
    ## @param reportDir
    #  The path to directory containing the final report.
    
    def __init__(self, rootFilePath, xmlConfigFilePath,\
                 xmlSummaryFilePath = None):

        ## @var XmlParser
        ## @brief The pXmlAlarmParser object responsible for parsing the
        #  input xml file.

        ## @var XmlSummaryFilePath
        ## @brief The path to the output xml summary path.

        ## @var ReportDir
        ## @brief The path to directory containing the final report.

        ## @var RootFileManager
        ## @brief A pRootFileManager object providing the facilities for
        #  managing the input ROOT file.

        
        self.XmlParser = pXmlAlarmParser(xmlConfigFilePath)
        if xmlSummaryFilePath == None:
            xmlSummaryFilePath = rootFilePath.replace('.root', '.alarms.xml')
        self.XmlSummaryFilePath = xmlSummaryFilePath

        outputDirPath = os.path.dirname(self.XmlSummaryFilePath)
        if not os.path.exists(outputDirPath):
            os.makedirs(outputDirPath)
            logger.debug('Creating new directory to store output files: %s' % outputDirPath )
        
        self.ReportDir = xmlSummaryFilePath.replace('.xml','')
        self.RootFileManager = pRootFileManager(rootFilePath)
        self.setAlarmSetsPlotLists()
        self.activateAlarms()
        self.AlarmStats = self.evalStatistics()
        pAlarmXmlSummaryGenerator(self).run()
        

    ## @brief Assing the ROOT objects to the alarm sets.
    #
    #  This actually dives into the ROOT file and find all the ROOT objects
    #  matching a given alarm set (taking care of the wildcards).
    ## @param self
    #  The class instance.

    def setAlarmSetsPlotLists(self):
        logger.info('Assigning the plots to the alarm sets...')
        for alarmSet in self.XmlParser.getEnabledAlarmSets():
            PlotList = self.RootFileManager.find(alarmSet.Name)
            alarmSet.setPlotsList(PlotList)
            if PlotList == []:
                logger.error('Alarm set %s has no associated alarms.' %\
                             alarmSet.Name)
        logger.info('Done. %d enabled alarm set(s) found.\n' %\
                    len(self.XmlParser.getEnabledAlarmSets()))

    ## @brief Activate the alarms.
    ## @param self
    #  The class instance.

    def activateAlarms(self):
        logger.info('Activating the alarms...')
        for alarm in self.XmlParser.getEnabledAlarms():
            alarm.activate()
        logger.info('Done. %d enabled alarm(s) found.\n' %\
                     len(self.XmlParser.getEnabledAlarms()))
        
    ## @brief Evaluation of alarm statistics to be written
    #  at the beginning of the output .xml file anf .html report
    ## @param self
    #  The class instance.
    
    def evalStatistics(self):
        StatDict = {"error"     : 0,
                    "warning"   : 0,
                    "clean"     : 0,
                    "undefined" : 0}
        for alarm in self.XmlParser.getEnabledAlarms():
            StatDict[alarm.getStatus().lower()] +=1
        return StatDict



if __name__ == '__main__':
    from pOptionParser import pOptionParser
    optparser = pOptionParser('corV',1,1,False)
    if optparser.Options.c is None:
        optparser.error('Please supply an xml configuration file.')
    if optparser.Options.V and not optparser.Options.r:
        logger.warning('Without the -r option the -V option will be ignored!')
    alarmHandler = pAlarmHandler(optparser.Argument, optparser.Options.c,\
                                 optparser.Options.o)
    if optparser.Options.r:
        ReportGenerator = pAlarmReportGenerator(alarmHandler)
        ReportGenerator.run(False)
        if optparser.Options.V:
            ReportGenerator.viewReport()

        
