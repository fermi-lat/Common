
import pUtils

from pSafeROOT           import ROOT
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm



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
#  @li <tt>num_warning_bins</tt>: number of bins/poins causing a warning.
#  <br>
#  @li <tt>num_error_bins</tt>: number of bins/poins causing an error.
#  <br>
#  @li <tt>warning_bins</tt>: detailed list of bins/poins causing a warning.
#  <br>
#  @li <tt>error_bins</tt>: detailed list of bins/poins causing an error.
#  <br>


class alg__y_values(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TProfile']
    SUPPORTED_PARAMETERS = ['normalize']
    OUTPUT_DICTIONARY    = {'num_warning_points': 0,
                            'num_error_points'  : 0,
                            'warning_points'    : [],
                            'error_points'      : []
                            }
    OUTPUT_LABEL         = 'The most "out of range" y-value'

    def run(self):
        deltaDict = {}
        if self.ParamsDict.has_key('normalize'):
            if self.ParamsDict['normalize'] == True:
                numEntries = self.RootObject.GetEntries()
                self.Limits.ErrorMax   *= numEntries
                self.Limits.ErrorMin   *= numEntries
                self.Limits.WarningMin *= numEntries
                self.Limits.WarningMax *= numEntries
        for bin in range(self.RootObject.GetXaxis().GetFirst(),\
                         self.RootObject.GetXaxis().GetLast()+1):
            value = self.RootObject.GetBinContent(bin)
            x = self.RootObject.GetBinCenter(bin)
            binString = 'bin/point @ %s, value = %s' %\
                (pUtils.formatNumber(x), pUtils.formatNumber(value)) 
            if value < self.Limits.ErrorMin:
                self.Output.incrementDictValue('num_error_points')
                self.Output.appendDictValue('error_points', binString)
                delta = (self.Limits.ErrorMin - value)*10000
            elif value > self.Limits.ErrorMax:
                self.Output.incrementDictValue('num_error_points')
                self.Output.appendDictValue('error_points', binString)
                delta = (value - self.Limits.ErrorMax)*10000
            elif value < self.Limits.WarningMin:
                self.Output.incrementDictValue('num_warning_points')
                self.Output.appendDictValue('warning_points', binString)
                delta = (self.Limits.WarningMin - value)*100
            elif value > self.Limits.WarningMax:
                self.Output.incrementDictValue('num_warning_points')
                self.Output.appendDictValue('warning_points', binString)
                delta = (value - self.Limits.WarningMax)*100
            else:
                delta = max((self.Limits.WarningMax - value),\
                            (value - self.Limits.WarningMin))
            deltaDict[delta] = value
        deltas = deltaDict.keys()
        deltas.sort()
        self.Output.setValue(deltaDict[deltas[-1]])



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
