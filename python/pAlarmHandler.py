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
                 xmlSummaryFilePath = None, reportDir = None,\
                 verbose = False, compileLatex = False):

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
            xmlSummaryFilePath = os.path.abspath(rootFilePath)
            xmlSummaryFilePath = xmlSummaryFilePath.replace('.root', '.xml')
        self.XmlSummaryFilePath = xmlSummaryFilePath
        if reportDir == None:
            reportDir = os.path.dirname(os.path.abspath(rootFilePath))
            reportDir = os.path.join(reportDir, 'alarms')
        self.ReportDir = reportDir
        self.RootFileManager = pRootFileManager(rootFilePath)
        self.setAlarmSetsPlotLists()
        self.activateAlarms()
        pAlarmXmlSummaryGenerator(self).run()
        pAlarmReportGenerator(self).run(verbose, compileLatex)

    ## @brief Assing the ROOT objects to the alarm sets.
    #
    #  This actually dives into the ROOT file and find all the ROOT objects
    #  matching a given alarm set (taking care of the wildcards).
    ## @param self
    #  The class instance.

    def setAlarmSetsPlotLists(self):
        logger.info('Assigning the plots to the alarm sets...')
        for alarmSet in self.XmlParser.getEnabledAlarmSets():
            alarmSet.setPlotsList(self.RootFileManager.find(alarmSet.Name))
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



if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog [options] data_file')
    parser.add_option('-c', '--config-file', dest='config_file',
                      default='../xml/config.xml', type=str,
                      help='path to the input xml configuration file')
    parser.add_option('-o', '--output-file', dest='output_file',
                      default=None, type=str,
                      help='path to the output xml file')
    
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('incorrect number of arguments')
        sys.exit()
    if not os.path.isfile(args[0]):
        parser.error('first argument is not an existing file')
        sys.exit()
    if not os.path.isfile(options.config_file):
        parser.error('input configuration file (%s) not found'%\
                     (options.config_file))
        sys.exit()
           
    alarmHandler = pAlarmHandler(args[0],\
                                 options.config_file,\
                                 options.output_file)
