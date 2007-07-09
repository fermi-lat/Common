## @package pAlarmLimits
## @brief Module for the definition of alarm limits.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmLimits')


## @brief Class describing alarm limits.
#
#  There are two different levels of limits: WARNING and ERROR.

class pAlarmLimits:

    ## @brief Basic constructor.
    ## @param self
    #  The class instance.
    ## @param warningMin
    #  The minimum value under which a warning is issued.
    ## @param warningMax
    #  The maximum value over which a warning is issued.
    ## @param errorMin
    #  The minimum value under which an error is issued.
    ## @param errorMax
    #  The maximum value over which an error is issued.

    def __init__(self, warningMin, warningMax, errorMin, errorMax):

        ## @var WarningMin
        ## @brief The minimum value under which a warning is issued.

        ## @var WarningMax
        ## @brief The maximum value over which a warning is issued.

        ## @var ErrorMin
        ## @brief The minimum value under which an error is issued.

        ## @var ErrorMax
        ## @brief The maximum value over which an error is issued.
        
        self.WarningMin = warningMin
        self.WarningMax = warningMax
        self.ErrorMin   = errorMin
        self.ErrorMax   = errorMax
        self.__validate()

    ## @brief Validate the limits (i.e. make sure that the min and max
    # values are consistent and that the warning margins are smnaller than
    #  the error margins.)
    ## @param self
    #  The class instance.
        
    def __validate(self):
        if self.WarningMin > self.WarningMax:
            logger.error('Warning min (%s) higher than warning max (%s).'  %\
                          (self.WarningMin, self.WarningMax))
        if self.ErrorMin > self.ErrorMax:
            logger.error('Error min (%s) higher than error max (%s).'      %\
                          (self.ErrorMin, self.ErrorMax))
        if self.WarningMin < self.ErrorMin:
            logger.error('Warning min (%s) lower than error min (%s).'     %\
                          (self.WarningMin, self.ErrorMin))
        if self.WarningMax > self.ErrorMax:
            logger.error('Warning max (%s) is higher than error max (%s).' %\
                          (self.WarningMax, self.ErrorMax))

    ## @brief Return a formatted representation of the limits.
    ## @param self
    #  The class instance.

    def getTextRep(self):
        return '[%s / %s --- %s / %s]' % (self.ErrorMin, self.WarningMin,
                                          self.WarningMax, self.ErrorMax)

    ## @brief Class representation.
    ## @param self
    #  The class instance.
    
    def __str__(self):
        return self.getTextRep()


if __name__ == '__main__':
    limits = pAlarmLimits(1, 2, 0, 3)
    print limits
