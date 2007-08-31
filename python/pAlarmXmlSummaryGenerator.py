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

    ## @brief Evaluation of alarm statistics to be written
    #  at the beginning of the output .xml file
    ## @param self
    #  The class instance.

    def evalStatistics(self):
        StatDict = {"error"     : 0,
                    "warning"    : 0,
                    "clean"     : 0,
                    "undefined" : 0}
        for alarm in self.AlarmHandler.XmlParser.getEnabledAlarms():
            StatDict[alarm.getStatus().lower()] +=1
        return StatDict

    ## @brief Implementation of the summary generation.
    ## @param self
    #  The class instance.
    
    def run(self):
        self.openTag('alarmStatistics', self.evalStatistics(), close=True)
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


    
