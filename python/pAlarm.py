
## @package pAlarm
## @brief Description of an alarm.

import sys
import logging

import pUtils
import pAlarmAlgorithms

from pXmlBaseElement import pXmlBaseElement

UNDEFINED_STATUS     = 'UNDEFINED'
CLEAN_STATUS         = 'CLEAN'
WARNING_STATUS       = 'WARNING'
ERROR_STATUS         = 'ERROR'
LEVELS_DICT          = {UNDEFINED_STATUS: 4,
                        CLEAN_STATUS    : 1,
                        WARNING_STATUS  : 2,
                        ERROR_STATUS    : 3
                        }
SUMMARY_COLUMNS_DICT = {'Plot name': 25,
                        'Function' : 10,
                        'Status'   : 7 ,
                        'Output'   : 6 ,
                        'Limits'   : 20
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
    
    def __init__(self, domElement, plot):

        ## @var __Plot
        ## @brief The ROOT object the alarm is set on.

        ## @var __Function
        ## @brief The type of the alarm (i.e. the specific algorithm).

        ## @var __WarningMin
        ## @brief The lower bound for the warning.

        ## @var __WarningMax
        ## @brief The higher bound for the warning.

        ## @var __ErrorMin
        ## @brief The lower bound for the error.

        ## @var __ErrorMax
        ## @brief The higher bound for the error.

        ## @var __OutputValue
        ## @brief The output value given by the algorithm implementing the
        #  alarm.

        ## @var __Status
        ## @brief The alarm status.
        #
        #  Set to undefined at the beginning; after the alarm has been
        #  activated it is either clean or warning or error.

        ## @var __ParamsDict
        ## @brief Dictionary of optional parameters to be passed to the
        #  algorithm implementing the alarm.
 
        pXmlBaseElement.__init__(self, domElement)
	self.__Plot        = plot
        self.__Function    = self.getAttribute('function')
     	(self.__WarningMin, self.__WarningMax) = self.__getLimits('warning')
	(self.__ErrorMin  , self.__ErrorMax  ) = self.__getLimits('error')
        self.__OutputValue = None
        self.__Status      = UNDEFINED_STATUS
	self.__ParamsDict  = self.__getParametersDict()
        self.__validateLimits()

    ## @brief Make sure that the warning/error limits are set consistently
    #  (i.e. the warning min is higher than the error min etc...).
    ## @param self
    #  The class instance.    

    def __validateLimits(self):
        if self.__WarningMin > self.__WarningMax:
            logging.error('Warning min is higher than warning max ' +\
                         'for function %s.' % self.__Function)
            sys.exit('Check the xml config file. Aborting...')
        if self.__ErrorMin > self.__ErrorMax:
            logging.error('Error min is higher than error max ' +\
                         'for function %s.' % self.__Function)
            sys.exit('Check the xml config file. Aborting...')        
        if self.__WarningMin < self.__ErrorMin:
            logging.warn('Warning min is lower than error min ' +\
                         'for function %s.' % self.__Function)
            self.__ErrorMin = self.__WarningMin
            logging.warn('Error min set to %s' % self.__WarningMin)
        if self.__WarningMax > self.__ErrorMax:
            logging.warn('Warning max is higher than error max ' +\
                         'for function %s.' % self.__Function)
            self.__ErrorMax = self.__WarningMax
            logging.warn('Error min set to %s' % self.__WarningMax)
        
    ## @brief Return a pXmlBaseElement object containg the
    #  (either warning or error) limits for the alarm.
    ## @param self
    #  The class instance.
    ## @param type
    #  The type of the limits (either warning or error).

    def __getLimits(self, type):
        limits = pXmlBaseElement(self.getElementByTagName('%s_limits' % type))
        return (limits.evalAttribute('min'), limits.evalAttribute('max'))

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

    ## @brief Return True if the alarm Status is CLEAN_STATUS.
    ## @param self
    #  The class instance.

    def isClean(self):
        return (self.__Status == CLEAN_STATUS)

    ## @brief Return the alarm level correspnding to its status.
    #
    #  Used while printing on the terinal.
    ## @param self
    #  The class instance.

    def getLevel(self):
        return LEVELS_DICT[self.__Status]

    ## @brief Activate the alarm (i.e. actually verify the plot).
    ## @param self
    #  The class instance.

    def activate(self):
        if self.__Function in dir(pAlarmAlgorithms):
            self.__OutputValue = eval(\
                ('pAlarmAlgorithms.%s' % self.__Function)+\
                '(self._pAlarm__Plot, self._pAlarm__ParamsDict)')
	    self.__checkStatus()
        else:
            logging.error('Function %s() not implemented in the alarms.' %\
                          self.__Function)

    ## @brief Check the status of the alarm after it has been activated.
    ## @param self
    #  The class instance.    

    def __checkStatus(self):
        if self.__OutputValue is None:
	    self.__Status = UNDEFINED_STATUS
        elif (self.__OutputValue > self.__WarningMin)\
                 and (self.__OutputValue < self.__WarningMax):
            self.__Status = CLEAN_STATUS
        elif (self.__OutputValue < self.__ErrorMin)\
                 or (self.__OutputValue > self.__ErrorMax):	
            self.__Status = ERROR_STATUS
        else:
            self.__Status = WARNING_STATUS

    ## @brief Return the name of the plot the alarm is set on.
    ## @param self
    #  The class instance.            

    def getPlotName(self):
        return self.__Plot.GetName()

    ## @brief Return the plot name, formatted to be printed on the terminal.
    ## @param self
    #  The class instance.      

    def getTxtFormattedPlotName(self):
        return pUtils.expandString(self.getPlotName(),\
                                   SUMMARY_COLUMNS_DICT['Plot name'])

    ## @brief Return the alarm function, formatted to be printed on the
    #  terminal.
    ## @param self
    #  The class instance.

    def getTxtFormattedFunction(self):
        return pUtils.expandString(self.__Function,\
                                   SUMMARY_COLUMNS_DICT['Function'])

    ## @brief Return the alarm status, formatted to be printed on the
    #  terminal.
    ## @param self
    #  The class instance.

    def getTxtFormattedStatus(self):
        return pUtils.expandString(self.__Status,\
                                   SUMMARY_COLUMNS_DICT['Status'])

    ## @brief Return the output value of the alarm, formatted to be printed
    #  on the terminal.
    ## @param self
    #  The class instance.

    def getTxtFormattedOutputValue(self):
        return pUtils.expandNumber(self.__OutputValue,\
                                   SUMMARY_COLUMNS_DICT['Output'])

    ## @brief Return the alarm limits, formatted to be printed on the terminal.
    ## @param self
    #  The class instance.

    def getTxtFormattedLimits(self):
        limits = '[%s/%s, %s/%s]' % (self.__ErrorMin, self.__WarningMin,\
                                     self.__WarningMax, self.__ErrorMax)
        return pUtils.expandString(limits,\
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

    ## @brief Return all the relevant information on the alarm status,
    #  formatted for the xml output summary.
    ## @param self
    #  The class instance.
    
    def getXmlFormattedSummary(self):
        summary = '<plot name="%s">\n' % self.getPlotName() +\
                  '    <alarm function="%s">\n' % self.__Function
        for item in self.__ParamsDict.items():
            summary += '        <parameter name="%s" value="%s"/>\n' % item
        summary += '        <warning_limits min="%s" max="%s"/>\n' %\
                   (self.__WarningMin, self.__WarningMax) +\
                   '        <error_limits min="%s" max="%s"/>\n' %\
                   (self.__ErrorMin, self.__ErrorMax) +\
                   '        <output>%s</output>\n' % self.__OutputValue +\
                   '        <status>%s</status>\n' % self.__Status.lower() +\
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
