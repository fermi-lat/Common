
from pSafeROOT import *

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Return the RMS on the x axis.
#
#  The average value is retrieved through the ROOT TH1::GetRMS() method.
#  In case the <tt>min</tt> or <tt>max</tt> parameters are specified,
#  the range is properly set, first. At the end the range is reset anyway.
#
#  Valid parameters:
#  @li <tt>min</tt>: the minimum x value for the rms calculation.
#  @li <tt>max</tt>: the maximum x value for the rms calculation.
#
## @param plot
#  The ROOT object.
## @param paramsDict
#  The (optional) dictionary of parameters.

class alg__x_rms(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = ['min', 'max']

    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)

    def run(self):
        self.adjustXRange()
        self.Output.setValue(self.RootObject.GetRMS())
        self.resetXRange()


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(1, 2, 0, 3)
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('gaus', 1000)
    dict = {'min': -2, 'max': 2}
    algorithm = alg__x_rms(limits, histogram, dict)
    algorithm.apply()
    print algorithm.Output
