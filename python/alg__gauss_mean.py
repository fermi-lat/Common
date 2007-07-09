
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Make sure the mean of a gaussian fit is within limits.
#
#  @todo Implement support for fitting in a subrange (min and max not
#  used, at the moment).
#
#  Valid parameters:
#  @li <tt>min</tt>: the minimum x value for the fit.
#  @li <tt>max</tt>: the maximum x value for the fit.


class alg__gauss_mean(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = ['min', 'max']

    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)

    def run(self):
        self.adjustXRange()
        gaussian = ROOT.TF1('g', 'gaus')
        self.RootObject.Fit(gaussian, 'QN')
        self.Output.setValue(gaussian.GetParameter(1))
        self.resetXRange()


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(1, 2, 0, 3)
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('gaus', 1000)
    dict = {'min': -2, 'max': 2}
    algorithm = alg__gauss_mean(limits, histogram, dict)
    algorithm.apply()
    print algorithm.Output
