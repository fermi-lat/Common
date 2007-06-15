

class pAlarmLimits:

    def __init__(self, warningMin, warningMax, errorMin, errorMax):
        self.WarningMin = warningMin
        self.WarningMax = warningMax
        self.ErrorMin   = errorMin
        self.ErrorMax   = errorMax
        self.__validate()

    def __validate(self):
        if self.WarningMin > self.WarningMax:
            logging.error('Warning min higher than warning max.')
        if self.ErrorMin > self.ErrorMax:
            logging.error('Error min higher than error max.')
        if self.WarningMin < self.ErrorMin:
            logging.error('Warning min lower than error min.')
        if self.WarningMax > self.ErrorMax:
            logging.error('Warning max is higher than error max.')

    def getTextSummary(self):
        return '[%s/%s; %s/%s]' % (self.ErrorMin, self.WarningMin,
                                   self.WarningMax, self.ErrorMax)

    def __str__(self):
        return self.getTextSummary()


if __name__ == '__main__':
    limits = pAlarmLimits(1, 2, 0, 3)
    print limits
