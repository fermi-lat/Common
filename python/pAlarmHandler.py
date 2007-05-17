## @package pAlarmHandler
## @brief Module managing the data automated alarm system.

import logging
import pUtils
import time

import ROOT

from pXmlElement import pXmlElement
from pXmlAlarmParser  import pXmlAlarmParser
from pAlarm      import pAlarm


## @brief Base class handling all the alarms.

class pAlarmHandler:

    ## @brief Constructor
    ## @param self
    #  The class instance.

    def __init__(self):

        ## @var __EnabledAlarmsDict
        ## @brief Base dictionary containing all the alarms.
        #
        #  The alarms are store as (name, alarms) pairs, where
        #  name is the name of the plot the alarms refer to and alarms
        #  is a list of pAlarm instances set on the plot itself.
        
        self.__EnabledAlarmsDict = {}
        self.__XmlParser = pXmlAlarmParser("../xml/config.xml")
	self.rootFileName = 'test.root'
	self.RootFile = ROOT.TFile(self.rootFileName)
	
	self.RootObjectsDict = {}
        for i in range(self.RootFile.GetListOfKeys().LastIndex()):
	    plotKey = self.RootFile.GetListOfKeys().At(i)
	    plotObject = self.RootFile.FindObjectAny(plotKey.GetName())
            self.RootObjectsDict[plotKey.GetName()] = plotObject
	
	for alarmSet in self.__XmlParser.getEnabledAlarmSets():
    	    plotlists = []
	    for (key, value) in self.RootObjectsDict.items():
	        if key.replace(alarmSet.getName().replace('*', ''), '').isdigit():
		    plotlists.append(value)
	    alarmSet.setPlotsList(plotlists)
	    for alarm in alarmSet.getEnabledAlarmsList():
	        alarm.activate()
	        print alarm.getFormattedStatus()

    ## @brief Add an alarm for the specified plot.
    ## @param self
    #  The class instance.
    ## @param alarm
    #  The alarm to be added to the dictionary.
    ## @param plotName
    #  The name of the plot the alarm refers to.
        
    def addAlarm(self, alarm, plotName):
        if not alarm.isEnabled():
            return
        if plotName not in self.__EnabledAlarmsDict.keys():
            self.__EnabledAlarmsDict[plotName] = [alarm]
        else:
            self.__EnabledAlarmsDict[plotName].append(alarm)

    ## @brief Activate all the alarms set on a specified plot.
    #
    #  This actually verifies that the plot parameters lie in the desired
    #  ranges.
    ## @param self
    #  The class instance.
    ## @param plot
    #  The plot (a ROOT object),

    def activateAlarms(self, plot):
        try:
            for alarm in self.__EnabledAlarmsDict[plot.GetName()]:
                alarm.activate(plot)
        except KeyError:
            pass

    ## @brief Return true if all the activated alarms are clean.
    ## @param self
    #  The class instance.        

    def allAlarmsClean(self):
        for (plotName, alarmsList) in self.__EnabledAlarmsDict.items():
            for alarm in alarmsList:
                if not alarm.isClean():
                    return False
        return True

    ## @brief Return the alarm handler summary, nicely formatted to be
    #  printed on the screen.
    ## @param self
    #  The class instance.
    ## @param verbose
    #  If the flag is set, the status is printed out for all the alarms,
    #  otherwise only for those which are set (i.e. for the plots which do
    #  not satisfy the required conditions).

    def getFormattedSummary(self, verbose=False):
        summary = '** Alarm handler summary **\n'
        if self.allAlarmsClean():
            summary += 'All alarms clean.\n'
        else:
            summary += 'Plot name                        %s\n' % ALARM_HEADER
            for (plotName, alarmsList) in self.__EnabledAlarmsDict.items():
                for alarm in alarmsList:
                    if not alarm.isClean():
                        summary += '%s %s\n' %\
                                   (pUtils.expandString(plotName, 32),\
                                    alarm.getFormattedStatus())
                    else:
                        if verbose:
                            summary += '%s %s\n' %\
                                       (pUtils.expandString(plotName, 32),\
                                        alarm.getFormattedStatus())
        return summary

    ## @brief Return the alarm handler summary, in a doxygen-like fashion,
    #  to be included in the report.
    ## @todo Probably some more work is needed here, cause when the
    #  alarms table gets very long, the LaTeX part may screw up.
    #  We may think oh having more tables (one per list of per plot?).
    ## @param self
    #  The class instance.
    ## @param verbose
    #  If the flag is set, the status is printed out for all the alarms,
    #  otherwise only for those which are set (i.e. for the plots which do
    #  not satisfy the required conditions).
    
    def getDoxygenFormattedSummary(self, verbose=False):   
        caption = 'Summary table'
        label   = 'alarmHandlerTable'
        headers = ['Plot name', 'Type', 'Status', 'Parameter', 'Limits']
        summary = '\n@section alarms_summary Alarm handler summary\n\n'
        if self.allAlarmsClean():
            summary += 'All alarms clean.\n'
        else:
            summary += '@htmlonly\n'                                      +\
                       '<table border="1" width="100%">\n'                +\
                       '<caption>%s</caption>\n' % caption                +\
                       '\t<tr>\n'
            for header in headers:
                summary += '\t\t<td>%s</td>\n' % header
            summary += '\t</tr>\n'
            for (plotName, alarmsList) in self.__EnabledAlarmsDict.items():
                for alarm in alarmsList:
                    if not alarm.isClean():
                        summary += '\t<tr>\n\t\t<td>%s</td>\n' % plotName         +\
                                   alarm.getHtmlFormattedStatus() + '</tr>\n'
                    else:
                        if verbose:
                            summary += '\t<tr>\n\t\t<td>%s</td>\n' % plotName     +\
                                       alarm.getHtmlFormattedStatus() + '</tr>\n'
            summary += '</table>\n'                                       +\
                       '@endhtmlonly\n\n'                                 +\
                       '@latexonly\n'                                     +\
                       '\\begin{table}[!htb]\n'                           +\
                       '\\begin{center}\n'                                +\
                       '\\caption{%s}\n' % caption                        +\
                       '\\label{%s}\n' % label                            +\
                       '\\begin{tabular}{|c|c|c|c|c|}\n'                  +\
                       '\\hline\n'
            for header in headers[:-1]:
                summary += '%s & ' % header
            summary += '%s \\\\\n' % headers[-1]                          +\
                       '\\hline\n'                                        +\
                       '\\hline\n'
            for (plotName, alarmsList) in self.__EnabledAlarmsDict.items():
                for alarm in alarmsList:
                    if not alarm.isClean():
                        summary += pUtils.formatForLatex('%s & %s'        %\
                                   (plotName,                              \
                                    alarm.getLatexFormattedStatus()))     +\
                                    '\\hline\n'
                    else:
                        if verbose:
                            summary += pUtils.formatForLatex('%s & %s'    %\
                                       (plotName,                          \
                                        alarm.getLatexFormattedStatus())) +\
                                    '\\hline\n'
            summary += '\\end{tabular}\n'                                 +\
                       '\\end{center}\n'                                  +\
                       '\\end{table}\n'                                   +\
                       '@endlatexonly\n'
        return '%s\n\n' % summary

    ## @brief Write the doxygen summary to a file, to be included in the
    #  report at a later stage.
    ## @param self
    #  The class instance.
    ## @param filePath
    #  The output file path.
    
    def writeDoxygenFormattedSummary(self, filePath):
        logging.info('Writing the alarms file for the report...')
        startTime = time.time()
        file(filePath, 'w').writelines(self.getDoxygenFormattedSummary())
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return self.getFormattedSummary()



if __name__ == '__main__':
    ah = pAlarmHandler()

