## @package pAlarmOutput
## @brief Module describing the output of an alarm.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmOutput')

import pUtils
import pAlarm

from pAlarmLimits import WARNING_BADNESS, ERROR_BADNESS

STATUS_CLEAN     = 0x0
STATUS_UNDEFINED = 0x1
STATUS_WARNING   = 0x2
STATUS_ERROR     = 0x4

STATUS_DICT = {STATUS_CLEAN    : 'CLEAN',
               STATUS_UNDEFINED: 'UNDEFINED',
               STATUS_WARNING  : 'WARNING',
               STATUS_ERROR    : 'ERROR'
               }

MAX_DETAIL_SIZE  = 1500

## @brief Class describing the output of an alarm.
#
#  The output of an alarm consists of three main pieces:
#  @li an output value returned by a given algorithm.
#  @li a status resulting from the comparison of the value with the limits.
#  @li a detailed dictionary wich can be filled with arbitrary information
#  while the alarm algorithm is run on the ROOT object.
#
#  This class is responsible for checking the output value provided by
#  an algorithm against the alarm limits. This happens whenever the
#  setValue() method is called.

class pAlarmOutput:
    
    def __init__(self, limits, parent = None):
        self.Limits       = limits
        self.Parent       = parent
        self.Value        = None
        self.Error        = None
        self.Label        = None
        self.Status       = STATUS_UNDEFINED
        self.DetailedDict = {}

    def getStatusAsText(self):
        return STATUS_DICT[self.Status]

    def isUndefined(self):
        return self.Status == STATUS_UNDEFINED

    def isClean(self):
        return self.Status == STATUS_CLEAN

    def isWarning(self):
        return self.Status == STATUS_WARNING

    def isError(self):
        return self.Status == STATUS_ERROR

    def getStatus(self, badness):
        if badness <= WARNING_BADNESS:
            return STATUS_CLEAN
        elif badness <= ERROR_BADNESS:
            return STATUS_WARNING
        else:
            return STATUS_ERROR

    def setValue(self, value, error = None, badness = None):
        self.Value = value
        self.Error = error
        if badness is None:
            badness = self.Limits.getBadness(value, error)
        self.Status = self.getStatus(badness)
        self.compress()

    ## @brief Get the value corresponding to a particular key of the
    #  detailed dictionary.
    ## @param self
    #  The class instance.
    ## @param key
    #  The dictionary key.

    def getDictValue(self, key):
        return self.DetailedDict[key]

    ## @brief Set the value corresponding to a particular key of the
    #  detailed dictionary.
    ## @param self
    #  The class instance.
    ## @param key
    #  The dictionary key.
    ## @param value
    #  The dictionary value.

    def setDictValue(self, key, value):
        self.DetailedDict[key] = value

    ## @brief Increment the value corresponding to a particular key of the
    #  detailed dictionary by a specific amount.
    ## @param self
    #  The class instance.
    ## @param key
    #  The dictionary key.
    ## @param amount
    #  The amount.

    def incrementDictValue(self, key, amount = 1):
        try:
            self.DetailedDict[key] += amount
        except KeyError:
            self.DetailedDict[key] = amount

    ## @brief Append an element to a specific key of the detailed dictionary.
    ## @param self
    #  The class instance.
    ## @param key
    #  The dictionary key.
    ## @param value
    #  The value to append.

    def appendDictValue(self, key, value):
        try:
            self.DetailedDict[key].append(value)
        except KeyError:
            self.DetailedDict[key] = [value]

    ## @brief Return the output value, nicely formatted as a string.
    ## @param self
    #  The class instance. 

    def getFormattedValue(self):
        value = pUtils.formatNumber(self.Value)
        if self.Error is None:
            return value
        try:
            numDecimalPlaces = len(value.split('.')[1])
        except:
            numDecimalPlaces = 0
        formatString = '%' + '.%df' % numDecimalPlaces
        error = formatString % self.Error
        return '%s +- %s' % (value, error)

    ## @brief Compress the output detailed dictionary in order to avoid too
    #  much verbosity in the output xml file.
    ## @param self
    #  The class instance. 

    def compress(self):
        for (key, value) in self.DetailedDict.items():
            if len(str(value)) > MAX_DETAIL_SIZE:
                self.DetailedDict[key] = '%s... too much garbage following]' %\
                    str(value)[:MAX_DETAIL_SIZE]

    ## @brief Return a string representation of the alarm output.
    ## @param self
    #  The class instance.
            
    def getTextSummary(self):
        summary = ''
        summary += 'Limits  : %s\n' % self.Limits
        summary += 'Output  : %s (%s)\n' %\
            (self.getFormattedValue(), self.Label)
        summary += 'Status  : %s\n' % self.getStatusAsText()
        summary += 'Details : %s\n' % self.DetailedDict
        return summary

    ## @brief Class representation.
    ## @param self
    #  The class instance.    

    def __str__(self):
        return self.getTextSummary()

    
if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-1, 3, -1, 6)
    output = pAlarmOutput(limits)
    output.Label = 'Some explanation...'
    print output
    output.setValue(100, 10)
    print output
    output.setValue(100.863287651487, 10.763175)
    print output
    output.setValue(4.5)
    print output
    output.setValue(4.5, 2)
    print output
    output.setValue(4.5, 20)
    print output
