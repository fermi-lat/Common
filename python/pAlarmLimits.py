## @package pAlarmLimits
## @brief Module for the definition of alarm limits.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmLimits')

import pUtils

WARNING_BADNESS = 1.0
ERROR_BADNESS   = 2.0
DELTA_BADNESS   = ERROR_BADNESS - WARNING_BADNESS

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
    #  values are consistent and that the warning margins are smnaller than
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

    ## @brief Return the badness of a given number (possibly with its error).
    #
    #  The "badness" is the basic measure for determining the status of an
    #  alarm; it is a function that is equal to the value of WARNING_BADNESS
    #  on the warning limits and is equal to the value of ERROR_BADNESS in
    #  correspondence of the error limits.
    #
    #  It is essentially calculated according to the following steps:
    #  - the average of the warning limits (center) is calculated;
    #  - the best value (the one that best fits into the limits, once the
    #  associated error is taken into account is calculated). If the error bar
    #  does *not* cross the center, than the best value is the actual value
    #  plus or minus the error (possibly multiplicated by a constant), depending
    #  on whether the value itself lieas above or below the center. If the
    #  error bar *does* cross the center, then the best value is assumed to
    #  be the center itself.
    #  - the badness (i.e. the function defined above) is calculated on
    #  the best value.

    def getBadness(self, value, error = 0.0, numSigma = 1.0):
        error = error*numSigma
        center = (self.WarningMin + self.WarningMax)/2.0
        if (value - error) >= center:
            bestValue = value - error
        elif (value + error) <= center:
            bestValue = value + error
        else:
            bestValue = center
        if (bestValue >= self.WarningMin) and (bestValue <= self.WarningMax):
            badness = WARNING_BADNESS*abs(bestValue - center)/\
                (self.WarningMax - center)
        elif bestValue < self.WarningMin:
            badness = WARNING_BADNESS + DELTA_BADNESS*\
                (self.WarningMin - bestValue)/(self.WarningMin - self.ErrorMin)
        else:
            badness = WARNING_BADNESS + DELTA_BADNESS*\
                (bestValue - self.WarningMax)/(self.ErrorMax - self.WarningMax)
        return badness

    ## @brief Return a formatted representation of the limits.
    ## @param self
    #  The class instance.

    def getSummary(self):
        return '[%s / %s --- %s / %s]'% (pUtils.formatNumber(self.ErrorMin),\
                                         pUtils.formatNumber(self.WarningMin),\
                                         pUtils.formatNumber(self.WarningMax),\
                                         pUtils.formatNumber(self.ErrorMax))

    ## @brief Class representation.
    ## @param self
    #  The class instance.
    
    def __str__(self):
        return self.getSummary()


if __name__ == '__main__':
    import ROOT
    limits = pAlarmLimits(200, 300, 100, 400)
    print limits
    graph = ROOT.TGraph()
    i = 0
    for value in range(0, 501, 10):
        graph.SetPoint(i, value, limits.getBadness(value, 10))
        i += 1
    graph.Draw('ALP')
