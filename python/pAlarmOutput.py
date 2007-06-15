
import logging

import pUtils
import pAlarm

class pAlarmOutput:

    def __init__(self, limits):
        self.__Limits = limits
        self.__Value  = None
        self.__Status = pAlarm.UNDEFINED_STATUS
        self.__Dict   = {}

    def getValue(self):
        return self.__OutputValue

    def setValue(self, value):
        self.__Value = value
        self.processValue()

    def processValue(self):
        if self.__Value is None:
	    self.__Status = pAlarm.UNDEFINED_STATUS
        elif (self.__Value > self.__Limits.WarningMin)\
                 and (self.__Value < self.__Limits.WarningMax):
            self.__Status = pAlarm.CLEAN_STATUS
        elif (self.__Value < self.__Limits.ErrorMin)\
                 or (self.__Value > self.__Limits.ErrorMax):	
            self.__Status = pAlarm.ERROR_STATUS
        else:
            self.__Status = pAlarm.WARNING_STATUS

    def getStatus(self):
        return self.__Status

    def setStatus(self, status):
        self.__Status = status

    def getDict(self):
        return self.__Dict

    def getDictValue(self, key):
        try:
            return self.__Dict[key]
        except KeyError:
            logging.warn('Unknown key (%s) in the alarm output dict.' % key)
            return None

    def setDictValue(self, key, value):
        self.__Dict[key] = value

    def appendDictValue(self, key, value):
        try:
            self.__Dict[key].append(value)
        except KeyError:
            self.__Dict[key] = [value]

    def getDictTextSummary(self):
        summary = 'Optional output dictionary following...\n'
        if self.__Dict == {}:
            summary += 'Empty\n'
        else:
            for (key, value) in self.__Dict.items():
                summary += '%s: %s\n' % (pUtils.expandString(key, 20), value)
        return summary

    def getTextSummary(self):
        return '** Alarm output summary **\n'                        +\
               'Output value: %s\n' % self.__Value                   +\
               'Limits:     : %s\n' % self.__Limits.getTextSummary() +\
               'Status      : %s\n' % self.__Status                  +\
               self.getDictTextSummary()

    def getXmlSummary(self):
        pass

    def getDoxygenSummary(self):
        pass

    def __str__(self):
        return self.getTextSummary()
    

if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(1, 2, 0, 3)
    output = pAlarmOutput(limits)
    output.setDictValue('How is it going?', 'Not too bad...')
    output.appendDictValue('A list', 9)
    output.appendDictValue('A list', 'test')
    output.setValue(2.3)
    print output
    output = pAlarmOutput(limits)
    output.setValue(3.5)
    print output
    output = pAlarmOutput(limits)
    output.setValue(1.5)
    print output
    output = pAlarmOutput(limits)
    print output
