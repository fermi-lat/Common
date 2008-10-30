
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from pGlobals            import MINUS_INFINITY, PLUS_INFINITY


## @brief Average value (on the y-axis) of a 1-dimensional histogram.
#
#  The average calculation is restricted to a subrange, if required.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>min</tt>: the minimum x value for the subrange.
#  <br>
#  @li <tt>max</tt>: the maximum x value for the subrange.
#  <br>
#  @li <tt>exclude</tt>: the (optional) list of bin indexes to be excluded from
#  the average.
#
#  <b>Output value</b>:
#
#  The mean value of the histogram on the y axis.



class alg__y_average(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH1D']
    SUPPORTED_PARAMETERS = ['min', 'max', 'exclude']
    OUTPUT_LABEL         = 'Histogram y mean value'

    def run(self):
        numBins = self.RootObject.GetNbinsX()
        xmin = self.getParameter('min', MINUS_INFINITY)
        xmax = self.getParameter('max', PLUS_INFINITY)
        excludeList = self.getParameter('exclude', [])
        average = 0
        n = 0
        for i in range(1, numBins + 1):
            binCenter = self.RootObject.GetBinCenter(i)
            if binCenter > xmin and binCenter < xmax and i not in excludeList:
                average += self.RootObject.GetBinContent(i)
                n += 1
        try:
            average /= n
        except:
            average = 0
        self.Output.setValue(average)

                

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
    pardict = {'min': -2, 'max': -0.1}
    algorithm = alg__y_average(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output
