
## @package pAlarm
## @brief Description of an alarm.

import sys
import logging

import pUtils
import pAlarmAlgorithms

from pXmlBaseElement import pXmlBaseElement

UNDEFINED_STATUS = 'UNDEFINED'
CLEAN_STATUS     = 'CLEAN'
WARNING_STATUS   = 'WARNING'
ERROR_STATUS     = 'ERROR'
ALARM_HEADER     = 'Function      Status  Parameter Limits'

## @brief Class describing an alarm to be activated on a plot.
#
#  The basic idea, here, is that the alarm must verify whether a simple
#  plot parameter (average value or RMS of a histogram, etc., depending
#  on the alarm Function) lies or not within a specified interval.

class pAlarm(pXmlBaseElement):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element from which the alarm is constructed.
    ## @param plot
    #  The ROOT object the alarm is set on.
    
    def __init__(self, element, plot):

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
 
        pXmlBaseElement.__init__(self, element)
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
                           xmlElement.getAttribute('value')
        return parametersDict

    ## @brief Return True if the alarm Status is CLEAN_STATUS.
    ## @param self
    #  The class instance.

    def isClean(self):
        return (self.__Status == CLEAN_STATUS)

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

    ## @brief Return the Min, Max pair formatted to be printed on the screen.
    ## @param self
    #  The class instance.

    def getFormattedLimits(self):
        return '[%s, %s]' % (self.__WarningMin, self.__WarningMax)

    ## @brief Return all the relevant information on the alarm status,
    #  nicely formatted.
    ## @param self
    #  The class instance.

    def getFormattedStatus(self):
        return '%s%s%s%s' % (pUtils.expandString(self.__Function)      ,\
                             pUtils.expandString(self.__Status, 10)    ,\
                             pUtils.expandNumber(self.__OutputValue)   ,\
                             pUtils.expandString(self.getFormattedLimits(),15))

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
