
import logging


class pAlarmLimits:

    def __init__(self, warningMin, warningMax, errorMin, errorMax):
        self.WarningMin = warningMin
        self.WarningMax = warningMax
        self.ErrorMin   = errorMin
        self.ErrorMax   = errorMax
        self.__validate()

    def __validate(self):
        if self.WarningMin > self.WarningMax:
            logging.error('Warning min (%s) higher than warning max (%s).'  %\
                          (self.WarningMin, self.WarningMax))
        if self.ErrorMin > self.ErrorMax:
            logging.error('Error min (%s) higher than error max (%s).'      %\
                          (self.ErrorMin, self.ErrorMax))
        if self.WarningMin < self.ErrorMin:
            logging.error('Warning min (%s) lower than error min (%s).'     %\
                          (self.WarningMin, self.ErrorMin))
        if self.WarningMax > self.ErrorMax:
            logging.error('Warning max (%s) is higher than error max (%s).' %\
                          (self.WarningMax, self.ErrorMax))

    def getTextSummary(self):
        return '[%s/%s; %s/%s]' % (self.ErrorMin, self.WarningMin,
                                   self.WarningMax, self.ErrorMax)

    def __str__(self):
        return self.getTextSummary()


if __name__ == '__main__':
    limits = pAlarmLimits(1, 2, 0, 3)
    print limits
