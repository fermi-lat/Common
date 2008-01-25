
from pSafeROOT import ROOT
from math      import sqrt

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm



class alg__empty_bins(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH2F']
    SUPPORTED_PARAMETERS = []
    
    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)

    def __runTH2(self):
        values = [0.0]
        for i in range(1, self.RootObject.GetNbinsX() + 1):
            for j in range(1, self.RootObject.GetNbinsY() + 1):
                if self.RootObject.GetBinContent(i, j) == 0:
                    averageNeighbourContent = self.getNeighbourAverage((i, j))
                    significance = sqrt(averageNeighbourContent)
                    values.append(significance)
                    if significance > self.Limits.ErrorMax:
                        self.Output.incrementDictValue('num_error_bins')
                        self.Output.appendDictValue('error_bins',\
                                                    (i-1, j-1, significance))
                    elif significance > self.Limits.WarningMax:
                        self.Output.incrementDictValue('num_warning_bins')
                        self.Output.appendDictValue('warning_bins',\
                                                    (i-1, j-1, significance))
        self.Output.setValue(max(values))
        
    def run(self):
        self.Output.setDictValue('num_warning_bins', 0)
        self.Output.setDictValue('num_error_bins'  , 0)
        self.Output.setDictValue('warning_bins', [])
        self.Output.setDictValue('error_bins'  , [])
        self.__runTH2()
