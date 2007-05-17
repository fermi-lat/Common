
import logging
import pUtils
import pAlarmAlgorithms

from pXmlElement import pXmlElement

UNDEFINED_STATUS = 'UNDEFINED'
CLEAN_STATUS    = 'CLEAN'
WARNING_STATUS   = 'WARNING'
ERROR_STATUS     = 'ERROR'
ALARM_HEADER     = 'Function      Status  Parameter Limits'

## @brief Class describing an alarm to be activated on a plot.
#
#  The basic idea, here, is that the alarm must verify whether a simple
#  plot parameter (average value or RMS of a histogram,
#  etc., depending on the alarm Function) lies or not within a specified interval.
## @todo Should we support more sophisticated alarms?
## @todo Should we support multiple-level alarms?

class pAlarm(pXmlElement):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element from which the alarm is constructed.
    
    def __init__(self, element, plot):
      
        pXmlElement.__init__(self, element)
	self.Plot         = plot
        self.Function     = self.getAttribute('function')
	warningLimits     = self.getElementsByTagName('warning_limits')[0]
	alarmLimits       = self.getElementsByTagName('error_limits')[0]
     	self.__WarningMin = eval(warningLimits.getAttribute('min'))
	self.__WarningMax = eval(warningLimits.getAttribute('max'))
	self.__ErrorMin   = eval(alarmLimits.getAttribute('min'))
	self.__ErrorMax   = eval(alarmLimits.getAttribute('max'))

	self.Parameters = {}
	for element in self.getElementsByTagName('parameter'):
	    self.Parameters[str(element.getAttribute('name'))] = eval(element.getAttribute('value'))

	self.__Value      = None
        self.Status       = UNDEFINED_STATUS

    ## @brief Return True if the alarm Status is CLEAN_STATUS.
    ## @param self
    #  The class instance.

    def isClean(self):
        return (self.Status == CLEAN_STATUS)

    ## @brief Activate the alarm (i.e. actually verify the plot).
    ## @param self
    #  The class instance.
    ## @param plot
    #  The plot against which the alarm is set.

    def activate(self):
        if self.Function in dir(pAlarmAlgorithms):
            self.__Value = eval('pAlarmAlgorithms.%s(self.Plot, self.Parameters)' % self.Function)
	    self.__checkValue()
        else:
            logging.error('Function %s() not implemented in the alarms.' %\
                          self.Function)


    def __checkValue(self):
        if self.__Value is None:
	    self.Status = UNDEFINED_STATUS
        elif (self.__Value > self.__WarningMin) and (self.__Value < self.__WarningMax):
            self.Status = CLEAN_STATUS
        elif (self.__Value < self.__ErrorMin) or (self.__Value > self.__ErrorMax):	
            self.Status = ERROR_STATUS
        else:
            self.Status = WARNING_STATUS

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
        return '%s%s%s%s' % (pUtils.expandString(self.Function)      ,\
                             pUtils.expandString(self.Status, 10)    ,\
                             pUtils.expandNumber(self.__Value) ,\
                             pUtils.expandString(self.getFormattedLimits(),15))

    ## @brief Return all the relevant information on the alarm status,
    #  formatted for the html report.
    ## @param self
    #  The class instance.
    
    def getHtmlFormattedStatus(self):
        return '\t\t<td>%s</td>\n' % self.Function      +\
               '\t\t<td>%s</td>\n' % self.Status    +\
               '\t\t<td>%s</td>\n' % self.__Value +\
               '\t\t<td>%s</td>\n' % self.getFormattedLimits()

    ## @brief Return all the relevant information on the alarm status,
    #  formatted for the LaTeX report.
    ## @param self
    #  The class instance.

    def getLatexFormattedStatus(self):
        return '%s & %s & %s & %s \\\\\n' % (self.Function, self.Status,\
                                             self.__Value,\
                                             self.getFormattedLimits())
