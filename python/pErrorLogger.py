#! /usr/bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pXmlErrorMerger')

import sys
import os

from pXmlAlarmParser           import pXmlAlarmParser
from xml.dom                   import minidom
from pXmlBaseElement           import pXmlBaseElement
from pXmlElement               import pXmlElement
from pAlarm                    import pAlarm
from pAlarmOutput              import pAlarmOutput
from pAlarmXmlSummaryGenerator import pAlarmXmlSummaryGenerator
from pAlarmHandler             import pAlarmHandler
from pAlarmBaseAlgorithm       import pAlarmBaseAlgorithm



LABEL_DICT = {
    'number'  : 'Total number of errors',
    'fraction': 'Number of errors normalized to the number of events',
    'rate'    : 'Number of errors normalized to the elapsed seconds'
    }


class pErrorAlarmBaseAlgorithm(pAlarmBaseAlgorithm):

    def __init__(self, limits):
        self.Limits = limits
        self.Output = pAlarmOutput(limits, self)
        self.Exception = None



class pErrorAlarm(pAlarm):

    def __init__(self, domElement, targetObjectName = None):
        pXmlBaseElement.__init__(self, domElement)
        self.TargetObjectName = targetObjectName
        self.Limits = self._pAlarm__extractLimits()
	self.ParamsDict = self._pAlarm__extractParametersDict()
	self.ConditionsDict = self._pAlarm__extractConditionsDict()
        self.FunctionName = self.getAttribute('function')
        self.Severity = self._pAlarm__extractSeverity()
        self.Algorithm = pErrorAlarmBaseAlgorithm(self.Limits)

    def checkConditions(self, eventSummary):
        for (key, value) in self.ConditionsDict.items():
            try:
                status = eval('self._pErrorAlarm__%s(%s, eventSummary)' %\
                                  (key, value))
                if status is False:
                    return 'Condition %s not fulfilled (target = %s)' %\
                        (key, value)
            except:
                logger.warn('Could not eval condition "%s" for "%s".' %\
                                (key, self.TargetObjectName))
        return False

    def __min_seconds_elapsed(self, value, eventSummary):
        return (eventSummary['seconds_elapsed'] > value)



