
import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Return the number of entries in the overflow bin
#
#  Valid parameters: None.
#
## @param plot
#  The ROOT object.
## @param paramsDict
#  The (optional) dictionary of parameters.

class alg__x_overflow(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = []

    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)

    def run(self):
        lastBin = self.RootObject.GetNbinsX() + 1
        self.Output.setValue(self.RootObject.GetBinContent(lastBin))


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-2, 2, -3, 3)
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('gaus', 1000)
    algorithm = alg__x_overflow(limits, histogram)
    algorithm.apply()
    print algorithm.Output
