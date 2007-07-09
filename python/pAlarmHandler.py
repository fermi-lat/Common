#!/bin/env python

## @package pAlarmHandler
## @brief Module managing the data automated alarm system.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmHandler')

import os
import sys
import pUtils
import time

from pXmlElement           import pXmlElement
from pXmlAlarmParser       import pXmlAlarmParser
from pAlarm                import pAlarm
from pAlarm                import SUMMARY_COLUMNS_DICT, SUMMARY_COLUMNS_LIST
from pAlarmReportGenerator import pAlarmReportGenerator
from pSafeROOT             import ROOT
from pRootFileManager      import pRootFileManager


## @brief Base class handling the alarms.

class pAlarmHandler:

    def __init__(self, rootFilePath, xmlConfigFilePath,\
                 xmlSummaryFilePath = None, reportDir = None,
                 printLevel = None):
        self.XmlParser = pXmlAlarmParser(xmlConfigFilePath)
        if xmlSummaryFilePath == None:
            xmlSummaryFilePath = os.path.abspath(rootFilePath)
            xmlSummaryFilePath = xmlSummaryFilePath.replace('.root', '.xml')
        self.XmlSummaryFilePath = xmlSummaryFilePath
        if reportDir == None:
            reportDir = os.path.dirname(os.path.abspath(rootFilePath))
            reportDir = os.path.join(reportDir, 'alarms')
        self.__ReportDir = reportDir
        self.RootFileManager = pRootFileManager(rootFilePath)
        self.__setAlarmSetsPlotLists()
        self.__printLevel = printLevel

    def __setAlarmSetsPlotLists(self):
        logger.info('Assigning the plots to the alarm sets...')
        for alarmSet in self.XmlParser.getEnabledAlarmSets():
            alarmSet.setPlotsList(self.RootFileManager.find(alarmSet.Name))
        logger.info('Done. %d enabled alarm set(s) found.\n' %\
                     len(self.XmlParser.getEnabledAlarmSets()))

    def activateAlarms(self):
        logger.info('Activating the alarms...')
        for alarm in self.XmlParser.getEnabledAlarms():
            alarm.activate()
        logger.info('Done. %d enabled alarm(s) found.\n' %\
                     len(self.XmlParser.getEnabledAlarms()))
        if self.__printLevel != None:
            print self
        self.writeXmlSummaryFile()

    def writeXmlSummaryFile(self):
        logger.info('Writing summary to %s...' %\
                     os.path.abspath(self.XmlSummaryFilePath))
        xmlSummaryFile = file(self.XmlSummaryFilePath, 'w')
        xmlSummaryFile.writelines('<alarmSummary>\n')
        for alarm in self.XmlParser.getEnabledAlarms():
            xmlSummaryFile.writelines(alarm.getXmlFormattedSummary())
        xmlSummaryFile.writelines('</alarmSummary>\n')
        xmlSummaryFile.close()
        logger.info('Done.')

    def __getHorizontalLine(self):
        return '-'*(sum(SUMMARY_COLUMNS_DICT.values()) +\
                    3*(len(SUMMARY_COLUMNS_LIST) - 1)) + '\n'

    def __getTxtFormattedSummaryHeader(self):
        header = '** Alarm handler summary **\n\n'
        header += self.__getHorizontalLine()
        for label in SUMMARY_COLUMNS_LIST[:-1]:
            length = SUMMARY_COLUMNS_DICT[label]
            header += '%s | ' % pUtils.expandString(label, length)
        label  = SUMMARY_COLUMNS_LIST[-1]
        length = SUMMARY_COLUMNS_DICT[label]
        header += '%s\n' % pUtils.expandString(label, length)
        header += self.__getHorizontalLine()
        return header

    def getTxtFormattedSummary(self, level=1):
        summary = self.__getTxtFormattedSummaryHeader()
        for alarm in self.XmlParser.getEnabledAlarms():
            if alarm.getStatusLevel() > level:
                summary += alarm.getTxtFormattedSummary()
        summary += self.__getHorizontalLine()
        return summary

    def writeReport(self):
        reportGenerator = pAlarmReportGenerator(self, self.__ReportDir)
        reportGenerator.run()

    def __str__(self):
        return self.getTxtFormattedSummary(self.__printLevel)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog [options] data_file')
    parser.add_option('-c', '--config-file', dest='config_file',
                      default='../xml/config.xml', type=str,
                      help='path to the input xml configuration file')
    parser.add_option('-o', '--output-file', dest='output_file',
                      default=None, type=str,
                      help='path to the output xml file')
    parser.add_option('-l', '--screen-level', dest='screen_level',
                      default=None, type=int,
                      help='level of the on-screen output, No level by default')
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
                                 options.output_file,\
                                 options.screen_level )
    alarmHandler.activateAlarms()
    alarmHandler.writeReport()
