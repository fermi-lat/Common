## @package pAlarmReportGenerator
## @brief Module for generating alarm handler reports.

import os
import sys
import commands
import time
import copy

import pUtils

from pBaseReportGenerator import pBaseReportGenerator


## @brief Class implementing the generation of reports for the alarm handler.
#
#  @todo Save the the content of the output detailed dictionary 

class pAlarmReportGenerator(pBaseReportGenerator):

    ## @var ALARM_STATUS_LABELS
    ## @brief Ordered list of the alarm status labels.

    ## @var SUMMARY_TABLE_HEADER
    ## @brief Header row for the summary tables appearing in the report.

    MAIN_PAGE_TITLE      = 'Alarm handler report'
    REPORT_AUTHOR        = 'Automatically generated by pAlarmHandler.py'
    ALARM_STATUS_LABELS  = ['ERROR', 'WARNING', 'UNDEFINED', 'CLEAN']
    SUMMARY_TABLE_HEADER = ['Object name', 'Algorithm', 'Status',\
                            'Output value', 'Limits', 'Details']

    ## @brief Basic constructor.
    ## @param self
    #  The class instance.
    ## @param alarmHandler
    #  The parent alarm handler.
    ## @param forceOverwrite
    #  If True (default) existing files are overwritten without messages.
    

    def __init__(self, alarmHandler, forceOverwrite = True):

        ## @var AlarmHandler
        ## @brief The parent alarm handler.

        ## @var SummaryTablesDict
        ## @brief The alarm summary tables appearing on the report.
        #
        #  There is one table per status (ERROR, WARNING, etc...).
        
        self.AlarmHandler = alarmHandler
        pBaseReportGenerator.__init__(self, self.AlarmHandler.ReportDir,\
                                      forceOverwrite)
        self.SummaryTablesDict   = {}
        for label in self.ALARM_STATUS_LABELS:
            self.SummaryTablesDict[label] = []

    def run(self, verbose = False, writeClean = False):
        self.WriteClean = writeClean
        self.openReport()
        self.addSection('alarms_summary', 'Alarm summary')
        self.addDictionary('Alarm summary',self.AlarmHandler.AlarmStats )
        self.addSection('alarms_output', 'Alarms output')
        self.addPage('alarms_details', 'Alarms details')
        self.fillSummaryTables()
        labels = copy.copy(self.ALARM_STATUS_LABELS)
        if not self.WriteClean:
            labels.remove('CLEAN')
        for label in labels:
            subsectionLabel = 'alarms_%s' % label.lower()
            subsectionTitle = 'Alarms with %s status' % label
            tableName       = 'Alarms table'
            tableCaption    = 'Alarms with %s status.' % label
            self.addSubsection(subsectionLabel, subsectionTitle)
            self.addTable(self.SUMMARY_TABLE_HEADER      ,\
                          self.SummaryTablesDict[label]  ,\
                          tableName, tableCaption)
        self.closeReport()
        self.compileReport(verbose)

    ## @brief Fill the summary tables for the report.
    ## @param self
    #  The class instance.

    def fillSummaryTables(self):
        for alarm in self.AlarmHandler.XmlParser.getEnabledAlarms():
            if alarm.Algorithm.hasDetails() and \
                    (not alarm.isClean() or self.WriteClean):
                details = alarm.getOutputDetails()
                self.addDictionary('%s---%s details' %\
                                   (alarm.getPlotName(), alarm.FunctionName),\
                                   details, 'alarms_details',\
                                   alarm.getPlotName())
                link = self.getHtmlLinkBlock('details',\
                                             'alarms_details.html#%s' %\
                                                 alarm.getPlotName())
            else:
                link = '-'
            row = [alarm.getPlotName(), alarm.FunctionName,\
                   alarm.getOutputStatus(), '%s (%s)'\
                   % (alarm.getFormattedOutputValue(),
                      alarm.getOutputLabel()),\
                   alarm.getLimits(), link]
            self.SummaryTablesDict[alarm.getOutputStatus()].append(row)

