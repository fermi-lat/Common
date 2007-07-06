
import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmOutput')

import pUtils
import pAlarm


STATUS_CLEAN     = {'level': 1, 'label': 'CLEAN'}
STATUS_WARNING   = {'level': 2, 'label': 'WARNING'}
STATUS_ERROR     = {'level': 3, 'label': 'ERROR'}
STATUS_UNDEFINED = {'level': 4, 'label': 'UNDEFINED'}


class pAlarmOutput:

    def __init__(self, limits):
        self.__Limits = limits
        self.__Value  = None
        self.__Status = STATUS_UNDEFINED
        self.__Dict   = {}

    def getValue(self):
        return self.__Value

    def setValue(self, value):
        self.__Value = value
        self.__processValue()

    def __processValue(self):
        if self.__Value is None:
	    self.__Status = STATUS_UNDEFINED
        elif (self.__Value > self.__Limits.WarningMin)\
                 and (self.__Value < self.__Limits.WarningMax):
            self.__Status = STATUS_CLEAN
        elif (self.__Value < self.__Limits.ErrorMin)\
                 or (self.__Value > self.__Limits.ErrorMax):	
            self.__Status = STATUS_ERROR
        else:
            self.__Status = STATUS_WARNING

    def getStatus(self):
        return self.__Status

    def getStatusLevel(self):
        return self.getStatus()['level']

    def getStatusLabel(self):
        return self.getStatus()['label']

    def isClean(self):
        return (self.getStatus() == STATUS_CLEAN) 

    def setStatus(self, status):
        self.__Status = status

    def getDict(self):
        return self.__Dict

    def getDictValue(self, key):
        try:
            return self.__Dict[key]
        except KeyError:
            logger.warn('Unknown key (%s) in the alarm output dict.' % key)
            return None

    def setDictValue(self, key, value):
        self.__Dict[key] = value

    def incrementDictValue(self, key, amount = 1):
        self.__Dict[key] += amount

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
