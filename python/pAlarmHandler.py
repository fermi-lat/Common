#!/bin/env python

## @package pAlarmHandler
## @brief Module managing the data automated alarm system.

import logging
import os
import sys
import pUtils
import time

import ROOT

from pXmlElement      import pXmlElement
from pXmlAlarmParser  import pXmlAlarmParser
from pAlarm           import pAlarm

logging.basicConfig(level=logging.INFO)


## @brief Base class handling the alarms.

class pAlarmHandler:

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param rootFilePath
    #  Path to the input ROOT file containing the plots.
    ## @param xmlConfigFilePath
    #  Path to the xml configuration file containing the alarms definition.
    ## @param xmlSummaryFilePath
    #  Path to the output xml file containing the alarm handler complete
    #  status.
    #
    #  Used by the web tools for visualization.

    def __init__(self, rootFilePath = 'test.root',\
                 xmlConfigFilePath  = '../xml/config.xml',
                 xmlSummaryFilePath = './output.xml'):

        ## @var __XmlParser
        ## @brief The base xml parser.

        ## @var __XmlSummaryFilePath
        #  Path to the output summary xml file.

        ## @var __RootFile
        ## @brief The input ROOT.TFile object.

        ## @var __RootObjectsDict
        ## @brief Dictionary containing all the objects in the input
        #  ROOT file, indexed by object name.
        
        self.__XmlParser = pXmlAlarmParser(xmlConfigFilePath)
        self.__XmlSummaryFilePath = xmlSummaryFilePath
	self.__RootFile = ROOT.TFile(rootFilePath)
        self.__RootObjectsDict = {}
	self.__populateRootObjectsDict()
        self.__setAlarmSetsPlotLists()

    ## @brief Populate the dictionary of ROOT objects.
    #
    #  This function loops over the list of keys into the ROOT file
    #  and adds the corresponding objects to the dictionary.
    ## @param self
    #  The class instance.

    def __populateRootObjectsDict(self):
        for i in range(self.__RootFile.GetListOfKeys().LastIndex()):
	    key    = self.__RootFile.GetListOfKeys().At(i)
            name   = key.GetName()
	    object = self.__RootFile.FindObjectAny(name)
            self.__RootObjectsDict[name] = object

    ## @brief Go through all the alarms set and identify in the ROOT
    #  file the corresponding ROOT objects (i.e. plots).
    #
    #  At this moment the actual pAlarm objects are also created
    #  (one for each plot).
    ## @param self
    #  The class instance.

    def __setAlarmSetsPlotLists(self):
        for alarmSet in self.__XmlParser.getEnabledAlarmSets():
	    alarmSet.setPlotsList(self.__findRootObjects(alarmSet.getName()))

    ## @brief Return all the ROOT objects whose name matches a specified
    #  pattern into the __RootObjectsDict variable.
    #
    #  This allow to use wildcards in the xml file defining the alarms
    #  (i.e. if an identical alarm is specified on multiple plots, differing
    #  in the tower ID, for instance, it doesn't need to be specified
    #  each signgle time). At the moment the wildcards stand for numbers only.
    ## @param self
    #  The class instance.
    ## @param pattern
    #  The pattern (possibly including wildcards) identifying the object name.

    def __findRootObjects(self, pattern):
        objectsList = []
        for (key, value) in self.__RootObjectsDict.items():
            if key.replace(pattern.replace('*', ''), '').isdigit():
                objectsList.append(value)
        return objectsList

    ## @brief Activate all the alarms (i.e. dive into the ROOT file and
    #  look at the plots).
    ## @param self
    #  The class instance.
    
    def activateAlarms(self):
        for alarm in self.__XmlParser.getEnabledAlarms():
            alarm.activate()
        print self
        self.writeXmlSummaryFile()

    ## @brief Write the alarm handler summary to an xml file which
    #  can be parsed by the web tool for later display.
    ## @param self
    #  The class instance.

    def writeXmlSummaryFile(self):
        logging.info('Writing summary to %s...' %\
                     os.path.abspath(self.__XmlSummaryFilePath))
        xmlSummaryFile = file(self.__XmlSummaryFilePath, 'w')
        xmlSummaryFile.writelines('<alarmSummary>\n')
        for alarm in self.__XmlParser.getEnabledAlarms():
            xmlSummaryFile.writelines(alarm.getXmlFormattedSummary())
        xmlSummaryFile.writelines('</alarmSummary>\n')
        xmlSummaryFile.close()
        logging.info('Done.')

    ## @brief Return a summary of the alarm handler status, formatted
    #  for the terminal output.
    ## @param self
    #  The class instance.
    ## @param level
    #  The screen level for the summary output.
    #
    #  It allows to screen the CLEAN alarms, for instance, when printing
    #  the summary on the terminal.

    def getTxtFormattedSummary(self, level=1):
        summary = ''
        for alarm in self.__XmlParser.getEnabledAlarms():
            if alarm.getLevel() > level:
                summary += alarm.getTxtFormattedSummary()
        return summary

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return self.getTxtFormattedSummary()
                
    
##     def getDoxygenFormattedSummary(self, verbose=False):   
##         caption = 'Summary table'
##         label   = 'alarmHandlerTable'
##         headers = ['Plot name', 'Type', 'Status', 'Parameter', 'Limits']
##         summary = '\n@section alarms_summary Alarm handler summary\n\n'
##         if self.allAlarmsClean():
##             summary += 'All alarms clean.\n'
##         else:
##             summary += '@htmlonly\n'                                      +\
##                        '<table border="1" width="100%">\n'                +\
##                        '<caption>%s</caption>\n' % caption                +\
##                        '\t<tr>\n'
##             for header in headers:
##                 summary += '\t\t<td>%s</td>\n' % header
##             summary += '\t</tr>\n'
##             for (plotName, alarmsList) in self.__EnabledAlarmsDict.items():
##                 for alarm in alarmsList:
##                     if not alarm.isClean():
##                         summary += '\t<tr>\n\t\t<td>%s</td>\n' % plotName         +\
##                                    alarm.getHtmlFormattedStatus() + '</tr>\n'
##                     else:
##                         if verbose:
##                             summary += '\t<tr>\n\t\t<td>%s</td>\n' % plotName     +\
##                                        alarm.getHtmlFormattedStatus() + '</tr>\n'
##             summary += '</table>\n'                                       +\
##                        '@endhtmlonly\n\n'                                 +\
##                        '@latexonly\n'                                     +\
##                        '\\begin{table}[!htb]\n'                           +\
##                        '\\begin{center}\n'                                +\
##                        '\\caption{%s}\n' % caption                        +\
##                        '\\label{%s}\n' % label                            +\
##                        '\\begin{tabular}{|c|c|c|c|c|}\n'                  +\
##                        '\\hline\n'
##             for header in headers[:-1]:
##                 summary += '%s & ' % header
##             summary += '%s \\\\\n' % headers[-1]                          +\
##                        '\\hline\n'                                        +\
##                        '\\hline\n'
##             for (plotName, alarmsList) in self.__EnabledAlarmsDict.items():
##                 for alarm in alarmsList:
##                     if not alarm.isClean():
##                         summary += pUtils.formatForLatex('%s & %s'        %\
##                                    (plotName,                              \
##                                     alarm.getLatexFormattedStatus()))     +\
##                                     '\\hline\n'
##                     else:
##                         if verbose:
##                             summary += pUtils.formatForLatex('%s & %s'    %\
##                                        (plotName,                          \
##                                         alarm.getLatexFormattedStatus())) +\
##                                     '\\hline\n'
##             summary += '\\end{tabular}\n'                                 +\
##                        '\\end{center}\n'                                  +\
##                        '\\end{table}\n'                                   +\
##                        '@endlatexonly\n'
##         return '%s\n\n' % summary

##     ## @brief Write the doxygen summary to a file, to be included in the
##     #  report at a later stage.
##     ## @param self
##     #  The class instance.
##     ## @param filePath
##     #  The output file path.
    
##     def writeDoxygenFormattedSummary(self, filePath):
##         logging.info('Writing the alarms file for the report...')
##         startTime = time.time()
##         file(filePath, 'w').writelines(self.getDoxygenFormattedSummary())
##         logging.info('Done in %s s.\n' % (time.time() - startTime))


if __name__ == '__main__':
    alarmHandler = pAlarmHandler()
    alarmHandler.activateAlarms()
