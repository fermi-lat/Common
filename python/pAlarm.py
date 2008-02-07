## @package pAlarm
## @brief Module describing an alarm.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarm')

import sys
import re
import pUtils

from pXmlBaseElement import pXmlBaseElement
from pAlarmLimits import pAlarmLimits



## @brief Class describing an alarm to be activated on a plot.

class pAlarm(pXmlBaseElement):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param domElement
    #  The xml element from which the alarm is constructed.
    ## @param rootObject
    #  The ROOT object the alarm is set on.
    
    def __init__(self, domElement, rootObject):

        ## @var RootObject
        ## @brief The ROOT object the alarm is set on.

        ## @var Limits
        ## @brief The alarm (both error and warning limits).
        #
        #  It's a pAlarmLimits object.

        ## @var ParamsDict
        ## @brief Dictionary of optional parameters to be passed to the
        #  algorithm implementing the alarm.

        ## @var FunctionName
        ## @brief The name of the specific algorithm that the alarm is
        #  supposed to apply.

        ## @var Algorithm
        ## @brief The actual algorithm the alarm is applying. 
 
        pXmlBaseElement.__init__(self, domElement)
	self.RootObject = rootObject
        self.PlotName = self.RootObject.GetName()
        self.Limits = self.__extractLimits()
	self.ParamsDict = self.__extractParametersDict()
	self.ConditionsDict = self.__extractConditionsDict()
        self.FunctionName = self.getAttribute('function')
        try:
            exec('from alg__%s import alg__%s' % (self.FunctionName,\
                                                  self.FunctionName))
            self.Algorithm = eval('alg__%s(self.Limits, self.RootObject, self.ParamsDict, self.ConditionsDict)' % self.FunctionName)
        except ImportError:
            logger.error('Could not import alg__%s. ' % self.FunctionName +\
                          'The alarm will be ignored.')
            self.Algorithm = None

    def __cmp__(self, other):
        if self.PlotName > other.PlotName:
            return 1
        return -1
        
    ## @brief Extract the limits from the underlying dom element.
    ## @param self
    #  The class instance.

    def __extractLimits(self):
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

    ## @brief Extract the dictionary of parameters from the underlying
    #  dom element.
    ## @param self
    #  The class instance.

    def __extractParametersDict(self):
        parametersDict = {}
        for domElement in self.getElementsByTagName('parameter'):
            xmlElement = pXmlBaseElement(domElement)
            parametersDict[xmlElement.getAttribute('name')] =\
                xmlElement.evalAttribute('value')
        return parametersDict

    def __extractConditionsDict(self):
        conditionsDict = {}
        for domElement in self.getElementsByTagName('condition'):
            xmlElement = pXmlBaseElement(domElement)
            conditionsDict[xmlElement.getAttribute('name')] =\
                xmlElement.evalAttribute('value')
        return conditionsDict

    ## @brief Return the status label (i.e. CLEAN, WARNING, ERROR, UNDEFINED)
    #  of the algorithm output.
    ## @param self
    #  The class instance.

    def getOutputStatus(self):
        return self.Algorithm.Output.Status['label']

    def isClean(self):
        return self.Algorithm.Output.isClean()

    ## @brief Return the output value of the algorithm.
    ## @param self
    #  The class instance.

    def getOutputValue(self):
        return self.Algorithm.Output.Value

    def getFormattedOutputValue(self):
        return self.Algorithm.Output.getFormattedValue()

    def getOutputLabel(self):
        return self.Algorithm.Output.Label

    def getOutputDetails(self):
        return self.Algorithm.Output.DetailedDict
    
    ## @brief Return a formatted representation of the alarm limits.
    ## @param self
    #  The class instance.

    def getLimits(self):
        return self.Limits.getSummary()
    
    ## @brief Activate the alarm (i.e. actually verify the plot).
    ## @param self
    #  The class instance.

    def activate(self):
        self.Algorithm.apply()
