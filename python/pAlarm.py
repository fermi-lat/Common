
## @package pAlarm
## @brief Description of an alarm.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarm')

import sys
import re
import pUtils
from pXmlBaseElement import pXmlBaseElement
from pAlarmLimits import pAlarmLimits


SUMMARY_COLUMNS_LIST = ['Plot name',
                        'Function' ,
                        'Status'   ,
                        'Output'   ,
                        'Limits'
                        ]
SUMMARY_COLUMNS_DICT = {'Plot name': 25,
                        'Function' : 10,
                        'Status'   : 7 ,
                        'Output'   : 6 ,
                        'Limits'   : 19
                        }


## @brief Class describing an alarm to be activated on a plot.
#
#  The basic idea, here, is that the alarm must verify whether a simple
#  plot parameter (average value or RMS of a histogram, etc., depending
#  on the alarm Function) lies or not within a specified interval.

class pAlarm(pXmlBaseElement):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param domElement
    #  The xml element from which the alarm is constructed.
    ## @param plot
    #  The ROOT object the alarm is set on.
    
    def __init__(self, domElement, rootObject):

        ## @var __Function
        ## @brief The type of the alarm (i.e. the specific algorithm).

        ## @var __ParamsDict
        ## @brief Dictionary of optional parameters to be passed to the
        #  algorithm implementing the alarm.
 
        pXmlBaseElement.__init__(self, domElement)
	self.RootObject      = rootObject
        self.Limits          = self.__getLimits()
	self.ParamsDict      = self.__getParametersDict()
        self.FunctionName    = self.getAttribute('function')
        try:
            exec('from alg__%s import alg__%s' % (self.FunctionName,\
                                                  self.FunctionName))
            self.Algorithm = eval('alg__%s(self.Limits, self.RootObject, ' %\
                                  self.FunctionName + 'self.ParamsDict)' )
        except ImportError:
            logger.error('Could not import alg__%s. ' % self.FunctionName +\
                          'The alarm will be ignored.')
            self.Algorithm = None

        
    ## @brief

    def __getLimits(self):
        warnLims = pXmlBaseElement(self.getElementByTagName('warning_limits'))
        warnMin  = warnLims.getAttribute('min')
        warnMax  = warnLims.getAttribute('max')
        errLims  = pXmlBaseElement(self.getElementByTagName('error_limits'))
        errMin   = errLims.getAttribute('min')
        errMax   = errLims.getAttribute('max')
        strLims  = '%s%s%s%s' % (warnMin, warnMax, errMin, errMax)
        if 'MEAN' in strLims:
            mean = str(self.RootObject.GetMean())
        else:
            mean = ''
        if 'RMS' in strLims:
            rms = str(self.RootObject.GetRMS())
        else:
            rms = ''
        if 'ENTRIES' in strLims:
            entries = str(self.RootObject.GetEntries())
        else:
            entries = ''
        warnMin  = warnMin.upper().replace('MEAN', mean)
        warnMin  = warnMin.upper().replace('RMS', rms)
        warnMin  = warnMin.upper().replace('ENTRIES', entries)
        warnMin  = eval(warnMin)
        warnMax  = warnMax.upper().replace('MEAN', mean)
        warnMax  = warnMax.upper().replace('RMS', rms)
        warnMax  = warnMax.upper().replace('ENTRIES', entries)
        warnMax  = eval(warnMax)
        errMin   = errMin.upper().replace('MEAN', mean)
        errMin   = errMin.upper().replace('RMS', rms)
        errMin   = errMin.upper().replace('ENTRIES', entries)
        errMin   = eval(errMin)
        errMax   = errMax.upper().replace('MEAN', mean)
        errMax   = errMax.upper().replace('RMS', rms)
        errMax   = errMax.upper().replace('ENTRIES', entries)
        errMax   = eval(errMax)
        try:
            return pAlarmLimits(warnMin, warnMax, errMin, errMax)
        except:
            logger.error('Could not eval limits. Returning None...' )
            return None

    ## @brief Retrieve the function parameters from the xml
    #  element.
    ## @param self
    #  The class instance.

    def __getParametersDict(self):
        parametersDict = {}
        for domElement in self.getElementsByTagName('parameter'):
            xmlElement = pXmlBaseElement(domElement)
            parametersDict[xmlElement.getAttribute('name')] =\
                           xmlElement.evalAttribute('value')
        return parametersDict

    def getOutput(self):
        return self.Algorithm.Output

    def getStatus(self):
        return self.getOutput().getStatus()

    def getStatusLevel(self):
        return self.getOutput().getStatusLevel()
    
    def getStatusLabel(self):
        return self.getOutput().getStatusLabel()
    
    def isClean(self):
        return self.getOutput().isClean()
    
    def getOutputValue(self):
        return self.getOutput().getValue()
    
    def getOutputDict(self):
        return self.getOutput().getDict()
    
    def getOutputDictValue(self, key):
        return self.getOutput().getDictValue(key)
    
    ## @brief Activate the alarm (i.e. actually verify the plot).
    ## @param self
    #  The class instance.

    def activate(self):
        self.Algorithm.apply()

    ## @brief Return the name of the plot the alarm is set on.
    ## @param self
    #  The class instance.            

    def getRootObjectName(self):
        return self.RootObject.GetName()

    ## @brief Return the plot name, formatted to be printed on the terminal.
    ## @param self
    #  The class instance.      

    def getTxtFormattedPlotName(self):
        return pUtils.expandString(self.getRootObjectName(),\
                                   SUMMARY_COLUMNS_DICT['Plot name'])

    ## @brief Return the alarm function, formatted to be printed on the
    #  terminal.
    ## @param self
    #  The class instance.

    def getTxtFormattedFunction(self):
        return pUtils.expandString(self.FunctionName,\
                                   SUMMARY_COLUMNS_DICT['Function'])

    ## @brief Return the alarm status, formatted to be printed on the
    #  terminal.
    ## @param self
    #  The class instance.

    def getTxtFormattedStatus(self):
        return pUtils.expandString(self.getStatusLabel(),\
                                   SUMMARY_COLUMNS_DICT['Status'])

    ## @brief Return the output value of the alarm, formatted to be printed
    #  on the terminal.
    ## @param self
    #  The class instance.

    def getTxtFormattedOutputValue(self):
        return pUtils.expandNumber(self.getOutputValue(),\
                                   SUMMARY_COLUMNS_DICT['Output'])

    def getFullTxtFormattedLimits(self):
        return '[%s/%s, %s/%s]' % (self.Limits.ErrorMin,  \
                                   self.Limits.WarningMin,\
                                   self.Limits.WarningMax,\
                                   self.Limits.ErrorMax)

    ## @brief Return the alarm limits, formatted to be printed on the terminal.
    ## @param self
    #  The class instance.

    def getTxtFormattedLimits(self):
        return pUtils.expandString(self.getFullTxtFormattedLimits(),\
                                   SUMMARY_COLUMNS_DICT['Limits'])

    ## @brief Return all the relevant information on the alarm status,
    #  nicely formatted.
    ## @param self
    #  The class instance.

    def getTxtFormattedSummary(self):
        return '%s | %s | %s | %s | %s\n' % (self.getTxtFormattedPlotName(),
                                             self.getTxtFormattedFunction(),
                                             self.getTxtFormattedStatus(),
                                             self.getTxtFormattedOutputValue(),
                                             self.getTxtFormattedLimits())

    def getTableSummaryRow(self):
        return [self.getRootObjectName(), self.FunctionName,\
                self.getStatusLabel(), self.getOutputValue(),\
                self.getFullTxtFormattedLimits(), 'N/A']

    ## @brief Return all the relevant information on the alarm status,
    #  formatted for the xml output summary.
    ## @param self
    #  The class instance.
    
    def getXmlFormattedSummary(self):
        summary = '<plot name="%s">\n' % self.getRootObjectName() +\
                  '    <alarm function="%s">\n' % self.FunctionName
        for item in self.ParamsDict.items():
            summary += '        <parameter name="%s" value="%s"/>\n' % item
        summary += '        <warning_limits min="%s" max="%s"/>\n' %\
                   (self.Limits.WarningMin, self.Limits.WarningMax) +\
                   '        <error_limits min="%s" max="%s"/>\n' %\
                   (self.Limits.ErrorMin, self.Limits.ErrorMax) +\
                   '        <output>%s</output>\n' % self.getOutputValue() +\
                   '        <status>%s</status>\n' % self.getStatusLabel() +\
                   '    </alarm>\n' +\
                   '</plot>\n'
        return summary
    
    ## @brief Return all the relevant information on the alarm status,
    #  formatted for the html report.
    ## @param self
    #  The class instance.
    
    def getHtmlFormattedStatus(self):
        return '\t\t<td>%s</td>\n' % self.__Function    +\
               '\t\t<td>%s</td>\n' % self.__Status      +\
               '\t\t<td>%s</td>\n' % self.__OutputValue +\
               '\t\t<td>%s</td>\n' % self.getFormattedLimits()

    ## @brief Return all the relevant information on the alarm status,
    #  formatted for the LaTeX report.
    ## @param self
    #  The class instance.

    def getLatexFormattedStatus(self):
        return '%s & %s & %s & %s \\\\\n' % (self.__Function, self.__Status,\
                                             self.__OutputValue            ,\
                                             self.getFormattedLimits())

    def __str__(self):
        return self.getTxtFormattedSummary()
