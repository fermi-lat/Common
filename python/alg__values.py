
import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


class alg__values(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TBranch']
    SUPPORTED_PARAMETERS = []

    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)
        self.RootTree = self.RootObject.GetTree()

    def getBranchContent(self, entry):
        self.RootObject.GetEntry(entry)
        return eval('self.RootTree.%s' % self.RootObject.GetName())

    def run(self):
        self.Output.setDictValue('num_warning_points', 0)
        self.Output.setDictValue('num_error_points'  , 0)
        self.Output.setDictValue('warning_points', [])
        self.Output.setDictValue('error_points'  , [])
        for entry in range(self.RootObject.GetEntries()):
            value = self.getBranchContent(entry)
            if value < self.getErrorMin() or value > self.getErrorMax():
                point = (entry, value)
                self.Output.incrementDictValue('num_error_points')
                self.Output.appendDictValue('error_points', point)
            elif value < self.getWarningMin() or value > self.getWarningMax():
                point = (entry, value)
                self.Output.incrementDictValue('num_warning_points')
                self.Output.appendDictValue('warning_points', point)
            if self.Output.getDictValue('num_error_points'):
                self.Output.setValue(self.Output.getDictValue('error_points')[0][1])
            elif self.Output.getDictValue('num_warning_points'):
                self.Output.setValue(self.Output.getDictValue('warning_points')[0][1])
            else:
                entry = self.RootObject.GetEntries()/2
                self.Output.setValue(self.RootObject.GetBranchContent(entry))
                

if __name__ == '__main__':
    pass
    #from pAlarmLimits import pAlarmLimits
    #limits = pAlarmLimits(4, 16, 2, 24)
    #histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    #histogram.FillRandom('pol0', 1000)
    #algorithm = alg__y_values(limits, histogram)
    #algorithm.apply()
    #print algorithm.Output
