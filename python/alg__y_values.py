
import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


class alg__y_values(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = []

    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)

    def run(self):
        self.Output.setDictValue('num_warning_points', 0)
        self.Output.setDictValue('num_error_points'  , 0)
        self.Output.setDictValue('warning_points', [])
        self.Output.setDictValue('error_points'  , []) 
        for bin in range(self.RootObject.GetXaxis().GetFirst(),\
                         self.RootObject.GetXaxis().GetLast()+1):
            value = self.RootObject.GetBinContent(bin)
            if value < self.getErrorMin() or value > self.getErrorMax():
                point = (self.RootObject.GetBinCenter(bin), value)
                self.Output.incrementDictValue('num_error_points')
                self.Output.appendDictValue('error_points', point)
            elif value < self.getWarningMin() or value > self.getWarningMax():
                point = (self.RootObject.GetBinCenter(bin), value)
                self.Output.incrementDictValue('num_warning_points')
                self.Output.appendDictValue('warning_points', point)
        if self.Output.getDictValue('num_error_points'):
            self.Output.setValue(self.Output.getDictValue('error_points')[0][1])
        elif self.Output.getDictValue('num_warning_points'):
            self.Output.setValue(self.Output.getDictValue('warning_points')[0][1])
        else:
            bin = self.RootObject.GetXaxis().GetLast()/2
            self.Output.setValue(self.RootObject.GetBinContent(bin))

if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(4, 16, 2, 24)
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('pol0', 1000)
    algorithm = alg__y_values(limits, histogram)
    algorithm.apply()
    print algorithm.Output
