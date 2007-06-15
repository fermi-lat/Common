
import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Return position of the center of the last populated bin of
#  the histogram on the x axis minus the center of the first populated bin of
#  the histogram on the x .
#
#  Valid parameters: None.
#
## @param plot
#  The ROOT object.
## @param paramsDict
#  The (optional) dictionary of parameters.

class alg__x_max_minus_min_bin(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = []

    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)

    def run(self):
        lastBin  = -1
        firstBin = -1
        for bin in range(self.RootObject.GetXaxis().GetLast(),\
                         self.RootObject.GetXaxis().GetFirst()-1, -1):
            if self.RootObject.GetBinContent(bin) > 0:
                lastBin = bin
                break
        for bin in range(self.RootObject.GetXaxis().GetFirst(),\
                         self.RootObject.GetXaxis().GetLast()+1):
            if self.RootObject.GetBinContent(bin) > 0:
                firstBin = bin
                break
        if(lastBin == - 1 or firstBin == - 1):
            delta = -1
        else:
            delta = self.RootObject.GetBinCenter(lastBin) -\
                    self.RootObject.GetBinCenter(firstBin)
        self.Output.setValue(delta)


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-4, 4, -5, 5)
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('gaus', 1000)
    algorithm = alg__x_max_minus_min_bin(limits, histogram)
    algorithm.apply()
    print algorithm.Output
