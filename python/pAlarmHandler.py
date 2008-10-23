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
from pXmlExceptionParser       import pXmlExceptionParser
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
    
    def __init__(self, rootFilePath, xmlConfigFilePath, xmlExceptionsFilePath,\
                     xmlSummaryFilePath, referenceFolderPath):

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

        ## @var AlarmStats
        ## @brief Basic alarm handler statistics.
        
        self.AlarmExceptionsDict = {}
        if xmlExceptionsFilePath is not None:
            xmlExceptionParser = pXmlExceptionParser(xmlExceptionsFilePath)
            self.AlarmExceptionsDict = xmlExceptionParser.AlarmExceptionsDict
        self.XmlParser = pXmlAlarmParser(xmlConfigFilePath)
        if xmlSummaryFilePath == None:
            xmlSummaryFilePath = rootFilePath.replace('.root', '.alarms.xml')
        self.XmlSummaryFilePath = xmlSummaryFilePath
        outputDirPath = os.path.dirname(self.XmlSummaryFilePath)
        if outputDirPath == '':
            outputDirPath = os.path.curdir
        if not os.path.exists(outputDirPath):
            os.makedirs(outputDirPath)
            logger.debug('Creating new directory to store output files: %s' %\
                             outputDirPath )
        self.ReportDir = xmlSummaryFilePath.replace('.xml','')
        self.ReferenceFolderPath = referenceFolderPath
        self.ReferenceHistogramsDict = {}
        self.loadReferenceHistograms()
        self.RootFileManager = pRootFileManager(rootFilePath)
        self.setAlarmSetsPlotLists()
        self.activateAlarms()
        self.AlarmStats = self.evalStatistics()
        pAlarmXmlSummaryGenerator(self).run()

    ## @brief Load the reference histograms into memory.
    #
    #  If \ref ReferenceFolderPath is not set, then the funtion does not
    #  actually do nothing. Otherwise it loops over the root file in the
    #  specified folders, opens them and put a reference into the
    #  dictionary \ref ReferenceHistogramsDict.

    def loadReferenceHistograms(self):
        if self.ReferenceFolderPath is None:
            logger.info('Path to the reference histograms folder not set.')
            logger.info('Reference histograms will not be loaded.')
        else:
            logger.info('Loading reference histograms into memory...')
            if not os.path.exists(self.ReferenceFolderPath):
                logger.error('%s does not exist. References not loaded.' %\
                             self.ReferenceFolderPath)
                return
            if not os.path.isdir(self.ReferenceFolderPath):
                logger.error('%s is not a directory. References not loaded.' %\
                             self.ReferenceFolderPath)
                return
            fileNameList = os.listdir(self.ReferenceFolderPath)
            for fileName in fileNameList:
                if fileName.endswith('.root'):
                    filePath = os.path.join(self.ReferenceFolderPath, fileName)
                    logger.info('Loading %s...' % filePath)
                    rootFile = ROOT.TFile(filePath)
                    if rootFile.IsZombie():
                        logger.error('Problems loading %s.' % filePath)
                    else:
                        self.ReferenceHistogramsDict[fileName] = rootFile
                        logger.info('Done.')

    ## @brief Assing the ROOT objects to the alarm sets.
    #
    #  This actually dives into the ROOT file and find all the ROOT objects
    #  matching a given alarm set (taking care of the wildcards).
    ## @param self
    #  The class instance.

    def setAlarmSetsPlotLists(self):
        logger.info('Assigning the plots to the alarm sets...')
        for alarmSet in self.XmlParser.getEnabledAlarmSets():
            PlotList = self.RootFileManager.find(alarmSet.Name,\
                                                 alarmSet.Selection)
            alarmSet.setPlotsList(PlotList)
        logger.info('Done. %d enabled alarm set(s) found.\n' %\
                    len(self.XmlParser.getEnabledAlarmSets()))

    ## @brief Activate the alarms.
    ## @param self
    #  The class instance.

    def activateAlarms(self):
        logger.info('Activating the alarms...')
        for alarm in self.XmlParser.getEnabledAlarms():
            logger.debug('Activating alarm on "%s"' % alarm.getPlotName())
            alarmTuple = (alarm.getPlotName(), alarm.FunctionName)
            if alarmTuple in self.AlarmExceptionsDict.keys():
                logger.info('Setting exception(s) on %s %s...' % alarmTuple)
                logger.info('Details:\n%s' %\
                            self.AlarmExceptionsDict[alarmTuple])
                alarm.Algorithm.Exception =\
                                          self.AlarmExceptionsDict[alarmTuple]
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
            StatDict[alarm.getOutputStatus().lower()] +=1
        return StatDict



if __name__ == '__main__':
    from pOptionParser import pOptionParser
    optparser = pOptionParser('corVxwR',1,1,False)
    if optparser.Options.c is None:
        optparser.error('Please supply an xml configuration file.')
    if optparser.Options.V and not optparser.Options.r:
        logger.warning('Without the -r option the -V option will be ignored!')
    alarmHandler = pAlarmHandler(optparser.Argument, optparser.Options.c,\
                                 optparser.Options.x, optparser.Options.o,
                                 optparser.Options.R)
    if optparser.Options.r:
        ReportGenerator = pAlarmReportGenerator(alarmHandler)
        ReportGenerator.run(False, optparser.Options.w)
        if optparser.Options.V:
            ReportGenerator.viewReport()
    alarmHandler.RootFileManager.closeFile()
        
