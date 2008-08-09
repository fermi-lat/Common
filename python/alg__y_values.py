
import pUtils

from pSafeROOT           import ROOT
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from pGlobals            import MINUS_INFINITY


## @brief Make sure all the y values are within limits.
#
#  The algorithm loops over the contents of each bins and checks that
#  all the values are within the limits.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>normalize</tt>: if this parameter is set, then all the limits are
#  scaled to (read: multiplied by) the number of entries in the histogram.
#  @li <tt>num_sigma</tt>: multiplicative factor for the error bars.
#
#  <b>Output value</b>:
#
#  The value of the bin/point which is "more" out of the limits.
#
#  <b>Output details</b>:
#
#  @li <tt>num_warning_entries</tt>: number of bins/poins causing a warning.
#  <br>
#  @li <tt>num_error_entries</tt>: number of bins/poins causing an error.
#  <br>
#  @li <tt>warning_entries</tt>: detailed list of bins/poins causing a warning.
#  <br>
#  @li <tt>error_entries</tt>: detailed list of bins/poins causing an error.
#  <br>


class alg__y_values(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TProfile']
    SUPPORTED_PARAMETERS = ['normalize', 'num_sigma']
    OUTPUT_LABEL         = 'The worst y-value'

    def run(self):
        self.NumSigma = self.getParameter('num_sigma', 1.0)
        if self.getParameter('normalize', False):
            numEntries = self.RootObject.GetEntries()
            self.Limits.ErrorMax   *= numEntries
            self.Limits.ErrorMin   *= numEntries
            self.Limits.WarningMin *= numEntries
            self.Limits.WarningMax *= numEntries
        maxBadness = MINUS_INFINITY
        for i in range(self.RootObject.GetXaxis().GetFirst(),\
                         self.RootObject.GetXaxis().GetLast() + 1):
            value = self.RootObject.GetBinContent(i)
            error = self.RootObject.GetBinError(i)*self.NumSigma
            badness = self.checkStatus(i, value, 'y-value', error)
            if badness > maxBadness:
                maxBadness = badness
                outputValue = value
        self.Output.setValue(outputValue, None, maxBadness)
        


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(4, 16, 2, 24)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('pol0', 1000)
    histogram.Draw()
    canvas.Update()
    algorithm = alg__y_values(limits, histogram, {})
    algorithm.apply()
    print algorithm.Output
    histogram.Draw()
