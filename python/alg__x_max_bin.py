
from pSafeROOT import *

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Return position of the center of the last populated bin of
#  the histogram on the x axis.
#
#  Valid parameters: None.
#
## @param plot
#  The ROOT object.
## @param paramsDict
#  The (optional) dictionary of parameters.

class alg__x_max_bin(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = []

    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)

    def run(self):
        for bin in range(self.RootObject.GetXaxis().GetLast(),\
                         self.RootObject.GetXaxis().GetFirst()-1, -1):
            if self.RootObject.GetBinContent(bin) > 0:
                self.Output.setValue(self.RootObject.GetBinCenter(bin))
                return None


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-4, 4, -5, 5)
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('gaus', 1000)
    algorithm = alg__x_max_bin(limits, histogram)
    algorithm.apply()
    print algorithm.Output
