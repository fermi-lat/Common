
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm



## @brief Average value (on the x-axis) of a 1-dimensional histogram.
#
#  The average is retrieved trhough the ROOT method TH1::GetMean().
#  The average calculation is restricted to a subrange, if required.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>min</tt>: the minimum x value for the subrange.
#  <br>
#  @li <tt>max</tt>: the maximum x value for the subrange.
#
#  <b>Output value</b>:
#
#  The mean value of the histogram.



class alg__x_average(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH1D']
    SUPPORTED_PARAMETERS = ['min', 'max']
    OUTPUT_LABEL         = 'Histogram mean value'

    def run(self):
        self.adjustXRange()
        self.Output.setValue(self.RootObject.GetMean())
        self.resetXRange()


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-2, 2, -3, 3)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('gaus', 1000)
    histogram.Draw()
    canvas.Update()
    pardict = {'min': 0, 'max': 2}
    algorithm = alg__x_average(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output
