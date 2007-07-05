
from pSafeROOT import *

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm




class alg__num_entries(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = ['min', 'max']

    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)

    def run(self):
        self.adjustXRange()
        self.Output.setValue(self.RootObject.GetEntries())
        self.resetXRange()


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(0, 2000, 0, 20000)
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('gaus', 1000)
    algorithm = alg__num_entries(limits, histogram)
    algorithm.apply()
    print algorithm.Output
