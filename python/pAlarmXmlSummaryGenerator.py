## @package pAlarmXmlSummaryGenerator
## @brief Module for generating the alarm handler xml summary.

from pXmlWriter import pXmlWriter


## @brief Class implementing the xml summary generation for the
#  alarm handler.

class pAlarmXmlSummaryGenerator(pXmlWriter):

    ## @brief Basic constructor.
    ## @param self
    #  The class instance.
    ## @param alarmHandler
    #  The parent alarm handler.

    def __init__(self, alarmHandler):

        ## @var AlarmHandler
        ## @brief The parent alarm handler.
        
        self.AlarmHandler = alarmHandler
        pXmlWriter.__init__(self, self.AlarmHandler.XmlSummaryFilePath)

    ## @brief Implementation of the summary generation.
    ## @param self
    #  The class instance.
    
    def run(self):
        self.openTag('alarmSummary')
        self.openTag('alarmStatistics', self.AlarmHandler.AlarmStats,\
                     close = True)
        for alarm in self.AlarmHandler.XmlParser.getEnabledAlarms():
            self.openTag('plot', {'name': alarm.getPlotName()})
            self.indent()
            self.openTag('alarm', {'function': alarm.FunctionName})
            self.indent()
            if alarm.FunctionName == 'values':
                linksDict = alarm.Algorithm.LinksDict
                if len(linksDict) > 0:
                    self.openTag('link_arguments')
                    self.indent()
                    for (key, value) in linksDict.items():
                        value = str(value)
                        value = value.strip('[').strip(']').replace(' ', '')
                        value = '%s=%s' % (key, value)
                        self.writeTag('link_argument', {}, value)
                    self.backup()
                    self.closeTag('link_arguments')
            for (key, value) in alarm.ParamsDict.items():
                self.writeTag('parameter', {'name': key, 'value': value})
            for (key, value) in alarm.ConditionsDict.items():
                self.writeTag('condition', {'name': key, 'value': value})
            self.writeTag('warning_limits', {'min': alarm.Limits.WarningMin,\
                                             'max': alarm.Limits.WarningMax})
            self.writeTag('error_limits', {'min': alarm.Limits.ErrorMin,\
                                           'max': alarm.Limits.ErrorMax})
            self.writeTag('severity', {}, alarm.Severity)
            self.writeTag('output', {}, alarm.getFormattedOutputValue())
            self.writeTag('label', {}, alarm.getOutputLabel())
            self.writeTag('status', {}, alarm.getOutputStatus())
            if alarm.Algorithm.hasDetails():
                for (key, value) in alarm.getOutputDetails().items():
                    self.writeTag('detail', {'name': key, 'value': value })
            self.backup()
            self.closeTag('alarm')
            self.backup()
            self.closeTag('plot')
        self.closeTag('alarmSummary')
        self.closeFile()


    
