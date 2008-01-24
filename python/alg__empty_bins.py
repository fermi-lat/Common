
from pSafeROOT import ROOT
from math      import sqrt

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm



class alg__empty_bins(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH2F']
    SUPPORTED_PARAMETERS = []
    
    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)

    def __getAverageNeighbourBinContentTH2(self, binx, biny,\
                                           numNeighbours = 2):
        binContents = []
        for i in range(binx - numNeighbours, binx + numNeighbours):
            for j in range(biny - numNeighbours, biny + numNeighbours):
                if (i, j) != (binx, biny):
                    binContents.append(self.RootObject.GetBinContent(i, j))
        binContents.sort()
        binContents = binContents[numNeighbours:-numNeighbours]
        return sum(binContents)/len(binContents)

    def __runTH2(self):
        values = [0.0]
        xbins = self.RootObject.GetNbinsX()
        ybins = self.RootObject.GetNbinsY()
        for i in range(1, xbins + 1):
            for j in range(1, ybins + 1):
                if self.RootObject.GetBinContent(i, j) == 0:
                    averageNeighbourContent =\
                         self.__getAverageNeighbourBinContentTH2(i, j)
                    value = sqrt(averageNeighbourContent)
                    values.append(value)
                    if value > self.Limits.ErrorMax:
                        self.Output.incrementDictValue('num_error_bins')
                        self.Output.appendDictValue('error_bins',\
                                                    (i - 1, j - 1, value))
                    elif value > self.Limits.WarningMax:
                        self.Output.incrementDictValue('num_warning_bins')
                        self.Output.appendDictValue('warning_bins',\
                                                    (i - 1, j - 1, value))
        self.Output.setValue(max(values))
        
    def run(self):
        self.Output.setDictValue('num_warning_bins', 0)
        self.Output.setDictValue('num_error_bins'  , 0)
        self.Output.setDictValue('warning_bins', [])
        self.Output.setDictValue('error_bins'  , [])
        self.__runTH2()
