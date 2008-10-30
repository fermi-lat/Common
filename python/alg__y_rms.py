
import math

from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from pGlobals            import MINUS_INFINITY, PLUS_INFINITY


## @brief RMS value (on the y-axis) of a 1-dimensional histogram.
#
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
#  The RMS value of the histogram on the y axis.



class alg__y_rms(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH1D']
    SUPPORTED_PARAMETERS = ['min', 'max']
    OUTPUT_LABEL         = 'Histogram y RMS value'

    def run(self):
        numBins = self.RootObject.GetNbinsX()
        xmin = self.getParameter('min', MINUS_INFINITY)
        xmax = self.getParameter('max', PLUS_INFINITY)
        x = 0
        x2 = 0
        n = 0
        for i in range(1, numBins + 1):
            binCenter = self.RootObject.GetBinCenter(i)
            if binCenter > xmin and binCenter < xmax:
                binContent = self.RootObject.GetBinContent(i)
                x += binContent
                x2 += binContent*binContent
                n += 1
        try:
            x /= n
            x2 /= n
            rms = math.sqrt(x2 - x*x)
        except:
            rms = 0
        self.Output.setValue(rms)

                

if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-2, 2, -3, 3)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('pol0', 10000)
    for i in range(1, 50):
        histogram.SetBinContent(i, 0.5*histogram.GetBinContent(i))
    histogram.Draw()
    canvas.Update()
    pardict = {'min': 0, 'max': 2}
    algorithm = alg__y_rms(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output