class pErrorLogger(pAlarmHandler):

    def __init__(self, xmlInputFilePath, xmlConfigFilePath, xmlOutputFilePath):
        self.ErrorCountsDict  = {}
        self.EventSummaryDict = {'num_error_events'      : 0,
                                 'num_processed_events'  : 0,
                                 'seconds_elapsed'       : 0,
                                 'truncated'             : 0
                                 }
        self.XmlParser = pXmlAlarmParser(xmlConfigFilePath)
        if xmlOutputFilePath == None:
            xmlOutputFilePath = xmlConfigFilePath.replace('.xml',
                                                          '_alarms.xml')
        self.XmlSummaryFilePath = xmlOutputFilePath
        outputDirPath = os.path.dirname(self.XmlSummaryFilePath)
        if outputDirPath == '':
            outputDirPath = os.path.curdir
        if not os.path.exists(outputDirPath):
            os.makedirs(outputDirPath)
            logger.debug('Creating new directory to store output files: %s' %\
                         outputDirPath)
        self.parseInputFile(xmlInputFilePath)
        self.populateAlarmLists()
        self.activateAlarms()
        self.AlarmStats = self.evalStatistics()
        pAlarmXmlSummaryGenerator(self).run()

    def parseInputFile(self, filePath, parseAll = False):
        if parseAll:
            logger.info('Parsing the entire input file %s...' % filePath)
            xmlDoc = pXmlBaseElement(minidom.parse(file(filePath)))
        else:
            # This was motivated by the fact that in the first tests
            # with the trunc64 configuration the input xml file was ~70 MB
            # long and the parsing was crashing with a memory error.
            # The idea is that we read line by line what's necessary and then
            # we parse the xml block as a string.
            logger.info('Parsing line by line the input file %s...' % filePath)
            inputData = ''
            for (i, line) in enumerate(file(filePath)):
                inputData += line
                # Once we have the eventSummary tag we're ok.
                if line.strip().startswith('<eventSummary'):
                    break
            logger.info('Done, %d line(s) read.' % i)
            logger.info('Closing open tags...')
            # Were there evennts with errors in between?
            if not line.strip().endswith('/>'):
                inputData += '    </eventSummary>\n'
            # Close the final tag.
            inputData += '\n</errorContribution>'
            xmlDoc = pXmlBaseElement(minidom.parseString(inputData))
        for element in xmlDoc.getElementsByTagName('errorType'):
            element = pXmlBaseElement(element)
            code = element.getAttribute('code')
            quantity = int(element.getAttribute('quantity'))
            try:
                self.ErrorCountsDict[code] += quantity
            except KeyError:
                self.ErrorCountsDict[code] = quantity
        element = pXmlBaseElement(xmlDoc.getElementByTagName('eventSummary'))
        logger.info('Parsing statistics...')
        for key in self.EventSummaryDict.keys():
            value = element.evalAttribute(key)
            if value is None:
                logger.warn('Could not eval "%s", leaving default.' % key)
                value = self.EventSummaryDict[key]
            self.EventSummaryDict[key] = value
            logger.info('Key = "%s", value = "%s"'% (key, value))

    def getNumProcessedEvents(self):
        return self.EventSummaryDict['num_processed_events']

    def getElapsedSeconds(self):
        return self.EventSummaryDict['seconds_elapsed']
        
    def getNumErrors(self, code):
        try:
            return self.ErrorCountsDict[code]
        except KeyError:
            return 0

    def getErrorFraction(self, code):        
        try:
            return float(self.getNumErrors(code))/self.getNumProcessedEvents()
        except ZeroDivisionError:
            return 0

    def getErrorRate(self, code):
        try:
            return float(self.getNumErrors(code))/self.getElapsedSeconds()
        except ZeroDivisionError:
            return 0

    def populateAlarmLists(self):
        logger.info('Populating the alarm lists...')
        for alarmSet in self.XmlParser.getEnabledAlarmSets():
            for element in alarmSet.getElementsByTagName('alarm'):
                xmlElement = pXmlElement(element)
                if xmlElement.Enabled:
                    alarm = pErrorAlarm(element, alarmSet.getName())
                    alarmSet.EnabledAlarmsList.append(alarm)

    def __number(self, code):
        return self.getNumErrors(code)

    def __fraction(self, code):
        return self.getErrorFraction(code)

    def __rate(self, code):
        return self.getErrorRate(code)

    def activateAlarms(self):
        logger.info('Activating the alarms...')
        for alarm in self.XmlParser.getEnabledAlarms():
            expression = 'self._pErrorLogger__%s("%s")' %\
                (alarm.FunctionName, alarm.TargetObjectName)
            try:
                alarm.Algorithm.Output.Label = LABEL_DICT[alarm.FunctionName]
            except:
                logger.warn('Could not set label for %s.' % alarm.FunctionName)
            try:
                outputValue = eval(expression)
                alarm.Algorithm.Output.setValue(outputValue)
            except:
                logger.error('Could not eval func %s for alarm on %s.' %\
                                 (alarm.FunctionName,
                                  alarm.TargetObjectName))
            errorCode = alarm.checkConditions(self.EventSummaryDict)
            if errorCode:
                alarm.Algorithm.Output.setUndefined(errorCode)

            

if __name__ == '__main__':
    from pOptionParser import pOptionParser
    optparser = pOptionParser('co', 1, 1, False)
    if optparser.Options.c is None:
        optparser.error('Please supply an xml configuration file.')
    errorLogger = pErrorLogger(optparser.Argument, optparser.Options.c,
                               optparser.Options.o)
