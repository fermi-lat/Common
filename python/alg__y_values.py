
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Make sure all the y values are within limits.
#
#  The algorithm loops over the contents of each bins and checks that
#  all the values are within the limits.
#  In case of an error/warning the content of the FIRST bin out of limits
#  is returned.
#  The detailed output dictionary contains the value and the bin center of
#  all the bins the are out of the limits. 
#
#  Valid parameters:
#  @li normalize: if set to True the alarm limits will be multiplied
#  by the number of entries in the histogram.
#  Used to set limits that does not depend on run statistics.

class alg__y_values(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = ['normalize']

    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)

    def run(self):
        self.Output.setDictValue('num_warning_points', 0)
        self.Output.setDictValue('num_error_points'  , 0)
        self.Output.setDictValue('warning_points', [])
        self.Output.setDictValue('error_points'  , [])
        if self.ParamsDict.has_key('normalize') and self.ParamsDict['normalize'] == True:
            nEntries = self.RootObject.GetEntries()
            self.Limits.ErrorMax   *= nEntries
            self.Limits.ErrorMin   *= nEntries
            self.Limits.WarningMin *= nEntries
            self.Limits.WarningMax *= nEntries
        for bin in range(self.RootObject.GetXaxis().GetFirst(),\
                         self.RootObject.GetXaxis().GetLast()+1):
            value = self.RootObject.GetBinContent(bin)
            if value < self.Limits.ErrorMin or value > self.Limits.ErrorMax:
                point = (self.RootObject.GetBinCenter(bin), value)
                self.Output.incrementDictValue('num_error_points')
                self.Output.appendDictValue('error_points', point)
            elif value < self.Limits.WarningMin or value > self.Limits.WarningMax:
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
    print algorithm.Output.DetailedDict
    histogram.Draw()
