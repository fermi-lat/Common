
import pUtils

from pSafeROOT           import ROOT
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from pAlarmOutput        import STATUS_CLEAN, STATUS_WARNING, STATUS_ERROR


## @brief Make sure all the y values are within limits.
#
#  The algorithm loops over the contents of each bins and checks that
#  all the values are within the limits.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>normalize</tt>: if this parameter is set, then all the limits are
#  scaled to (read: multiplied by) the number of entries in the histogram.
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
    SUPPORTED_PARAMETERS = ['normalize']
    OUTPUT_DICTIONARY    = {'num_warning_entries': 0,
                            'num_error_entries'  : 0,
                            'warning_entries'    : [],
                            'error_entries'      : []
                            }
    OUTPUT_LABEL         = 'The worst y-value'

    def run(self):
        if self.getParameter('normalize', False):
            numEntries = self.RootObject.GetEntries()
            self.Limits.ErrorMax   *= numEntries
            self.Limits.ErrorMin   *= numEntries
            self.Limits.WarningMin *= numEntries
            self.Limits.WarningMax *= numEntries
        badnessDict = {}
        for i in range(self.RootObject.GetXaxis().GetFirst(),\
                         self.RootObject.GetXaxis().GetLast() + 1):
            value = self.RootObject.GetBinContent(i)
            status = self.getStatus(value)
            badnessDict[self.getBadness(value)] = value
            self.checkStatus(i, value, 'y-value')
        badnessList = badnessDict.keys()
        badnessList.sort()
        maxBadness = badnessList[-1]
        self.Output.setValue(badnessDict[maxBadness])
        


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
