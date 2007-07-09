
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
        self.Limits       = limits
        self.Value        = None
        self.Status       = STATUS_UNDEFINED
        self.DetailedDict = {}

    def setValue(self, value):
        self.Value = value
        self.__processValue()

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

    def getStatusLevel(self):
        return self.Status['level']

    def getStatusLabel(self):
        return self.Status['label']

    def isClean(self):
        return (self.Status == STATUS_CLEAN) 

    def setStatus(self, status):
        self.Status = status

    def getDictValue(self, key):
        try:
            return self.DetailedDict[key]
        except KeyError:
            logger.warn('Unknown key (%s) in the alarm output dict.' % key)
            return None

    def setDictValue(self, key, value):
        self.DetailedDict[key] = value

    def incrementDictValue(self, key, amount = 1):
        self.DetailedDict[key] += amount

    def appendDictValue(self, key, value):
        try:
            self.DetailedDict[key].append(value)
        except KeyError:
            self.DetailedDict[key] = [value]

    def getDictTextSummary(self):
        summary = 'Optional output dictionary following...\n'
        if self.DetailedDict == {}:
            summary += 'Empty\n'
        else:
            for (key, value) in self.DetailedDict.items():
                summary += '%s: %s\n' % (pUtils.expandString(key, 20), value)
        return summary

    def getTextSummary(self):
        return '** Alarm output summary **\n'                      +\
               'Output value: %s\n' % self.Value                   +\
               'Limits:     : %s\n' % self.Limits.getTextSummary() +\
               'Status      : %s\n' % self.Status                  +\
               self.getDictTextSummary()

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
