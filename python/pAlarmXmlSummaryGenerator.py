
from pXmlWriter import pXmlWriter


class pAlarmXmlSummaryGenerator(pXmlWriter):

    def __init__(self, alarmHandler):
        self.AlarmHandler = alarmHandler
        pXmlWriter.__init__(self, self.AlarmHandler.XmlSummaryFilePath)

    def run(self):
        self.openTag('alarmSummary')
        for alarm in self.AlarmHandler.XmlParser.getEnabledAlarms():
            self.openTag('plot', {'name': alarm.RootObject.GetName()})
            self.indent()
            self.openTag('alarm', {'function': alarm.FunctionName})
            self.indent()
            for (key, value) in alarm.ParamsDict.items():
                self.writeTag('parameter', {'name': key, 'value': value})
            self.writeTag('warning_limits', {'min': alarm.Limits.WarningMin,\
                                             'max': alarm.Limits.WarningMax})
            self.writeTag('error_limits', {'min': alarm.Limits.ErrorMin,\
                                           'max': alarm.Limits.ErrorMax})
            self.writeTag('output', {}, alarm.getValue())
            self.writeTag('status', {}, alarm.getStatus())
            self.backup()
            self.closeTag('alarm')
            self.backup()
            self.closeTag('plot')
        self.closeTag('alarmSummary')
        self.closeFile()


    
