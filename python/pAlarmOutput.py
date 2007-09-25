## @package pAlarmOutput
## @brief Module describing the output of an alarm.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmOutput')

import pUtils
import pAlarm


STATUS_CLEAN     = {'level': 1, 'label': 'CLEAN'}
STATUS_WARNING   = {'level': 2, 'label': 'WARNING'}
STATUS_ERROR     = {'level': 3, 'label': 'ERROR'}
STATUS_UNDEFINED = {'level': 4, 'label': 'UNDEFINED'}


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

    ## @brief Basic constructor.
    ## @param self
    #  The class instance.
    ## @param limits
    #  The alarm limits.
    
    def __init__(self, limits):

        ## @var Limits
        ## @brief The alarm limits.

        ## @var Value
        ## @brief The algorithm output value.

        ## @var Status
        ## @brief The status label.

        ## @var DetailedDict
        ## @brief The dictionary containing the detailed information.
        
        self.Limits       = limits
        self.Value        = None
        self.Status       = STATUS_UNDEFINED
        self.DetailedDict = {}

    def isClean(self):
        return self.Status['level'] == STATUS_CLEAN['level']

    ## @brief Set the output value and check it against the alarm limits.
    ## @param self
    #  The class instance.
    ## @param value
    #  The output value.
        
    def setValue(self, value):
        self.Value = value
        self.__processValue()

    ## @brief Check the output value against the limits.
    ## @param self
    #  The class instance.
    
    def __processValue(self):
        if self.Value is None:
	    self.Status = STATUS_UNDEFINED
        elif (self.Value > self.Limits.WarningMin)\
                 and (self.Value < self.Limits.WarningMax):
            self.Status = STATUS_CLEAN
        elif (self.Value < self.Limits.ErrorMin)\
                 or (self.Value > self.Limits.ErrorMax):	
            self.Status = STATUS_ERROR
        else:
            self.Status = STATUS_WARNING

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
        self.DetailedDict[key] += amount

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
            

    def getTextSummary(self):
        return 'The algorithm output value is : %s' % self.Value
   ###     return 'The algorithm alarm limits are : %s' % self.Limits

    def __str__(self):
        return self.getTextSummary()

    
if __name__ == '__main__':
    AlarmOutput = pAlarmOutput()
    print AlarmOutput
