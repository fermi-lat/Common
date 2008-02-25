## @package pAlarm
## @brief Module describing an alarm.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarm')

import sys
import re
import pUtils

from pXmlBaseElement import pXmlBaseElement
from pAlarmLimits    import pAlarmLimits
from pGlobals        import MINUS_INFINITY, PLUS_INFINITY, NAN


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

        ## @var ConditionsDict
        ## @brief Dictionary of optional conditions the alarm is subjected to.

        ## @var FunctionName
        ## @brief The name of the specific algorithm that the alarm is
        #  supposed to apply.

        ## @var Algorithm
        ## @brief The actual algorithm the alarm is applying. 
 
        pXmlBaseElement.__init__(self, domElement)
	self.RootObject = rootObject
        self.Limits = self.__extractLimits()
	self.ParamsDict = self.__extractParametersDict()
	self.ConditionsDict = self.__extractConditionsDict()
        self.FunctionName = self.getAttribute('function')
        try:
            exec('from alg__%s import alg__%s' % (self.FunctionName,\
                                                  self.FunctionName))
            self.Algorithm = eval(('alg__%s' % self.FunctionName)       +\
                                      '(self.Limits, self.RootObject, ' +\
                                      'self.ParamsDict, self.ConditionsDict)')
        except ImportError:
            logger.error('Could not import alg__%s. ' % self.FunctionName +\
                          'The alarm will be ignored.')
            self.Algorithm = None

    ## @brief Return the name of the ROOT object the alarm is set on.
    ## @par self
    #  The class instance.

    def getPlotName(self):
        return self.RootObject.GetName()

    ## @brief Comparing method.
    ## @par self
    #  The class instance.
    ## @par other
    #  The other instance---the one to make the comparison against.

    def __cmp__(self, other):
        if self.getPlotName() > other.getPlotName():
            return 1
        return -1
        
    ## @brief Extract the limits from the underlying dom element.
    ## @param self
    #  The class instance.

    def __extractLimits(self):
        warnLims = pXmlBaseElement(self.getElementByTagName('warning_limits'))
        warnMin  = warnLims.evalAttribute('min', MINUS_INFINITY)
        warnMax  = warnLims.evalAttribute('max', PLUS_INFINITY)
        errLims  = pXmlBaseElement(self.getElementByTagName('error_limits'))
        errMin   = errLims.evalAttribute('min', MINUS_INFINITY)
        errMax   = errLims.evalAttribute('max', PLUS_INFINITY)
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
            paramName = xmlElement.getAttribute('name')
            paramValue = xmlElement.evalAttribute('value')
            parametersDict[paramName] = paramValue
        return parametersDict

    ## @brief Extract the dictionary of conditions from the underlying
    #  dom element.
    ## @param self
    #  The class instance.

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

    ## @brief Return whether the alarm output is clean or not.
    ## @param self
    #  The class instance.
    
    def isClean(self):
        return self.Algorithm.Output.isClean()

    ## @brief Return the output value of the algorithm.
    ## @param self
    #  The class instance.

    def getOutputValue(self):
        return self.Algorithm.Output.Value

    ## @brief Return the algorithm output value nicely formatted as a string.
    ## @param self
    #  The class instance.

    def getFormattedOutputValue(self):
        return self.Algorithm.Output.getFormattedValue()

    ## @brief Return the algorithm output label.
    ## @param self
    #  The class instance.

    def getOutputLabel(self):
        return self.Algorithm.Output.Label

    ## @brief Return the alarm algorithm detailed output dictionary.
    ## @param self
    #  The class instance.

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
