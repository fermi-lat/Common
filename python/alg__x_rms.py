
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm



## @brief RMS (on the x-axis) of a 1-dimensional histogram.
#
#  The RMS is retrieved trhough the ROOT method TH1::GetRMS().
#  The RMS calculation is restricted to a subrange, if required.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>min</tt>: the minimum x value for the subrange.
#  <br>
#  @li <tt>max</tt>: the maximum x value for the subrange.
#
#  <b>Output value</b>:
#
#  The RMS of the histogram.



class alg__x_rms(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = ['min', 'max']
    OUTPUT_LABEL         = 'Histogram RMS'

    def run(self):
        self.adjustXRange()
        self.Output.setValue(self.RootObject.GetRMS())
        self.resetXRange()


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(1, 2, 0, 3)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('gaus', 1000)
    histogram.Draw()
    canvas.Update()
    pardict = {'min': -2, 'max': 2}
    algorithm = alg__x_rms(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % pardict
    print algorithm.Output
